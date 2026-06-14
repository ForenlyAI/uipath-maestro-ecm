#!/usr/bin/env python3
"""Queue consumer: process IncidentReports items + set transaction status.

Extends ``integrations/orchestrator_client.py`` with a runnable consumer that:

1. Calls ``get_next_item(queue_name)`` (StartTransaction) to atomically pop a
   New queue item from UiPath Orchestrator.
2. Extracts the ``SpecificContent`` field (the canonical IncidentReport payload).
3. Runs the Fleet AI Analyst (``agents.analyst_agent.analyze``) on the incident.
4. Marks the item ``Successful`` with the disposition as output, or ``Failed``
   with the error reason if anything goes wrong.

The loop runs until the queue is empty or ``--max-items`` is reached.

Usage:
    python -m integrations.consume_incidents                    # defaults
    python -m integrations.consume_incidents --queue IncidentReports --max-items 20

Required environment variables (see orchestrator_client.py):
    UIPATH_ORG, UIPATH_TENANT, UIPATH_CLIENT_ID,
    UIPATH_CLIENT_SECRET, UIPATH_FOLDER_ID

Optional:
    ANTHROPIC_API_KEY   — use Claude as the analyst LLM
    GEMINI_API_KEY      — use Gemini as the fallback analyst LLM
    (if neither is set, deterministic offline rules are used)
"""

import argparse
import json
import os
import sys

# Allow running as `python integrations/consume_incidents.py` from the repo root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.analyst_agent import analyze
from integrations.orchestrator_client import Orchestrator

DEFAULT_QUEUE = "IncidentReports"
DEFAULT_MAX_ITEMS = 50


def _process_item(item):
    """Extract, analyse, and return (disposition, provider_label).

    The IncidentReport is stored in ``item["SpecificContent"]``. Orchestrator
    may return it already parsed (dict) or as a serialised JSON string.
    """
    content = item.get("SpecificContent") or item.get("specificContent") or {}
    if isinstance(content, str):
        content = json.loads(content)

    incident_id = (
        content.get("incidentId")
        or item.get("Reference")
        or str(item.get("Id", "UNKNOWN"))
    )
    print(f"  processing item Id={item['Id']}  incidentId={incident_id}")
    content.setdefault("incidentId", incident_id)

    disposition, provider = analyze(content)
    return disposition, provider


def run(queue_name=DEFAULT_QUEUE, max_items=DEFAULT_MAX_ITEMS):
    """Pull items from *queue_name* and process them until empty or *max_items* reached.

    Returns a list of result dicts for the caller / tests.
    """
    orch = Orchestrator()
    results = []
    processed = 0

    print(f"\n[consume_incidents] starting — queue={queue_name}  max_items={max_items}")

    while processed < max_items:
        item = orch.get_next_item(queue_name)
        if item is None:
            print("[consume_incidents] queue is empty — done.")
            break

        item_id = item["Id"]
        try:
            disposition, provider = _process_item(item)

            summary = (
                f"category={disposition['category']} "
                f"riskScore={disposition['riskScore']} "
                f"hitlRequired={disposition['hitlRequired']} "
                f"suggestedAction={disposition['suggestedAction']} "
                f"provider={provider}"
            )
            orch.set_transaction_status(item_id, "Successful", reason=summary)
            print(f"  -> Successful  {summary}")

            results.append({"itemId": item_id, "status": "Successful", **disposition})

        except Exception as exc:  # noqa: BLE001 — mark Failed, keep consuming
            reason = f"{type(exc).__name__}: {exc}"
            print(f"  -> Failed  {reason}")
            try:
                orch.set_transaction_status(item_id, "Failed", reason=reason)
            except Exception as mark_exc:
                print(f"  [warn] could not mark item {item_id} as Failed: {mark_exc}")
            results.append({"itemId": item_id, "status": "Failed", "error": reason})

        processed += 1

    print(
        f"\n[consume_incidents] finished — "
        f"processed={processed} "
        f"successful={sum(1 for r in results if r['status'] == 'Successful')} "
        f"failed={sum(1 for r in results if r['status'] == 'Failed')}"
    )
    return results


def main():
    parser = argparse.ArgumentParser(
        description="Consume IncidentReport queue items from UiPath Orchestrator."
    )
    parser.add_argument(
        "--queue", default=DEFAULT_QUEUE,
        help=f"Orchestrator queue name (default: {DEFAULT_QUEUE})"
    )
    parser.add_argument(
        "--max-items", type=int, default=DEFAULT_MAX_ITEMS,
        help=f"Stop after this many items (default: {DEFAULT_MAX_ITEMS})"
    )
    args = parser.parse_args()
    run(queue_name=args.queue, max_items=args.max_items)


if __name__ == "__main__":
    main()
