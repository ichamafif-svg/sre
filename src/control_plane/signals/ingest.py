from __future__ import annotations

from control_plane.domain import IncidentClass, Signal, SignalKind, WorkItem
from control_plane.workitems.lifecycle import transition
from control_plane.domain import WorkItemState


def human_prompt(summary: str, payload: dict | None = None) -> Signal:
    return Signal(kind=SignalKind.HUMAN_PROMPT, summary=summary, payload=payload or {}, source="human")


def alert(summary: str, payload: dict) -> Signal:
    return Signal(kind=SignalKind.ALERT, summary=summary, payload=payload, source="alertmanager")


def normalize(signal: Signal) -> WorkItem:
    item = WorkItem(signal=signal, summary=signal.summary)
    transition(item, WorkItemState.NORMALIZED, "signal normalized")
    return item


def classify_incident(item: WorkItem) -> IncidentClass:
    payload = item.signal.payload
    service = str(payload.get("service", "")).lower()
    reason = str(payload.get("reason", "")).lower()
    if "security" in reason:
        return IncidentClass.SECURITY
    if "credential" in reason:
        return IncidentClass.CREDENTIAL
    if "provider" in reason:
        return IncidentClass.EXTERNAL_PROVIDER
    if "config" in reason:
        return IncidentClass.CONFIGURATION
    if service == "fixture-parser" or "parser" in reason:
        return IncidentClass.OUR_CODE
    return IncidentClass.UNKNOWN

