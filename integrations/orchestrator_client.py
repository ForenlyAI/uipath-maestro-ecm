"""Minimal UiPath Orchestrator (Cloud) client — the live task-node bridge.

Turns the local pipeline into something that runs against a real Orchestrator tenant:
the analyst's triage is pushed as Queue items, which a Maestro/Studio process then
dequeues and routes (HITL via Action Center vs autonomous Fast Track).

Config is read from the environment — no secrets in the repo:

    UIPATH_ORG            organization slug (the URL segment after cloud.uipath.com/)
    UIPATH_TENANT         tenant name (e.g. DefaultTenant)
    UIPATH_CLIENT_ID      Confidential external app — App ID
    UIPATH_CLIENT_SECRET  Confidential external app — App Secret
    UIPATH_FOLDER_ID      Orchestrator folder (modern folder) id, e.g. the Shared folder

The external app needs Application scopes: OR.Folders, OR.Queues, OR.Assets, OR.Tasks, OR.Jobs.

Note: UiPath's edge (Cloudflare) blocks requests without a browser-like User-Agent
(HTTP error 1010), so every call sets one explicitly.
"""
import json
import os
import urllib.error
import urllib.parse
import urllib.request

CLOUD = "https://cloud.uipath.com"
UA = "Mozilla/5.0 (uipath-maestro-ecm)"
SCOPES = "OR.Folders OR.Queues OR.Assets OR.Tasks OR.Jobs"


class Orchestrator:
    def __init__(self):
        self.org = os.environ["UIPATH_ORG"]
        self.tenant = os.environ["UIPATH_TENANT"]
        self.folder = os.environ["UIPATH_FOLDER_ID"]
        self._cid = os.environ["UIPATH_CLIENT_ID"]
        self._secret = os.environ["UIPATH_CLIENT_SECRET"]
        self.base = f"{CLOUD}/{self.org}/{self.tenant}/orchestrator_"
        self._token = None

    def _request(self, url, data=None, headers=None, method="GET"):
        body = json.dumps(data).encode() if data is not None else None
        h = {"User-Agent": UA, **(headers or {})}
        if body is not None:
            h["Content-Type"] = "application/json"
        req = urllib.request.Request(url, data=body, headers=h, method=method)
        try:
            with urllib.request.urlopen(req) as resp:
                raw = resp.read().decode()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            raise RuntimeError(f"{method} {url} -> {e.code}: {e.read().decode()[:300]}") from None

    def token(self):
        if self._token:
            return self._token
        data = urllib.parse.urlencode({
            "grant_type": "client_credentials", "client_id": self._cid,
            "client_secret": self._secret, "scope": SCOPES,
        }).encode()
        req = urllib.request.Request(
            f"{CLOUD}/identity_/connect/token", data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": UA},
        )
        with urllib.request.urlopen(req) as resp:
            self._token = json.loads(resp.read())["access_token"]
        return self._token

    def _auth_headers(self):
        return {"Authorization": f"Bearer {self.token()}",
                "X-UIPATH-OrganizationUnitId": str(self.folder)}

    # --- folders / queues -------------------------------------------------
    def list_folders(self):
        return self._request(f"{self.base}/odata/Folders", headers=self._auth_headers())["value"]

    def ensure_queue(self, name, description="", unique_reference=True):
        """Create the queue if it doesn't exist; return its definition."""
        query = urllib.parse.urlencode({"$filter": f"Name eq '{name}'"})
        existing = self._request(
            f"{self.base}/odata/QueueDefinitions?{query}",
            headers=self._auth_headers(),
        )["value"]
        if existing:
            return existing[0]
        return self._request(
            f"{self.base}/odata/QueueDefinitions",
            data={"Name": name, "Description": description,
                  "MaxNumberOfRetries": 1, "AcceptAutomaticallyRetry": False,
                  "EnforceUniqueReference": unique_reference},
            headers=self._auth_headers(), method="POST",
        )

    def add_queue_item(self, queue_name, reference, content, priority="Normal"):
        return self._request(
            f"{self.base}/odata/Queues/UiPathODataSvc.AddQueueItem",
            data={"itemData": {"Name": queue_name, "Priority": priority,
                               "Reference": reference, "SpecificContent": content}},
            headers=self._auth_headers(), method="POST",
        )

    def list_queue_items(self, queue_definition_id, top=50):
        query = urllib.parse.urlencode({
            "$filter": f"QueueDefinitionId eq {queue_definition_id}",
            "$select": "Id,Reference,Status,Priority", "$orderby": "Id", "$top": top,
        })
        return self._request(f"{self.base}/odata/QueueItems?{query}",
                             headers=self._auth_headers())["value"]

    def get_next_item(self, queue_name):
        """Pop the next New item from *queue_name* as a transaction (StartTransaction).

        Returns the queue-item dict (including ``Id`` and ``SpecificContent``) if a
        New item is available, or ``None`` when the queue is empty.

        The item transitions from New → InProgress in Orchestrator so no other
        robot/process picks it up concurrently.
        """
        result = self._request(
            f"{self.base}/odata/Queues/UiPathODataSvc.StartTransaction",
            data={"transactionData": {"Name": queue_name}},
            headers=self._auth_headers(),
            method="POST",
        )
        # Orchestrator returns {"value": null} when the queue is empty.
        value = result.get("value")
        return value if value else None

    def set_transaction_status(self, item_id, status, reason=""):
        """Update a queue item that is InProgress (SetTransactionResult).

        Args:
            item_id: The ``Id`` returned by ``get_next_item``.
            status:  ``"Successful"`` or ``"Failed"`` (Orchestrator vocabulary).
            reason:  Free-text output / error message stored on the item.

        Raises:
            RuntimeError: if Orchestrator returns an HTTP error.
        """
        if status not in ("Successful", "Failed"):
            raise ValueError(f"status must be 'Successful' or 'Failed', got {status!r}")

        payload = {
            "transactionResult": {
                "IsSuccessful": status == "Successful",
                "ProcessingException": None if status == "Successful" else {
                    "Reason": reason,
                    "Type": "ApplicationException",
                },
                "Output": {"reason": reason} if status == "Successful" else None,
            }
        }
        self._request(
            f"{self.base}/odata/Queues({item_id})/UiPathODataSvc.SetTransactionResult",
            data=payload,
            headers=self._auth_headers(),
            method="POST",
        )
