from __future__ import annotations

import os
from typing import Any
from copy import deepcopy
from datetime import datetime

from .repository import DataRepository
from .store import SessionStore
from . import platforms as platforms_mod
from . import policies as policies_mod
from . import approvals as approvals_mod
from . import bookings as bookings_mod
from .evaluator import evaluate_session


class TravelPolicyEnvironment:
    def __init__(self, data_root: str | None = None, state_root: str | None = None):
        self.repo = DataRepository(data_root)
        self.store = SessionStore(state_root)
        self._session_id: str | None = None
        self._event_at = datetime.now().isoformat()

    def _action_index(self) -> int:
        if self._session_id:
            session = self.store.get_session(self._session_id)
            if session:
                return len(session.get("actions", []))
        return 0

    def _record(self, action: str, params: dict[str, Any], result: Any):
        if self._session_id:
            self.store.record_action(self._session_id, action, params, result)
        return result

    def _record_unlocked(self, action: str, params: dict[str, Any], result: Any):
        if self._session_id:
            self.store.record_action_unlocked(self._session_id, action, params, result)
        return result

    def bind_session(self, session_id: str):
        self._session_id = session_id

    def set_event_time(self, event_at: str):
        self._event_at = event_at

    def list_scenarios(self) -> list[dict[str, Any]]:
        return self.repo.list_scenario_ids()

    def prepare_rollout(self, session_id: str, scenario_id: str):
        session = self.store.create_session(session_id, scenario_id, self.repo)
        self._session_id = session_id
        return session

    def list_platforms(self) -> list[dict[str, Any]]:
        result = platforms_mod.list_platforms(self.repo)
        return self._record("list_platforms", {}, result)

    def get_platform(self, platform_id: str) -> dict[str, Any]:
        result = platforms_mod.get_platform(self.repo, platform_id)
        return self._record("get_platform", {"platform_id": platform_id}, result)

    def search_flights(
        self,
        platform_id: str,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: str | None = None,
        cabin_class: str = "economy",
        passengers: int = 1,
    ) -> dict[str, Any]:
        result = platforms_mod.search_flights(
            self.repo, platform_id, origin, destination, departure_date,
            return_date, cabin_class, passengers, self._event_at, self._action_index()
        )
        return self._record("search_flights", {
            "platform_id": platform_id, "origin": origin, "destination": destination,
            "departure_date": departure_date, "return_date": return_date,
            "cabin_class": cabin_class, "passengers": passengers,
        }, result)

    def compare_platform_prices(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: str | None = None,
        cabin_class: str = "economy",
        passengers: int = 1,
    ) -> dict[str, Any]:
        result = platforms_mod.compare_platform_prices(
            self.repo, origin, destination, departure_date,
            return_date, cabin_class, passengers, self._event_at, self._action_index()
        )
        return self._record("compare_platform_prices", {
            "origin": origin, "destination": destination,
            "departure_date": departure_date, "return_date": return_date,
            "cabin_class": cabin_class, "passengers": passengers,
        }, result)

    def get_platform_fee_structure(self, platform_id: str) -> dict[str, Any]:
        result = platforms_mod.get_platform_fee_structure(
            self.repo, platform_id, self._event_at, self._action_index()
        )
        return self._record("get_platform_fee_structure", {"platform_id": platform_id}, result)

    def filter_platforms_by_region(self, region: str) -> list[dict[str, Any]]:
        result = platforms_mod.filter_platforms_by_region(
            self.repo, region, self._event_at, self._action_index()
        )
        return self._record("filter_platforms_by_region", {"region": region}, result)

    def get_platform_discounts(self, platform_id: str) -> dict[str, Any]:
        result = platforms_mod.get_platform_discounts(
            self.repo, platform_id, self._event_at, self._action_index()
        )
        return self._record("get_platform_discounts", {"platform_id": platform_id}, result)

    def calculate_total_cost(
        self,
        platform_id: str,
        base_price: float,
        cabin_class: str = "economy",
        baggage_fee: float = 0,
        seat_selection_fee: float = 0,
    ) -> dict[str, Any]:
        result = platforms_mod.calculate_total_cost(
            self.repo, platform_id, base_price, cabin_class,
            baggage_fee, seat_selection_fee, self._event_at, self._action_index()
        )
        return self._record("calculate_total_cost", {
            "platform_id": platform_id, "base_price": base_price,
            "cabin_class": cabin_class, "baggage_fee": baggage_fee,
            "seat_selection_fee": seat_selection_fee,
        }, result)

    def list_policies(self) -> list[dict[str, Any]]:
        result = policies_mod.list_policies(self.repo)
        return self._record("list_policies", {}, result)

    def get_policy(self, policy_id: str) -> dict[str, Any]:
        result = policies_mod.get_policy(self.repo, policy_id)
        return self._record("get_policy", {"policy_id": policy_id}, result)

    def validate_booking_against_policy(
        self,
        policy_id: str,
        estimated_cost: float,
        cabin_class: str,
        advance_booking_days: int,
    ) -> dict[str, Any]:
        result = policies_mod.validate_booking_against_policy(
            self.repo, policy_id, estimated_cost, cabin_class,
            advance_booking_days, self._event_at, self._action_index()
        )
        return self._record("validate_booking_against_policy", {
            "policy_id": policy_id, "estimated_cost": estimated_cost,
            "cabin_class": cabin_class, "advance_booking_days": advance_booking_days,
        }, result)

    def get_policy_approval_chain(
        self,
        policy_id: str,
        estimated_cost: float,
    ) -> dict[str, Any]:
        result = policies_mod.get_policy_approval_chain(
            self.repo, policy_id, estimated_cost, self._event_at, self._action_index()
        )
        return self._record("get_policy_approval_chain", {
            "policy_id": policy_id, "estimated_cost": estimated_cost,
        }, result)

    def check_policy_compliance(
        self,
        policy_id: str,
        booking_details: dict[str, Any],
    ) -> dict[str, Any]:
        result = policies_mod.check_policy_compliance(
            self.repo, policy_id, booking_details, self._event_at, self._action_index()
        )
        return self._record("check_policy_compliance", {
            "policy_id": policy_id, "booking_details": booking_details,
        }, result)

    def get_policy_restrictions(self, policy_id: str) -> dict[str, Any]:
        result = policies_mod.get_policy_restrictions(
            self.repo, policy_id, self._event_at, self._action_index()
        )
        return self._record("get_policy_restrictions", {"policy_id": policy_id}, result)

    def get_policy_travel_limits(self, policy_id: str) -> dict[str, Any]:
        result = policies_mod.get_policy_travel_limits(
            self.repo, policy_id, self._event_at, self._action_index()
        )
        return self._record("get_policy_travel_limits", {"policy_id": policy_id}, result)

    def get_domestic_vs_international_policy(
        self,
        policy_id: str,
        is_international: bool,
    ) -> dict[str, Any]:
        result = policies_mod.get_domestic_vs_international_policy(
            self.repo, policy_id, is_international, self._event_at, self._action_index()
        )
        return self._record("get_domestic_vs_international_policy", {
            "policy_id": policy_id, "is_international": is_international,
        }, result)

    def initiate_approval_request(
        self,
        policy_id: str,
        booking_details: dict[str, Any],
        estimated_cost: float,
        approver_email: str,
        justification: str,
    ) -> dict[str, Any]:
        params = {
            "policy_id": policy_id, "booking_details": booking_details,
            "estimated_cost": estimated_cost, "approver_email": approver_email,
            "justification": justification,
        }
        if self._session_id:
            with self.store.session_lock(self._session_id):
                result = approvals_mod.initiate_approval_request(
                    self.store, self._session_id, policy_id, booking_details,
                    estimated_cost, approver_email, justification,
                    self._event_at, self._action_index()
                )
                return self._record_unlocked("initiate_approval_request", params, result)
        result = approvals_mod.initiate_approval_request(
            self.store, self._session_id, policy_id, booking_details,
            estimated_cost, approver_email, justification,
            self._event_at, self._action_index()
        )
        return self._record("initiate_approval_request", params, result)

    def approve_request(
        self,
        approval_id: str,
        approver_email: str,
        comments: str | None = None,
    ) -> dict[str, Any]:
        params = {
            "approval_id": approval_id, "approver_email": approver_email,
            "comments": comments,
        }
        if self._session_id:
            with self.store.session_lock(self._session_id):
                result = approvals_mod.approve_request(
                    self.store, self._session_id, approval_id, approver_email,
                    comments, self._event_at, self._action_index()
                )
                return self._record_unlocked("approve_request", params, result)
        result = approvals_mod.approve_request(
            self.store, self._session_id, approval_id, approver_email,
            comments, self._event_at, self._action_index()
        )
        return self._record("approve_request", params, result)

    def reject_request(
        self,
        approval_id: str,
        approver_email: str,
        rejection_reason: str,
    ) -> dict[str, Any]:
        params = {
            "approval_id": approval_id, "approver_email": approver_email,
            "rejection_reason": rejection_reason,
        }
        if self._session_id:
            with self.store.session_lock(self._session_id):
                result = approvals_mod.reject_request(
                    self.store, self._session_id, approval_id, approver_email,
                    rejection_reason, self._event_at, self._action_index()
                )
                return self._record_unlocked("reject_request", params, result)
        result = approvals_mod.reject_request(
            self.store, self._session_id, approval_id, approver_email,
            rejection_reason, self._event_at, self._action_index()
        )
        return self._record("reject_request", params, result)

    def check_approval_status(self, approval_id: str) -> dict[str, Any]:
        result = approvals_mod.check_approval_status(
            self.store, self._session_id, approval_id,
            self._event_at, self._action_index()
        )
        return self._record("check_approval_status", {"approval_id": approval_id}, result)

    def list_pending_approvals(self) -> dict[str, Any]:
        result = approvals_mod.list_pending_approvals(
            self.store, self._session_id, self._event_at, self._action_index()
        )
        return self._record("list_pending_approvals", {}, result)

    def escalate_approval(
        self,
        approval_id: str,
        escalation_reason: str,
        new_approver_email: str,
    ) -> dict[str, Any]:
        params = {
            "approval_id": approval_id, "escalation_reason": escalation_reason,
            "new_approver_email": new_approver_email,
        }
        if self._session_id:
            with self.store.session_lock(self._session_id):
                result = approvals_mod.escalate_approval(
                    self.store, self._session_id, approval_id, escalation_reason,
                    new_approver_email, self._event_at, self._action_index()
                )
                return self._record_unlocked("escalate_approval", params, result)
        result = approvals_mod.escalate_approval(
            self.store, self._session_id, approval_id, escalation_reason,
            new_approver_email, self._event_at, self._action_index()
        )
        return self._record("escalate_approval", params, result)

    def bulk_approve_requests(
        self,
        approval_ids: list[str],
        approver_email: str,
        comments: str | None = None,
    ) -> dict[str, Any]:
        params = {
            "approval_ids": approval_ids, "approver_email": approver_email,
            "comments": comments,
        }
        if self._session_id:
            with self.store.session_lock(self._session_id):
                result = approvals_mod.bulk_approve_requests(
                    self.store, self._session_id, approval_ids, approver_email,
                    comments, self._event_at, self._action_index()
                )
                return self._record_unlocked("bulk_approve_requests", params, result)
        result = approvals_mod.bulk_approve_requests(
            self.store, self._session_id, approval_ids, approver_email,
            comments, self._event_at, self._action_index()
        )
        return self._record("bulk_approve_requests", params, result)

    def get_approval_history(self) -> dict[str, Any]:
        result = approvals_mod.get_approval_history(
            self.store, self._session_id, self._event_at, self._action_index()
        )
        return self._record("get_approval_history", {}, result)

    def create_booking(
        self,
        platform_id: str,
        platform_name: str,
        flight_details: dict[str, Any],
        total_cost: float,
        approval_id: str | None = None,
        booking_ref: str | None = None,
    ) -> dict[str, Any]:
        params = {
            "platform_id": platform_id, "platform_name": platform_name,
            "flight_details": flight_details, "total_cost": total_cost,
            "approval_id": approval_id, "booking_ref": booking_ref,
        }
        if self._session_id:
            with self.store.session_lock(self._session_id):
                result = bookings_mod.create_booking(
                    self.store, self._session_id, platform_id, platform_name,
                    flight_details, total_cost, approval_id, booking_ref,
                    self._event_at, self._action_index()
                )
                return self._record_unlocked("create_booking", params, result)
        result = bookings_mod.create_booking(
            self.store, self._session_id, platform_id, platform_name,
            flight_details, total_cost, approval_id, booking_ref,
            self._event_at, self._action_index()
        )
        return self._record("create_booking", params, result)

    def cancel_booking(self, booking_ref: str, cancellation_reason: str) -> dict[str, Any]:
        params = {
            "booking_ref": booking_ref, "cancellation_reason": cancellation_reason,
        }
        if self._session_id:
            with self.store.session_lock(self._session_id):
                result = bookings_mod.cancel_booking(
                    self.store, self._session_id, booking_ref, cancellation_reason,
                    self._event_at, self._action_index()
                )
                return self._record_unlocked("cancel_booking", params, result)
        result = bookings_mod.cancel_booking(
            self.store, self._session_id, booking_ref, cancellation_reason,
            self._event_at, self._action_index()
        )
        return self._record("cancel_booking", params, result)

    def get_booking_details(self, booking_ref: str) -> dict[str, Any]:
        result = bookings_mod.get_booking_details(
            self.store, self._session_id, booking_ref,
            self._event_at, self._action_index()
        )
        return self._record("get_booking_details", {"booking_ref": booking_ref}, result)

    def list_bookings(self, status_filter: str | None = None) -> dict[str, Any]:
        result = bookings_mod.list_bookings(
            self.store, self._session_id, status_filter,
            self._event_at, self._action_index()
        )
        return self._record("list_bookings", {"status_filter": status_filter}, result)

    def update_booking(self, booking_ref: str, update_fields: dict[str, Any]) -> dict[str, Any]:
        params = {
            "booking_ref": booking_ref, "update_fields": update_fields,
        }
        if self._session_id:
            with self.store.session_lock(self._session_id):
                result = bookings_mod.update_booking(
                    self.store, self._session_id, booking_ref, update_fields,
                    self._event_at, self._action_index()
                )
                return self._record_unlocked("update_booking", params, result)
        result = bookings_mod.update_booking(
            self.store, self._session_id, booking_ref, update_fields,
            self._event_at, self._action_index()
        )
        return self._record("update_booking", params, result)

    def get_booking_itinerary(self, booking_ref: str) -> dict[str, Any]:
        result = bookings_mod.get_booking_itinerary(
            self.store, self._session_id, booking_ref,
            self._event_at, self._action_index()
        )
        return self._record("get_booking_itinerary", {"booking_ref": booking_ref}, result)

    def confirm_booking_received(self, booking_ref: str) -> dict[str, Any]:
        params = {"booking_ref": booking_ref}
        if self._session_id:
            with self.store.session_lock(self._session_id):
                result = bookings_mod.confirm_booking_received(
                    self.store, self._session_id, booking_ref,
                    self._event_at, self._action_index()
                )
                return self._record_unlocked("confirm_booking_received", params, result)
        result = bookings_mod.confirm_booking_received(
            self.store, self._session_id, booking_ref,
            self._event_at, self._action_index()
        )
        return self._record("confirm_booking_received", params, result)

    def get_booking_statistics(self) -> dict[str, Any]:
        result = bookings_mod.get_booking_statistics(
            self.store, self._session_id, self._event_at, self._action_index()
        )
        return self._record("get_booking_statistics", {}, result)

    def session_summary(self, session_id: str | None = None) -> dict[str, Any]:
        if session_id is not None:
            self._session_id = session_id
        session = self.store.get_session(self._session_id)
        if not session:
            return {"success": False, "error": "Session not found"}
        evaluation = evaluate_session(self.store, self._session_id)
        return {
            "success": True,
            "session_id": self._session_id,
            "scenario_id": session.get("scenario_id"),
            "created_at": session.get("created_at"),
            "total_actions": len(session.get("actions", [])),
            "action_count": len(session.get("actions", [])),
            "total_approvals": len(session.get("approvals", [])),
            "total_bookings": len(session.get("bookings", [])),
            "evaluation": evaluation,
        }

    def evaluate_session(self, session_id: str | None = None) -> dict[str, Any]:
        if session_id is not None:
            self._session_id = session_id
        return evaluate_session(self.store, self._session_id)

    def reset_rollout(self):
        if self._session_id:
            self.store.reset_session(self._session_id, self.repo)
        return {"success": True, "message": "Session reset"}
