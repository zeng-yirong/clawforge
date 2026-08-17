from __future__ import annotations

from copy import deepcopy
from typing import Any


def save_evidence(
    session: dict[str, Any],
    evidence_type: str,
    description: str,
    source: str,
    metadata: dict[str, Any] | None = None,
    action_index: int | None = None,
) -> dict[str, Any]:
    evidence_list = session.setdefault("evidence", [])

    evidence_id = f"ev_{len(evidence_list) + 1:04d}"
    timestamp = session.get("meta", {}).get("current_time")

    evidence = {
        "evidence_id": evidence_id,
        "evidence_type": evidence_type,
        "description": description,
        "source": source,
        "metadata": metadata or {},
        "saved_at": timestamp,
        "action_index": action_index,
        "integrity_verified": True,
    }

    evidence_list.append(evidence)
    session.setdefault("evidence_index", {})[evidence_id] = evidence

    action = {
        "action": "save_evidence",
        "evidence_id": evidence_id,
        "evidence_type": evidence_type,
        "action_index": action_index,
        "timestamp": timestamp,
    }
    session.setdefault("actions", []).append(action)

    return deepcopy(evidence)


def get_evidence(session: dict[str, Any], evidence_id: str) -> dict[str, Any]:
    evidence_list = session.get("evidence", [])
    for ev in evidence_list:
        if ev.get("evidence_id") == evidence_id:
            return deepcopy(ev)
    return {"error": f"Evidence {evidence_id} not found"}


def list_evidence(
    session: dict[str, Any],
    query: str = "",
    evidence_type: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    evidence_list = session.get("evidence", [])
    results = []

    for ev in evidence_list:
        if query:
            if query.lower() not in ev.get("description", "").lower() and query.lower() not in ev.get("source", "").lower():
                continue

        if evidence_type and ev.get("evidence_type") != evidence_type:
            continue

        results.append(deepcopy(ev))

    results.sort(key=lambda x: x.get("saved_at", ""), reverse=True)

    if limit:
        results = results[:limit]

    return results


def verify_evidence_integrity(
    session: dict[str, Any],
    evidence_id: str,
    action_index: int | None = None,
) -> dict[str, Any]:
    evidence_list = session.get("evidence", [])
    for ev in evidence_list:
        if ev.get("evidence_id") == evidence_id:
            ev["integrity_verified"] = True
            ev["verified_at"] = session.get("meta", {}).get("current_time")

            action = {
                "action": "verify_evidence_integrity",
                "evidence_id": evidence_id,
                "action_index": action_index,
                "timestamp": session.get("meta", {}).get("current_time"),
            }
            session.setdefault("actions", []).append(action)

            return deepcopy(ev)

    return {"error": f"Evidence {evidence_id} not found"}


def capture_camera_snapshot(
    session: dict[str, Any],
    camera_id: str,
    zone_id: str,
    action_index: int | None = None,
) -> dict[str, Any]:
    cameras = session.get("cameras", {})
    if camera_id not in cameras:
        return {"error": f"Camera {camera_id} not found"}

    camera = cameras[camera_id]
    timestamp = session.get("meta", {}).get("current_time")

    evidence = save_evidence(
        session,
        evidence_type="camera_snapshot",
        description=f"Snapshot from {camera.get('name', camera_id)} at {zone_id}",
        source=camera_id,
        metadata={"zone_id": zone_id, "camera_name": camera.get("name")},
        action_index=action_index,
    )

    return evidence


def capture_motion_clip(
    session: dict[str, Any],
    camera_id: str,
    zone_id: str,
    duration_seconds: int,
    action_index: int | None = None,
) -> dict[str, Any]:
    cameras = session.get("cameras", {})
    if camera_id not in cameras:
        return {"error": f"Camera {camera_id} not found"}

    camera = cameras[camera_id]
    timestamp = session.get("meta", {}).get("current_time")

    evidence = save_evidence(
        session,
        evidence_type="motion_clip",
        description=f"Motion clip from {camera.get('name', camera_id)} - {duration_seconds}s",
        source=camera_id,
        metadata={
            "zone_id": zone_id,
            "camera_name": camera.get("name"),
            "duration_seconds": duration_seconds,
        },
        action_index=action_index,
    )

    return evidence


def list_camera_snapshots(
    session: dict[str, Any],
    camera_id: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    evidence_list = session.get("evidence", [])
    results = []

    for ev in evidence_list:
        if ev.get("evidence_type") != "camera_snapshot":
            continue

        if camera_id and ev.get("source") != camera_id:
            continue

        results.append(deepcopy(ev))

    results.sort(key=lambda x: x.get("saved_at", ""), reverse=True)

    if limit:
        results = results[:limit]

    return results
