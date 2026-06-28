# UiPath Orchestrator — live setup

How to point the pipeline at a real UiPath Automation Cloud tenant. The local runner
(`python run_pipeline.py`) needs none of this; this is for the live integration.

## 1. Create a Confidential external app

In **Admin → External Applications → Add application**:

- **Type:** Confidential application
- **Resource:** UiPath.Orchestrator (Orchestrator API Access)
- **Application scope(s):** `OR.Folders`, `OR.Queues`, `OR.Assets`, `OR.Tasks`, `OR.Jobs`
  - ⚠️ must be **Application** scopes, not User scopes — `client_credentials` only works with Application scopes (otherwise the token endpoint returns `unauthorized_client`).
- Leave the redirect URL empty.

Save and copy the **App ID** and **App Secret** (the secret is shown once).

## 2. Find your org slug + folder id

- **Org slug:** the URL segment — `cloud.uipath.com/<ORG>/<TENANT>/...`
- **Folder id:** `GET /<ORG>/<TENANT>/orchestrator_/odata/Folders` returns the modern
  folders; use the `Id` of the one you want (e.g. the default **Shared** folder).

## 3. Set the environment

```bash
export UIPATH_ORG=<org-slug>
export UIPATH_TENANT=DefaultTenant
export UIPATH_FOLDER_ID=<folder-id>
export UIPATH_CLIENT_ID=<app-id>
export UIPATH_CLIENT_SECRET=<app-secret>
```

## 4. Push anomalies into the live queue

```bash
python integrations/push_incidents.py
```

This creates the `IncidentReports` queue (if missing) and enqueues each sample
training-run anomaly with its analyst triage as `SpecificContent`. Check
**Orchestrator → Queues → IncidentReports** in the cloud UI.

## Gotchas

- **Cloudflare HTTP 1010:** the UiPath edge blocks requests without a browser-like
  `User-Agent`. `orchestrator_client.py` sets one on every call — keep it if you write
  your own calls.
- **Action Center tasks** can't be created with a bare `GenericTasks/CreateTask`; they
  require a registered action type (External / QuickForm / Document) — model the HITL
  action in the Maestro/Studio process (see issues for the orchestration task).
