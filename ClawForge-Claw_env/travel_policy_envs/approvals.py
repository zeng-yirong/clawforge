from __future__ import annotations

from typing import Any
from datetime import datetime


def initiate_approval_request(
    store,
    session_id: str,
    policy_id: str,
    booking_details: dict[str, Any],
    estimated_cost: float,
    approver_email: str,
    justification: str,
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    approval_id = f"apr_{session_id}_{action_index}"
    approval = {
        "approval_id": approval_id,
        "policy_id": policy_id,
        "booking_details": booking_details,
        "estimated_cost": estimated_cost,
        "approver_email": approver_email,
        "justification": justification,
        "status": "pending",
        "created_at": event_at,
        "action_index": action_index,
    }
    session = store.get_session(session_id)
    if session:
        session["approvals"].append(approval)
        store._save_session(session_id, session)
    return {
        "success": True,
        "approval_id": approval_id,
        "status": "pending",
        "approver_email": approver_email,
        "message": f"Approval request {approval_id} submitted to {approver_email}",
    }


def approve_request(
    store,
    session_id: str,
    approval_id: str,
    approver_email: str,
    comments: str | None = None,
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    session = store.get_session(session_id)
    if not session:
        return {"success": False, "error": "Session not found"}
    approval = None
    for a in session.get("approvals", []):
        if a["approval_id"] == approval_id:
            approval = a
            break
    if not approval:
        return {"success": False, "error": f"Approval {approval_id} not found"}
    if approval["approver_email"] != approver_email:
        return {"success": False, "error": "Unauthorized approver"}
    approval["status"] = "approved"
    approval["approved_at"] = event_at
    approval["approver_comments"] = comments
    store._save_session(session_id, session)
    return {
        "success": True,
        "approval_id": approval_id,
        "status": "approved",
        "message": f"Approval {approval_id} granted",
    }


def reject_request(
    store,
    session_id: str,
    approval_id: str,
    approver_email: str,
    rejection_reason: str,
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    session = store.get_session(session_id)
    if not session:
        return {"success": False, "error": "Session not found"}
    approval = None
    for a in session.get("approvals", []):
        if a["approval_id"] == approval_id:
            approval = a
            break
    if not approval:
        return {"success": False, "error": f"Approval {approval_id} not found"}
    if approval["approver_email"] != approver_email:
        return {"success": False, "error": "Unauthorized approver"}
    approval["status"] = "rejected"
    approval["rejected_at"] = event_at
    approval["rejection_reason"] = rejection_reason
    store._save_session(session_id, session)
    return {
        "success": True,
        "approval_id": approval_id,
        "status": "rejected",
        "message": f"Approval {approval_id} rejected: {rejection_reason}",
    }


def check_approval_status(
    store,
    session_id: str,
    approval_id: str,
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    session = store.get_session(session_id)
    if not session:
        return {"success": False, "error": "Session not found"}
    for a in session.get("approvals", []):
        if a["approval_id"] == approval_id:
            return {
                "success": True,
                "approval_id": approval_id,
                "status": a["status"],
                "created_at": a.get("created_at"),
                "approved_at": a.get("approved_at"),
                "rejected_at": a.get("rejected_at"),
            }
    return {"success": False, "error": f"Approval {approval_id} not found"}


def list_pending_approvals(
    store,
    session_id: str,
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    session = store.get_session(session_id)
    if not session:
        return {"success": False, "error": "Session not found"}
    pending = [a for a in session.get("approvals", []) if a["status"] == "pending"]
    return {
        "success": True,
        "pending_count": len(pending),
        "pending_approvals": pending,
    }


def escalate_approval(
    store,
    session_id: str,
    approval_id: str,
    escalation_reason: str,
    new_approver_email: str,
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    session = store.get_session(session_id)
    if not session:
        return {"success": False, "error": "Session not found"}
    for a in session.get("approvals", []):
        if a["approval_id"] == approval_id:
            a["status"] = "escalated"
            a["escalated_at"] = event_at
            a["escalation_reason"] = escalation_reason
            a["original_approver"] = a["approver_email"]
            a["approver_email"] = new_approver_email
            a["escalated_to"] = new_approver_email
            store._save_session(session_id, session)
            return {
                "success": True,
                "approval_id": approval_id,
                "status": "escalated",
                "new_approver": new_approver_email,
                "message": f"Approval escalated to {new_approver_email}",
            }
    return {"success": False, "error": f"Approval {approval_id} not found"}


def bulk_approve_requests(
    store,
    session_id: str,
    approval_ids: list[str],
    approver_email: str,
    comments: str | None = None,
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    session = store.get_session(session_id)
    if not session:
        return {"success": False, "error": "Session not found"}
    approved = []
    skipped = []
    for approval_id in approval_ids:
        for a in session.get("approvals", []):
            if a["approval_id"] == approval_id:
                if a["approver_email"] != approver_email:
                    skipped.append(approval_id)
                elif a["status"] != "pending":
                    skipped.append(approval_id)
                else:
                    a["status"] = "approved"
                    a["approved_at"] = event_at
                    a["approver_comments"] = comments
                    approved.append(approval_id)
                break
    store._save_session(session_id, session)
    return {
        "success": True,
        "approved_count": len(approved),
        "approved_ids": approved,
        "skipped_count": len(skipped),
        "skipped_ids": skipped,
    }


def get_approval_history(
    store,
    session_id: str,
    event_at: str = "",
    action_index: int = 0,
) -> dict[str, Any]:
    session = store.get_session(session_id)
    if not session:
        return {"success": False, "error": "Session not found"}
    return {
        "success": True,
        "total_approvals": len(session.get("approvals", [])),
        "pending": len([a for a in session.get("approvals", []) if a["status"] == "pending"]),
        "approved": len([a for a in session.get("approvals", []) if a["status"] == "approved"]),
        "rejected": len([a for a in session.get("approvals", []) if a["status"] == "rejected"]),
        "escalated": len([a for a in session.get("approvals", []) if a["status"] == "escalated"]),
        "history": session.get("approvals", []),
    }
