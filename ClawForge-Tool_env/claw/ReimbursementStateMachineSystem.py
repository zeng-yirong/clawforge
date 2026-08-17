from copy import deepcopy
from datetime import datetime
from typing import Dict, List, Optional, Any

DEFAULT_STATE = {
    "state_machines": [],
    "receipts": {},
    "bank_transactions": {},
    "reimbursement_forms": {},
    "reconciliation_log": [],
    "sm_counter": 1,
    "receipt_counter": 1,
    "transaction_counter": 1,
    "form_counter": 1,
}

VALID_RECEIPT_TYPES = ("taxi", "meal", "hotel", "flight", "other")
VALID_FORM_STATUSES = ("draft", "pending_review", "approved", "rejected", "paid")


class ReimbursementReconciliationEnv:
    """
    A state-machine-based environment for automated reimbursement reconciliation.

    This class models the lifecycle of expense reimbursement processing, from OCR
    receipt recognition through bank transaction matching to automated form filling
    and discrepancy detection. Entities (reimbursement forms) transition through
    states based on validation rules and reconciliation results.

    Attributes:
        state_machines (List[Dict]): Defined state machine templates for reimbursement workflows.
        receipts (Dict[str, Dict]): OCR-recognized receipt records keyed by receipt_id.
        bank_transactions (Dict[str, Dict]): Bank transaction records keyed by transaction_id.
        reimbursement_forms (Dict[str, Dict]): Reimbursement form entities keyed by form_id.
        reconciliation_log (List[Dict]): History of all reconciliation operations.
        sm_counter (int): Auto-incrementing state machine ID counter.
        receipt_counter (int): Auto-incrementing receipt ID counter.
        transaction_counter (int): Auto-incrementing transaction ID counter.
        form_counter (int): Auto-incrementing form ID counter.
    """

    def __init__(self):
        self.state_machines: List[Dict[str, Any]]
        self.receipts: Dict[str, Dict[str, Any]]
        self.bank_transactions: Dict[str, Dict[str, Any]]
        self.reimbursement_forms: Dict[str, Dict[str, Any]]
        self.reconciliation_log: List[Dict[str, Any]]
        self.sm_counter: int
        self.receipt_counter: int
        self.transaction_counter: int
        self.form_counter: int
        self._api_description = (
            "This tool automates reimbursement reconciliation by OCR receipt recognition, "
            "bank transaction matching, and automated form filling with discrepancy detection."
        )

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.state_machines = scenario.get("state_machines", DEFAULT_STATE_COPY["state_machines"])
        self.receipts = scenario.get("receipts", DEFAULT_STATE_COPY["receipts"])
        self.bank_transactions = scenario.get("bank_transactions", DEFAULT_STATE_COPY["bank_transactions"])
        self.reimbursement_forms = scenario.get("reimbursement_forms", DEFAULT_STATE_COPY["reimbursement_forms"])
        self.reconciliation_log = scenario.get("reconciliation_log", DEFAULT_STATE_COPY["reconciliation_log"])
        self.sm_counter = scenario.get("sm_counter", DEFAULT_STATE_COPY["sm_counter"])
        self.receipt_counter = scenario.get("receipt_counter", DEFAULT_STATE_COPY["receipt_counter"])
        self.transaction_counter = scenario.get("transaction_counter", DEFAULT_STATE_COPY["transaction_counter"])
        self.form_counter = scenario.get("form_counter", DEFAULT_STATE_COPY["form_counter"])

    def get_env_state(self) -> dict:
        """
        Return the current internal state of the environment.

        Returns:
            dict: All environment state variables including state machines, receipts,
                bank transactions, reimbursement forms, and reconciliation log.
        """
        return {
            "state_machines": self.state_machines,
            "receipts": self.receipts,
            "bank_transactions": self.bank_transactions,
            "reimbursement_forms": self.reimbursement_forms,
            "reconciliation_log": self.reconciliation_log,
            "sm_counter": self.sm_counter,
            "receipt_counter": self.receipt_counter,
            "transaction_counter": self.transaction_counter,
            "form_counter": self.form_counter,
        }

    # ── State machine definition ─────────────────────────────────────────

    def define_state_machine(
        self,
        name: str,
        initial_state: str,
        terminal_states: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Define a new reimbursement workflow state machine template.

        Args:
            name (str): State machine name (e.g. 'standard_reimbursement', 'urgent_approval').
            initial_state (str): The starting state for all reimbursement forms in this machine.
            terminal_states (List[str]): [Optional] States that mark form completion (e.g. 'paid', 'rejected').

        Returns:
            dict: Contains 'sm_id' (int) and 'state_machine' (Dict) with the created definition.
        """
        if not name.strip():
            return {"error": "State machine name is required."}
        if not initial_state.strip():
            return {"error": "Initial state is required."}

        sm_id = self.sm_counter
        self.sm_counter += 1

        sm = {
            "sm_id": sm_id,
            "name": name,
            "states": [{"name": initial_state, "on_enter": None, "on_exit": None}],
            "transitions": [],
            "initial_state": initial_state,
            "terminal_states": terminal_states or [],
            "form_count": 0,
        }
        self.state_machines.append(sm)
        self._log("sm_defined", {"sm_id": sm_id, "name": name, "initial_state": initial_state})
        return {"sm_id": sm_id, "state_machine": sm}

    def add_state(self, sm_id: int, name: str) -> Dict[str, Any]:
        """
        Add a new state to an existing reimbursement workflow state machine.

        Args:
            sm_id (int): State machine ID.
            name (str): State name (must be unique within this machine).

        Returns:
            dict: Contains 'sm_id' (int) and 'state' (Dict) with the added state entry.
        """
        sm = self._find_sm(sm_id)
        if not sm:
            return {"error": f"State machine ID {sm_id} not found."}
        if any(s["name"] == name for s in sm["states"]):
            return {"error": f"State '{name}' already exists in state machine {sm_id}."}

        state = {"name": name, "on_enter": None, "on_exit": None}
        sm["states"].append(state)
        self._log("state_added", {"sm_id": sm_id, "state": name})
        return {"sm_id": sm_id, "state": state}

    def add_transition(
        self,
        sm_id: int,
        from_state: str,
        to_state: str,
        guard: Optional[Dict[str, Any]] = None,
        trigger: str = "auto",
    ) -> Dict[str, Any]:
        """
        Define a transition between two states in a reimbursement workflow, optionally guarded.

        Args:
            sm_id (int): State machine ID.
            from_state (str): Source state name.
            to_state (str): Target state name.
            guard (Dict): [Optional] Guard condition as {field: {op: value}}.
                e.g. {"discrepancy": {"eq": 0}, "total_amount": {"lte": 5000}}.
            trigger (str): Trigger mode — 'auto' or 'manual'. Defaults to 'auto'.

        Returns:
            dict: Contains 'sm_id' (int) and 'transition' (Dict) with the created transition definition.
        """
        sm = self._find_sm(sm_id)
        if not sm:
            return {"error": f"State machine ID {sm_id} not found."}
        if trigger not in ("auto", "manual"):
            return {"error": f"Invalid trigger '{trigger}'. Must be 'auto' or 'manual'."}

        state_names = {s["name"] for s in sm["states"]}
        if from_state not in state_names:
            return {"error": f"Source state '{from_state}' not found in state machine {sm_id}."}
        if to_state not in state_names:
            return {"error": f"Target state '{to_state}' not found in state machine {sm_id}."}

        transition = {
            "from": from_state,
            "to": to_state,
            "guard": guard or {},
            "trigger": trigger,
        }
        sm["transitions"].append(transition)
        self._log("transition_added", {"sm_id": sm_id, "from": from_state, "to": to_state})
        return {"sm_id": sm_id, "transition": transition}

    # ── Receipt OCR management ───────────────────────────────────────────

    def ocr_receipt(
        self,
        receipt_type: str,
        amount: float,
        date: str,
        vendor: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Simulate OCR recognition of a receipt and store the extracted information.

        Args:
            receipt_type (str): Type of receipt ('taxi', 'meal', 'hotel', 'flight', 'other').
            amount (float): Total amount on the receipt.
            date (str): Date of the expense (e.g. '2024-01-15').
            vendor (str): Vendor or merchant name.
            metadata (Dict): [Optional] Additional OCR-extracted fields (e.g. tax, tip, items).

        Returns:
            dict: Contains 'receipt_id' (str) and 'receipt' (Dict) with the recognized receipt data.
        """
        if receipt_type not in VALID_RECEIPT_TYPES:
            return {"error": f"Invalid receipt type '{receipt_type}'. Must be one of: {', '.join(VALID_RECEIPT_TYPES)}"}
        if amount <= 0:
            return {"error": "Receipt amount must be positive."}
        if not date.strip():
            return {"error": "Receipt date is required."}
        if not vendor.strip():
            return {"error": "Vendor name is required."}

        receipt_id = str(self.receipt_counter)
        self.receipt_counter += 1

        receipt = {
            "receipt_id": receipt_id,
            "receipt_type": receipt_type,
            "amount": amount,
            "date": date,
            "vendor": vendor,
            "metadata": metadata or {},
            "matched_transaction_id": None,
            "status": "unmatched",
        }
        self.receipts[receipt_id] = receipt
        self._log("receipt_ocr", {"receipt_id": receipt_id, "amount": amount, "vendor": vendor})
        return {"receipt_id": receipt_id, "receipt": receipt}

    def get_receipt(self, receipt_id: str) -> Dict[str, Any]:
        """
        Retrieve a receipt by its ID.

        Args:
            receipt_id (str): Receipt ID.

        Returns:
            dict: Contains 'receipt' (Dict) with the full receipt record.
        """
        receipt = self.receipts.get(receipt_id)
        if not receipt:
            return {"error": f"Receipt '{receipt_id}' not found."}
        return {"receipt": receipt}

    def list_receipts(
        self,
        receipt_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List receipts, optionally filtered by type or matching status.

        Args:
            receipt_type (str): [Optional] Filter by receipt type.
            status (str): [Optional] Filter by matching status ('matched', 'unmatched').

        Returns:
            dict: Contains 'receipts' (List[Dict]) with matching receipt summaries.
        """
        receipts = list(self.receipts.values())
        if receipt_type:
            receipts = [r for r in receipts if r["receipt_type"] == receipt_type]
        if status:
            receipts = [r for r in receipts if r["status"] == status]
        summaries = [
            {
                "receipt_id": r["receipt_id"],
                "receipt_type": r["receipt_type"],
                "amount": r["amount"],
                "vendor": r["vendor"],
                "status": r["status"],
            }
            for r in receipts
        ]
        return {"receipts": summaries}

    # ── Bank transaction management ──────────────────────────────────────

    def add_bank_transaction(
        self,
        amount: float,
        date: str,
        description: str,
        card_last_four: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Add a bank transaction record for reconciliation matching.

        Args:
            amount (float): Transaction amount.
            date (str): Transaction date (e.g. '2024-01-15').
            description (str): Transaction description from bank statement.
            card_last_four (str): Last four digits of the card used.
            metadata (Dict): [Optional] Additional transaction details.

        Returns:
            dict: Contains 'transaction_id' (str) and 'transaction' (Dict) with the created record.
        """
        if amount is None or amount <= 0:
            return {"error": "Transaction amount must be a positive number."}
        if not date.strip():
            return {"error": "Transaction date is required."}
        if not description.strip():
            return {"error": "Transaction description is required."}
        if not card_last_four.strip() or len(card_last_four) != 4:
            return {"error": "Card last four digits must be exactly 4 characters."}

        transaction_id = str(self.transaction_counter)
        self.transaction_counter += 1

        transaction = {
            "transaction_id": transaction_id,
            "amount": amount,
            "date": date,
            "description": description,
            "card_last_four": card_last_four,
            "metadata": metadata or {},
            "matched_receipt_id": None,
            "status": "unmatched",
        }
        self.bank_transactions[transaction_id] = transaction
        self._log("transaction_added", {"transaction_id": transaction_id, "amount": amount})
        return {"transaction_id": transaction_id, "transaction": transaction}

    def get_bank_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """
        Retrieve a bank transaction by its ID.

        Args:
            transaction_id (str): Transaction ID.

        Returns:
            dict: Contains 'transaction' (Dict) with the full transaction record.
        """
        transaction = self.bank_transactions.get(transaction_id)
        if not transaction:
            return {"error": f"Bank transaction '{transaction_id}' not found."}
        return {"transaction": transaction}

    def list_bank_transactions(self, status: Optional[str] = None) -> Dict[str, Any]:
        """
        List bank transactions, optionally filtered by matching status.

        Args:
            status (str): [Optional] Filter by matching status ('matched', 'unmatched').

        Returns:
            dict: Contains 'transactions' (List[Dict]) with matching transaction summaries.
        """
        transactions = list(self.bank_transactions.values())
        if status:
            transactions = [t for t in transactions if t["status"] == status]
        summaries = [
            {
                "transaction_id": t["transaction_id"],
                "amount": t["amount"],
                "date": t["date"],
                "description": t["description"],
                "status": t["status"],
            }
            for t in transactions
        ]
        return {"transactions": summaries}

    # ── Reconciliation and matching ──────────────────────────────────────

    def match_receipt_to_transaction(
        self,
        receipt_id: str,
        transaction_id: str,
    ) -> Dict[str, Any]:
        """
        Match a receipt to a bank transaction for reconciliation.

        Args:
            receipt_id (str): Receipt ID.
            transaction_id (str): Bank transaction ID.

        Returns:
            dict: Contains 'receipt_id', 'transaction_id', 'discrepancy' (float), and 'status'.
        """
        receipt = self.receipts.get(receipt_id)
        if not receipt:
            return {"error": f"Receipt '{receipt_id}' not found."}
        transaction = self.bank_transactions.get(transaction_id)
        if not transaction:
            return {"error": f"Bank transaction '{transaction_id}' not found."}

        if receipt["status"] == "matched":
            return {"error": f"Receipt '{receipt_id}' is already matched to transaction '{receipt['matched_transaction_id']}'."}
        if transaction["status"] == "matched":
            return {"error": f"Transaction '{transaction_id}' is already matched to receipt '{transaction['matched_receipt_id']}'."}

        discrepancy = abs(receipt["amount"] - transaction["amount"])
        receipt["matched_transaction_id"] = transaction_id
        receipt["status"] = "matched"
        transaction["matched_receipt_id"] = receipt_id
        transaction["status"] = "matched"

        self._log("match_created", {
            "receipt_id": receipt_id,
            "transaction_id": transaction_id,
            "discrepancy": discrepancy,
        })

        return {
            "receipt_id": receipt_id,
            "transaction_id": transaction_id,
            "discrepancy": discrepancy,
            "status": "matched",
        }

    # ── Reimbursement form management ────────────────────────────────────

    def create_reimbursement_form(
        self,
        sm_id: int,
        receipt_ids: List[str],
        employee_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a reimbursement form entity from matched receipts, starting at the initial state.

        Args:
            sm_id (int): State machine ID that governs this reimbursement workflow.
            receipt_ids (List[str]): List of receipt IDs to include in this form.
            employee_id (str): Employee submitting the reimbursement.
            metadata (Dict): [Optional] Additional form data (e.g. department, project code).

        Returns:
            dict: Contains 'form_id' (str) and 'form' (Dict) with the created reimbursement form.
        """
        sm = self._find_sm(sm_id)
        if not sm:
            return {"error": f"State machine ID {sm_id} not found."}
        if not receipt_ids:
            return {"error": "At least one receipt ID is required."}
        if not employee_id.strip():
            return {"error": "Employee ID is required."}

        for receipt_id in receipt_ids:
            if receipt_id not in self.receipts:
                return {"error": f"Receipt '{receipt_id}' not found."}

        form_id = str(self.form_counter)
        self.form_counter += 1

        receipts = [self.receipts[rid] for rid in receipt_ids]
        total_amount = sum(r["amount"] for r in receipts)
        total_discrepancy = sum(
            abs(r["amount"] - self.bank_transactions[r["matched_transaction_id"]]["amount"])
            if r["matched_transaction_id"] and r["matched_transaction_id"] in self.bank_transactions
            else 0
            for r in receipts
        )

        form = {
            "form_id": form_id,
            "sm_id": sm_id,
            "current_state": sm["initial_state"],
            "employee_id": employee_id,
            "receipt_ids": receipt_ids,
            "total_amount": total_amount,
            "total_discrepancy": total_discrepancy,
            "metadata": metadata or {},
            "history": [{"state": sm["initial_state"], "timestamp": datetime.now().isoformat()}],
            "status": "active",
        }
        self.reimbursement_forms[form_id] = form
        sm["form_count"] += 1
        self._log("form_created", {"form_id": form_id, "sm_id": sm_id, "employee_id": employee_id})
        return {"form_id": form_id, "form": form}

    def trigger_form_transition(self, form_id: str, to_state: str) -> Dict[str, Any]:
        """
        Attempt to transition a reimbursement form to a target state.

        Validates that a transition exists from the current state to the target state,
        and that all guard conditions are satisfied against the form's data.

        Args:
            form_id (str): Reimbursement form ID.
            to_state (str): Desired target state.

        Returns:
            dict: Contains 'form_id', 'from_state', 'to_state', and 'result' indicating
                'transitioned', 'blocked_by_guard', or 'no_transition'.
        """
        form = self.reimbursement_forms.get(form_id)
        if not form:
            return {"error": f"Reimbursement form '{form_id}' not found."}
        if form["status"] != "active":
            return {"error": f"Reimbursement form '{form_id}' is {form['status']}."}

        sm = self._find_sm(form["sm_id"])
        if not sm:
            return {"error": f"State machine {form['sm_id']} not found."}

        current = form["current_state"]

        matching = [t for t in sm["transitions"] if t["from"] == current and t["to"] == to_state]
        if not matching:
            return {
                "form_id": form_id,
                "from_state": current,
                "to_state": to_state,
                "result": "no_transition",
                "available": [t["to"] for t in sm["transitions"] if t["from"] == current],
            }

        transition = matching[0]
        form_data = {
            "total_amount": form["total_amount"],
            "total_discrepancy": form["total_discrepancy"],
            "receipt_count": len(form["receipt_ids"]),
        }
        form_data.update(form["metadata"])

        if not self._validate_guard(transition.get("guard", {}), form_data):
            return {
                "form_id": form_id,
                "from_state": current,
                "to_state": to_state,
                "result": "blocked_by_guard",
                "failed_guard": transition["guard"],
            }

        form["current_state"] = to_state
        form["history"].append({"state": to_state, "timestamp": datetime.now().isoformat()})
        self.reconciliation_log.append({
            "form_id": form_id,
            "from": current,
            "to": to_state,
            "timestamp": datetime.now().isoformat(),
        })

        if to_state in sm["terminal_states"]:
            form["status"] = "completed"

        self._log("form_transition", {"form_id": form_id, "from": current, "to": to_state})
        return {
            "form_id": form_id,
            "from_state": current,
            "to_state": to_state,
            "result": "transitioned",
        }

    def get_reimbursement_form(self, form_id: str) -> Dict[str, Any]:
        """
        Get the full state and history of a reimbursement form.

        Args:
            form_id (str): Reimbursement form ID.

        Returns:
            dict: Contains 'form' (Dict) with the full form record including state and history.
        """
        form = self.reimbursement_forms.get(form_id)
        if not form:
            return {"error": f"Reimbursement form '{form_id}' not found."}
        return {"form": form}

    def list_reimbursement_forms(
        self,
        sm_id: Optional[int] = None,
        state: Optional[str] = None,
        employee_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List reimbursement forms, optionally filtered by state machine, current state, or employee.

        Args:
            sm_id (int): [Optional] Filter by state machine ID.
            state (str): [Optional] Filter by current state.
            employee_id (str): [Optional] Filter by employee ID.

        Returns:
            dict: Contains 'forms' (List[Dict]) with matching form summaries.
        """
        forms = list(self.reimbursement_forms.values())
        if sm_id is not None:
            forms = [f for f in forms if f["sm_id"] == sm_id]
        if state:
            forms = [f for f in forms if f["current_state"] == state]
        if employee_id:
            forms = [f for f in forms if f["employee_id"] == employee_id]
        summaries = [
            {
                "form_id": f["form_id"],
                "sm_id": f["sm_id"],
                "current_state": f["current_state"],
                "employee_id": f["employee_id"],
                "total_amount": f["total_amount"],
                "total_discrepancy": f["total_discrepancy"],
                "status": f["status"],
            }
            for f in forms
        ]
        return {"forms": summaries}

    def calculate_discrepancy(self, form_id: str) -> Dict[str, Any]:
        """
        Calculate the total discrepancy between receipts and bank transactions for a form.

        Args:
            form_id (str): Reimbursement form ID.

        Returns:
            dict: Contains 'form_id', 'total_discrepancy' (float), and 'details' (List[Dict])
                with per-receipt discrepancy breakdown.
        """
        form = self.reimbursement_forms.get(form_id)
        if not form:
            return {"error": f"Reimbursement form '{form_id}' not found."}

        details = []
        total_discrepancy = 0.0

        for receipt_id in form["receipt_ids"]:
            receipt = self.receipts.get(receipt_id)
            if not receipt:
                continue

            if receipt["matched_transaction_id"]:
                transaction = self.bank_transactions.get(receipt["matched_transaction_id"])
                if transaction:
                    discrepancy = abs(receipt["amount"] - transaction["amount"])
                    total_discrepancy += discrepancy
                    details.append({
                        "receipt_id": receipt_id,
                        "receipt_amount": receipt["amount"],
                        "transaction_amount": transaction["amount"],
                        "discrepancy": discrepancy,
                    })
                else:
                    details.append({
                        "receipt_id": receipt_id,
                        "receipt_amount": receipt["amount"],
                        "transaction_amount": None,
                        "discrepancy": None,
                        "note": "Matched transaction not found",
                    })
            else:
                details.append({
                    "receipt_id": receipt_id,
                    "receipt_amount": receipt["amount"],
                    "transaction_amount": None,
                    "discrepancy": None,
                    "note": "No matching transaction",
                })

        form["total_discrepancy"] = total_discrepancy
        self._log("discrepancy_calculated", {"form_id": form_id, "total_discrepancy": total_discrepancy})
        return {
            "form_id": form_id,
            "total_discrepancy": total_discrepancy,
            "details": details,
        }

    # ── Helpers ───────────────────────────────────────────────────────────

    def _find_sm(self, sm_id: int) -> Optional[Dict[str, Any]]:
        for sm in self.state_machines:
            if sm["sm_id"] == sm_id:
                return sm
        return None

    @staticmethod
    def _validate_guard(guard: Dict, data: Dict) -> bool:
        """Evaluate guard conditions against form data. Returns True if all pass."""
        if not guard:
            return True
        ops = {
            "eq": lambda a, b: a == b,
            "neq": lambda a, b: a != b,
            "gt": lambda a, b: a > b,
            "lt": lambda a, b: a < b,
            "gte": lambda a, b: a >= b,
            "lte": lambda a, b: a <= b,
            "contains": lambda a, b: b in a if hasattr(a, '__contains__') else False,
        }
        for field, condition in guard.items():
            actual = data.get(field)
            if actual is None:
                return False
            for op, expected in condition.items():
                if op not in ops:
                    continue
                if not ops[op](actual, expected):
                    return False
        return True

    def _log(self, event: str, detail: Dict) -> None:
        self.reconciliation_log.append({
            "event": event,
            "detail": detail,
            "timestamp": datetime.now().isoformat(),
        })