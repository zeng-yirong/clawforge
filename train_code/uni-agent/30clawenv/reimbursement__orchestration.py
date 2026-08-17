from copy import deepcopy
from typing import Dict, List, Optional, Any

DEFAULT_STATE = {
    "receipts": [],
    "bank_transactions": [],
    "reimbursement_forms": [],
    "reconciliation_log": [],
    "receipt_counter": 1,
    "transaction_counter": 1,
    "form_counter": 1,
}

VALID_RECEIPT_STATUSES = ("pending", "ocr_processing", "ocr_completed", "ocr_failed", "matched", "unmatched")
VALID_TRANSACTION_STATUSES = ("pending", "matched", "unmatched", "disputed")
VALID_FORM_STATUSES = ("draft", "pending_review", "approved", "rejected", "submitted", "paid")
VALID_RECONCILIATION_STATUSES = ("matched", "amount_mismatch", "missing_receipt", "missing_transaction", "duplicate")


class ExpenseReconciliationEnv:
    """
    An automated expense reconciliation environment for OCR receipt processing,
    bank transaction matching, and reimbursement form generation.

    This class models an end-to-end expense reconciliation pipeline where receipts
    are OCR-processed, matched against bank transactions, and automatically populated
    into reimbursement forms with discrepancy detection and reconciliation tracking.

    Attributes:
        receipts (List[Dict]): All uploaded receipts with OCR results and matching status.
        bank_transactions (List[Dict]): Bank card transaction records for matching.
        reimbursement_forms (List[Dict]): Generated reimbursement forms with line items.
        reconciliation_log (List[Dict]): History of all reconciliation operations.
        receipt_counter (int): Auto-incrementing receipt ID counter.
        transaction_counter (int): Auto-incrementing transaction ID counter.
        form_counter (int): Auto-incrementing form ID counter.
    """

    def __init__(self):
        self.receipts: List[Dict[str, Any]]
        self.bank_transactions: List[Dict[str, Any]]
        self.reimbursement_forms: List[Dict[str, Any]]
        self.reconciliation_log: List[Dict[str, Any]]
        self.receipt_counter: int
        self.transaction_counter: int
        self.form_counter: int
        self._api_description = (
            "This tool provides automated expense reconciliation: OCR receipt processing, "
            "bank transaction matching, reimbursement form auto-population, and discrepancy detection."
        )

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.receipts = scenario.get("receipts", DEFAULT_STATE_COPY["receipts"])
        self.bank_transactions = scenario.get("bank_transactions", DEFAULT_STATE_COPY["bank_transactions"])
        self.reimbursement_forms = scenario.get("reimbursement_forms", DEFAULT_STATE_COPY["reimbursement_forms"])
        self.reconciliation_log = scenario.get("reconciliation_log", DEFAULT_STATE_COPY["reconciliation_log"])
        self.receipt_counter = scenario.get("receipt_counter", DEFAULT_STATE_COPY["receipt_counter"])
        self.transaction_counter = scenario.get("transaction_counter", DEFAULT_STATE_COPY["transaction_counter"])
        self.form_counter = scenario.get("form_counter", DEFAULT_STATE_COPY["form_counter"])

    def get_env_state(self) -> dict:
        """
        Return the current internal state of the environment.

        Returns:
            dict: All environment state variables including receipts, bank transactions,
                  reimbursement forms, reconciliation log, and counters.
        """
        return {
            "receipts": self.receipts,
            "bank_transactions": self.bank_transactions,
            "reimbursement_forms": self.reimbursement_forms,
            "reconciliation_log": self.reconciliation_log,
            "receipt_counter": self.receipt_counter,
            "transaction_counter": self.transaction_counter,
            "form_counter": self.form_counter,
        }

    # ── Receipt management ────────────────────────────────────────────────

    def upload_receipt(
        self,
        file_name: str,
        upload_date: str,
        employee_id: str,
        category: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Upload a new receipt for OCR processing and reconciliation.

        Args:
            file_name (str): Receipt file name (e.g., 'receipt_001.jpg').
            upload_date (str): Date when the receipt was uploaded (ISO format).
            employee_id (str): Employee ID who submitted the receipt.
            category (str): [Optional] Expense category (e.g., 'travel', 'meals', 'office_supplies').

        Returns:
            receipt_id (str): Unique receipt identifier.
            receipt (Dict): The uploaded receipt record.
        """
        if not file_name.strip() or not upload_date.strip() or not employee_id.strip():
            return {"error": "File name, upload date, and employee ID must all be non-empty."}

        receipt_id = str(self.receipt_counter)
        self.receipt_counter += 1

        receipt = {
            "receipt_id": receipt_id,
            "file_name": file_name,
            "upload_date": upload_date,
            "employee_id": employee_id,
            "category": category,
            "status": "pending",
            "ocr_result": None,
            "matched_transaction_id": None,
            "amount": None,
            "vendor": None,
            "date": None,
        }
        self.receipts.append(receipt)
        self._log("receipt_uploaded", {"receipt_id": receipt_id, "employee_id": employee_id, "file_name": file_name})
        return {"receipt_id": receipt_id, "receipt": receipt}

    def process_ocr(self, receipt_id: str) -> Dict[str, Any]:
        """
        Process OCR on an uploaded receipt to extract structured information.

        Args:
            receipt_id (str): Receipt ID to process.

        Returns:
            receipt_id (str): The processed receipt ID.
            status (str): OCR processing status.
            ocr_result (Dict): Extracted information including amount, vendor, date, and items.
        """
        receipt = self._find_receipt(receipt_id)
        if not receipt:
            return {"error": f"Receipt '{receipt_id}' not found."}
        if receipt["status"] not in ("pending", "ocr_failed"):
            return {"error": f"Receipt '{receipt_id}' is already {receipt['status']}."}

        receipt["status"] = "ocr_processing"
        self._log("ocr_started", {"receipt_id": receipt_id})

        success, ocr_result = self._simulate_ocr(receipt)

        if success:
            receipt["status"] = "ocr_completed"
            receipt["ocr_result"] = ocr_result
            receipt["amount"] = ocr_result.get("amount")
            receipt["vendor"] = ocr_result.get("vendor")
            receipt["date"] = ocr_result.get("date")
            self._log("ocr_completed", {"receipt_id": receipt_id, "amount": receipt["amount"]})
        else:
            receipt["status"] = "ocr_failed"
            receipt["ocr_result"] = ocr_result
            self._log("ocr_failed", {"receipt_id": receipt_id, "error": ocr_result.get("error")})

        return {"receipt_id": receipt_id, "status": receipt["status"], "ocr_result": ocr_result}

    def list_receipts(
        self, employee_id: Optional[str] = None, status: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all receipts, optionally filtered by employee or status.

        Args:
            employee_id (str): [Optional] Filter by employee ID.
            status (str): [Optional] Filter by receipt status.

        Returns:
            receipts (List[Dict]): Matching receipt records.
        """
        if status and status not in VALID_RECEIPT_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_RECEIPT_STATUSES)}"}
        receipts = self.receipts
        if employee_id:
            receipts = [r for r in receipts if r["employee_id"] == employee_id]
        if status:
            receipts = [r for r in receipts if r["status"] == status]
        return {"receipts": receipts}

    # ── Bank transaction management ───────────────────────────────────────

    def import_bank_transaction(
        self,
        transaction_date: str,
        amount: float,
        merchant: str,
        card_last_four: str,
        employee_id: str,
    ) -> Dict[str, Any]:
        """
        Import a bank card transaction record for matching with receipts.

        Args:
            transaction_date (str): Transaction date (ISO format).
            amount (float): Transaction amount.
            merchant (str): Merchant name from bank statement.
            card_last_four (str): Last four digits of the card used.
            employee_id (str): Employee ID associated with the card.

        Returns:
            transaction_id (str): Unique transaction identifier.
            transaction (Dict): The imported transaction record.
        """
        if not transaction_date.strip() or not merchant.strip() or not employee_id.strip():
            return {"error": "Transaction date, merchant, and employee ID must all be non-empty."}
        if amount is None or amount <= 0:
            return {"error": "Transaction amount must be a positive number."}

        transaction_id = str(self.transaction_counter)
        self.transaction_counter += 1

        transaction = {
            "transaction_id": transaction_id,
            "transaction_date": transaction_date,
            "amount": amount,
            "merchant": merchant,
            "card_last_four": card_last_four,
            "employee_id": employee_id,
            "status": "pending",
            "matched_receipt_id": None,
        }
        self.bank_transactions.append(transaction)
        self._log("transaction_imported", {"transaction_id": transaction_id, "amount": amount, "merchant": merchant})
        return {"transaction_id": transaction_id, "transaction": transaction}

    def list_transactions(
        self, employee_id: Optional[str] = None, status: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all bank transactions, optionally filtered by employee or status.

        Args:
            employee_id (str): [Optional] Filter by employee ID.
            status (str): [Optional] Filter by transaction status.

        Returns:
            transactions (List[Dict]): Matching transaction records.
        """
        if status and status not in VALID_TRANSACTION_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_TRANSACTION_STATUSES)}"}
        transactions = self.bank_transactions
        if employee_id:
            transactions = [t for t in transactions if t["employee_id"] == employee_id]
        if status:
            transactions = [t for t in transactions if t["status"] == status]
        return {"transactions": transactions}

    # ── Matching and reconciliation ───────────────────────────────────────

    def match_receipt_to_transaction(
        self, receipt_id: str, transaction_id: str, tolerance: float = 0.01
    ) -> Dict[str, Any]:
        """
        Match a receipt to a bank transaction and validate amount consistency.

        Args:
            receipt_id (str): Receipt ID to match.
            transaction_id (str): Transaction ID to match against.
            tolerance (float): [Optional] Acceptable amount difference ratio. Defaults to 0.01 (1%).

        Returns:
            receipt_id (str): The matched receipt ID.
            transaction_id (str): The matched transaction ID.
            reconciliation_status (str): Match result — 'matched' or 'amount_mismatch'.
            amount_difference (float): Absolute difference between receipt and transaction amounts.
        """
        receipt = self._find_receipt(receipt_id)
        if not receipt:
            return {"error": f"Receipt '{receipt_id}' not found."}
        if receipt["status"] != "ocr_completed":
            return {"error": f"Receipt '{receipt_id}' must be OCR-completed before matching."}

        transaction = self._find_transaction(transaction_id)
        if not transaction:
            return {"error": f"Transaction '{transaction_id}' not found."}
        if transaction["status"] == "matched":
            return {"error": f"Transaction '{transaction_id}' is already matched."}

        if receipt["employee_id"] != transaction["employee_id"]:
            return {"error": "Receipt and transaction belong to different employees."}

        receipt_amount = receipt.get("amount", 0)
        transaction_amount = transaction.get("amount", 0)
        amount_diff = abs(receipt_amount - transaction_amount)
        relative_diff = amount_diff / max(receipt_amount, transaction_amount) if max(receipt_amount, transaction_amount) > 0 else 0

        if relative_diff <= tolerance:
            reconciliation_status = "matched"
            receipt["status"] = "matched"
            receipt["matched_transaction_id"] = transaction_id
            transaction["status"] = "matched"
            transaction["matched_receipt_id"] = receipt_id
        else:
            reconciliation_status = "amount_mismatch"
            receipt["status"] = "unmatched"
            transaction["status"] = "unmatched"

        self._log("match_attempted", {
            "receipt_id": receipt_id,
            "transaction_id": transaction_id,
            "reconciliation_status": reconciliation_status,
            "amount_difference": amount_diff,
        })

        return {
            "receipt_id": receipt_id,
            "transaction_id": transaction_id,
            "reconciliation_status": reconciliation_status,
            "amount_difference": amount_diff,
        }

    def auto_match_all(self, employee_id: str, tolerance: float = 0.01) -> Dict[str, Any]:
        """
        Automatically match all unmatched receipts and transactions for an employee.

        Args:
            employee_id (str): Employee ID to process.
            tolerance (float): [Optional] Acceptable amount difference ratio. Defaults to 0.01 (1%).

        Returns:
            employee_id (str): The processed employee ID.
            matched_count (int): Number of successful matches.
            mismatch_count (int): Number of amount mismatches.
            unmatched_receipts (int): Remaining unmatched receipts.
            unmatched_transactions (int): Remaining unmatched transactions.
        """
        receipts = [r for r in self.receipts if r["employee_id"] == employee_id and r["status"] == "ocr_completed"]
        transactions = [t for t in self.bank_transactions if t["employee_id"] == employee_id and t["status"] == "pending"]

        matched_count = 0
        mismatch_count = 0

        for receipt in receipts:
            best_match = None
            best_diff = float('inf')

            for transaction in transactions:
                if transaction["status"] != "pending":
                    continue
                amount_diff = abs(receipt.get("amount", 0) - transaction.get("amount", 0))
                if amount_diff < best_diff:
                    best_diff = amount_diff
                    best_match = transaction

            if best_match:
                result = self.match_receipt_to_transaction(receipt["receipt_id"], best_match["transaction_id"], tolerance)
                if result.get("reconciliation_status") == "matched":
                    matched_count += 1
                else:
                    mismatch_count += 1

        unmatched_receipts = len([r for r in self.receipts if r["employee_id"] == employee_id and r["status"] in ("ocr_completed", "unmatched")])
        unmatched_transactions = len([t for t in self.bank_transactions if t["employee_id"] == employee_id and t["status"] == "pending"])

        self._log("auto_match_completed", {
            "employee_id": employee_id,
            "matched_count": matched_count,
            "mismatch_count": mismatch_count,
        })

        return {
            "employee_id": employee_id,
            "matched_count": matched_count,
            "mismatch_count": mismatch_count,
            "unmatched_receipts": unmatched_receipts,
            "unmatched_transactions": unmatched_transactions,
        }

    # ── Reimbursement form generation ─────────────────────────────────────

    def create_reimbursement_form(
        self,
        employee_id: str,
        receipt_ids: List[str],
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a reimbursement form from matched receipts.

        Args:
            employee_id (str): Employee ID submitting the form.
            receipt_ids (List[str]): List of receipt IDs to include in the form.
            description (str): [Optional] Additional description or notes.

        Returns:
            form_id (str): Unique reimbursement form identifier.
            form (Dict): The created reimbursement form with line items and totals.
        """
        if not receipt_ids:
            return {"error": "At least one receipt ID is required."}

        line_items = []
        total_amount = 0.0
        discrepancies = []

        for receipt_id in receipt_ids:
            receipt = self._find_receipt(receipt_id)
            if not receipt:
                return {"error": f"Receipt '{receipt_id}' not found."}
            if receipt["employee_id"] != employee_id:
                return {"error": f"Receipt '{receipt_id}' does not belong to employee '{employee_id}'."}
            if receipt["status"] not in ("matched", "unmatched", "ocr_completed"):
                return {"error": f"Receipt '{receipt_id}' is not ready for reimbursement (status: {receipt['status']})."}

            line_item = {
                "receipt_id": receipt_id,
                "date": receipt.get("date"),
                "vendor": receipt.get("vendor"),
                "category": receipt.get("category"),
                "amount": receipt.get("amount", 0),
                "matched_transaction_id": receipt.get("matched_transaction_id"),
            }

            if receipt["status"] == "unmatched":
                discrepancies.append({
                    "receipt_id": receipt_id,
                    "issue": "No matching bank transaction found",
                })
            elif receipt.get("matched_transaction_id"):
                transaction = self._find_transaction(receipt["matched_transaction_id"])
                if transaction:
                    amount_diff = abs(receipt.get("amount", 0) - transaction.get("amount", 0))
                    if amount_diff > 0.01:
                        discrepancies.append({
                            "receipt_id": receipt_id,
                            "issue": f"Amount mismatch: receipt={receipt.get('amount')}, transaction={transaction.get('amount')}",
                            "difference": amount_diff,
                        })

            line_items.append(line_item)
            total_amount += receipt.get("amount", 0)

        form_id = str(self.form_counter)
        self.form_counter += 1

        form = {
            "form_id": form_id,
            "employee_id": employee_id,
            "status": "draft",
            "line_items": line_items,
            "total_amount": total_amount,
            "discrepancies": discrepancies,
            "description": description,
            "created_at": f"t+{self.form_counter}",
            "submitted_at": None,
            "approved_at": None,
        }
        self.reimbursement_forms.append(form)
        self._log("form_created", {"form_id": form_id, "employee_id": employee_id, "total_amount": total_amount})
        return {"form_id": form_id, "form": form}

    def submit_reimbursement_form(self, form_id: str) -> Dict[str, Any]:
        """
        Submit a reimbursement form for review and approval.

        Args:
            form_id (str): Form ID to submit.

        Returns:
            form_id (str): The submitted form ID.
            status (str): New form status.
            discrepancy_count (int): Number of discrepancies flagged.
        """
        form = self._find_form(form_id)
        if not form:
            return {"error": f"Reimbursement form '{form_id}' not found."}
        if form["status"] != "draft":
            return {"error": f"Form '{form_id}' is already {form['status']}."}

        form["status"] = "pending_review"
        form["submitted_at"] = f"t+{self.form_counter}"
        discrepancy_count = len(form.get("discrepancies", []))

        self._log("form_submitted", {"form_id": form_id, "discrepancy_count": discrepancy_count})
        return {"form_id": form_id, "status": form["status"], "discrepancy_count": discrepancy_count}

    def approve_reimbursement_form(self, form_id: str, approver_id: str) -> Dict[str, Any]:
        """
        Approve a reimbursement form for payment processing.

        Args:
            form_id (str): Form ID to approve.
            approver_id (str): ID of the approving manager or finance officer.

        Returns:
            form_id (str): The approved form ID.
            status (str): New form status.
            total_amount (float): Approved reimbursement amount.
        """
        form = self._find_form(form_id)
        if not form:
            return {"error": f"Reimbursement form '{form_id}' not found."}
        if form["status"] != "pending_review":
            return {"error": f"Form '{form_id}' is not pending review (current status: {form['status']})."}

        form["status"] = "approved"
        form["approved_at"] = f"t+{self.form_counter}"
        form["approver_id"] = approver_id

        self._log("form_approved", {"form_id": form_id, "approver_id": approver_id, "total_amount": form["total_amount"]})
        return {"form_id": form_id, "status": form["status"], "total_amount": form["total_amount"]}

    def reject_reimbursement_form(self, form_id: str, reason: str) -> Dict[str, Any]:
        """
        Reject a reimbursement form with a reason.

        Args:
            form_id (str): Form ID to reject.
            reason (str): Rejection reason.

        Returns:
            form_id (str): The rejected form ID.
            status (str): New form status.
            reason (str): Rejection reason.
        """
        form = self._find_form(form_id)
        if not form:
            return {"error": f"Reimbursement form '{form_id}' not found."}
        if form["status"] != "pending_review":
            return {"error": f"Form '{form_id}' is not pending review (current status: {form['status']})."}
        if not reason.strip():
            return {"error": "Rejection reason cannot be empty."}

        form["status"] = "rejected"
        form["rejection_reason"] = reason

        self._log("form_rejected", {"form_id": form_id, "reason": reason})
        return {"form_id": form_id, "status": form["status"], "reason": reason}

    def list_reimbursement_forms(
        self, employee_id: Optional[str] = None, status: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all reimbursement forms, optionally filtered by employee or status.

        Args:
            employee_id (str): [Optional] Filter by employee ID.
            status (str): [Optional] Filter by form status.

        Returns:
            forms (List[Dict]): Matching reimbursement form records.
        """
        if status and status not in VALID_FORM_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_FORM_STATUSES)}"}
        forms = self.reimbursement_forms
        if employee_id:
            forms = [f for f in forms if f["employee_id"] == employee_id]
        if status:
            forms = [f for f in forms if f["status"] == status]
        return {"forms": forms}

    # ── Discrepancy analysis ──────────────────────────────────────────────

    def analyze_discrepancies(self, employee_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze all discrepancies across receipts and transactions.

        Args:
            employee_id (str): [Optional] Filter by employee ID.

        Returns:
            summary (Dict): Discrepancy statistics and breakdown.
            details (List[Dict]): Detailed discrepancy records.
        """
        receipts = self.receipts
        transactions = self.bank_transactions
        if employee_id:
            receipts = [r for r in receipts if r["employee_id"] == employee_id]
            transactions = [t for t in transactions if t["employee_id"] == employee_id]

        unmatched_receipts = [r for r in receipts if r["status"] in ("ocr_completed", "unmatched")]
        unmatched_transactions = [t for t in transactions if t["status"] == "pending"]

        amount_mismatches = []
        for receipt in receipts:
            if receipt["status"] == "matched" and receipt.get("matched_transaction_id"):
                transaction = self._find_transaction(receipt["matched_transaction_id"])
                if transaction:
                    amount_diff = abs(receipt.get("amount", 0) - transaction.get("amount", 0))
                    if amount_diff > 0.01:
                        amount_mismatches.append({
                            "receipt_id": receipt["receipt_id"],
                            "transaction_id": transaction["transaction_id"],
                            "receipt_amount": receipt.get("amount"),
                            "transaction_amount": transaction.get("amount"),
                            "difference": amount_diff,
                        })

        summary = {
            "total_receipts": len(receipts),
            "total_transactions": len(transactions),
            "unmatched_receipts": len(unmatched_receipts),
            "unmatched_transactions": len(unmatched_transactions),
            "amount_mismatches": len(amount_mismatches),
        }

        details = {
            "unmatched_receipts": [{"receipt_id": r["receipt_id"], "amount": r.get("amount"), "vendor": r.get("vendor")} for r in unmatched_receipts],
            "unmatched_transactions": [{"transaction_id": t["transaction_id"], "amount": t.get("amount"), "merchant": t.get("merchant")} for t in unmatched_transactions],
            "amount_mismatches": amount_mismatches,
        }

        return {"summary": summary, "details": details}

    # ── Helpers ───────────────────────────────────────────────────────────

    def _find_receipt(self, receipt_id: str) -> Optional[Dict[str, Any]]:
        """Find a receipt by ID. Returns None if not found."""
        for r in self.receipts:
            if r["receipt_id"] == receipt_id:
                return r
        return None

    def _find_transaction(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """Find a transaction by ID. Returns None if not found."""
        for t in self.bank_transactions:
            if t["transaction_id"] == transaction_id:
                return t
        return None

    def _find_form(self, form_id: str) -> Optional[Dict[str, Any]]:
        """Find a reimbursement form by ID. Returns None if not found."""
        for f in self.reimbursement_forms:
            if f["form_id"] == form_id:
                return f
        return None

    def _simulate_ocr(self, receipt: Dict) -> tuple:
        """Simulate OCR processing. Returns (success: bool, result: dict)."""
        return True, {
            "amount": 125.50,
            "vendor": "Sample Vendor Inc.",
            "date": "2024-01-15",
            "items": [
                {"description": "Item 1", "quantity": 2, "unit_price": 50.00},
                {"description": "Item 2", "quantity": 1, "unit_price": 25.50},
            ],
            "confidence": 0.95,
        }

    def _log(self, event: str, detail: Dict) -> None:
        """Append an entry to the reconciliation log."""
        self.reconciliation_log.append({"event": event, "detail": detail, "timestamp": f"t+{self.form_counter}"})