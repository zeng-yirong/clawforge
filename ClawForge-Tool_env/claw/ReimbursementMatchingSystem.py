from copy import deepcopy
from typing import Dict, List, Optional, Union, Any, Tuple
from datetime import datetime

DEFAULT_STATE = {
    "batches": [],
    "invoices": [],
    "transactions": [],
    "reconciliations": [],
    "config": {
        "tolerance_percentage": 0.01,
        "auto_fill_enabled": True,
        "review_required_threshold": 1000.0,
    },
    "batch_counter": 1,
    "invoice_counter": 1,
    "transaction_counter": 1,
    "reconciliation_counter": 1,
    "audit_log": [],
}

VALID_INVOICE_STATUSES = ("pending", "processing", "verified", "rejected", "filled")
VALID_TRANSACTION_TYPES = ("payment", "withdrawal", "refund", "adjustment")
VALID_RECONCILIATION_STATUSES = ("pending", "matched", "partial", "unmatched", "adjusted")


class InvoiceReconciliationEnv:
    """
    An automated invoice reconciliation environment for expense reimbursement.

    This class models a financial reconciliation system that processes OCR-scanned invoices,
    compares them against bank transaction records, auto-fills expense reports in financial
    systems, and identifies discrepancies. It handles the complete lifecycle from invoice
    ingestion to final reconciliation approval.

    Attributes:
        batches (List[Dict]): Processing batches for grouping related invoices.
        invoices (List[Dict]): All invoices with OCR-extracted data.
        transactions (List[Dict]): Bank transaction records.
        reconciliations (List[Dict]): Generated reconciliation records.
        config (Dict): System configuration parameters.
        batch_counter (int): Auto-incrementing batch ID counter.
        invoice_counter (int): Auto-incrementing invoice ID counter.
        transaction_counter (int): Auto-incrementing transaction ID counter.
        reconciliation_counter (int): Auto-incrementing reconciliation ID counter.
        audit_log (List[Dict]): Audit trail of all operations.
    """

    def __init__(self):
        self.batches: List[Dict[str, Any]]
        self.invoices: List[Dict[str, Any]]
        self.transactions: List[Dict[str, Any]]
        self.reconciliations: List[Dict[str, Any]]
        self.config: Dict[str, Any]
        self.batch_counter: int
        self.invoice_counter: int
        self.transaction_counter: int
        self.reconciliation_counter: int
        self.audit_log: List[Dict[str, Any]]
        self._api_description = (
            "This tool automates expense invoice reconciliation by processing OCR-scanned "
            "invoices, matching with bank transactions, auto-filling expense reports, "
            "and identifying discrepancies for financial approval workflows."
        )

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.batches = scenario.get("batches", DEFAULT_STATE_COPY["batches"])
        self.invoices = scenario.get("invoices", DEFAULT_STATE_COPY["invoices"])
        self.transactions = scenario.get("transactions", DEFAULT_STATE_COPY["transactions"])
        self.reconciliations = scenario.get("reconciliations", DEFAULT_STATE_COPY["reconciliations"])
        self.config = scenario.get("config", DEFAULT_STATE_COPY["config"])
        self.batch_counter = scenario.get("batch_counter", DEFAULT_STATE_COPY["batch_counter"])
        self.invoice_counter = scenario.get("invoice_counter", DEFAULT_STATE_COPY["invoice_counter"])
        self.transaction_counter = scenario.get("transaction_counter", DEFAULT_STATE_COPY["transaction_counter"])
        self.reconciliation_counter = scenario.get("reconciliation_counter", DEFAULT_STATE_COPY["reconciliation_counter"])
        self.audit_log = scenario.get("audit_log", DEFAULT_STATE_COPY["audit_log"])

    def get_env_state(self) -> dict:
        """
        Return the current internal state of the environment.

        Returns:
            dict: All environment state variables including batches, invoices,
                transactions, reconciliations, configuration, counters, and audit log.
        """
        return {
            "batches": self.batches,
            "invoices": self.invoices,
            "transactions": self.transactions,
            "reconciliations": self.reconciliations,
            "config": self.config,
            "batch_counter": self.batch_counter,
            "invoice_counter": self.invoice_counter,
            "transaction_counter": self.transaction_counter,
            "reconciliation_counter": self.reconciliation_counter,
            "audit_log": self.audit_log,
        }

    # ── Batch management ──────────────────────────────────────────────────

    def create_batch(
        self,
        name: str,
        description: str = "",
        owner: str = "",
    ) -> Dict[str, Any]:
        """
        Create a new processing batch for grouping related invoices.

        Args:
            name (str): Batch name/identifier.
            description (str): Optional description of the batch.
            owner (str): Responsible person or department.

        Returns:
            batch_id (int): Unique batch identifier.
            batch (Dict): The created batch record.
        """
        if not name.strip():
            return {"error": "Batch name is required."}

        batch_id = self.batch_counter
        self.batch_counter += 1

        batch = {
            "batch_id": batch_id,
            "name": name,
            "description": description,
            "owner": owner,
            "created_time": self._current_timestamp(),
            "status": "active",
            "invoice_count": 0,
            "processed_count": 0,
        }
        self.batches.append(batch)
        self._log("batch_created", {"batch_id": batch_id, "name": name})
        return {"batch_id": batch_id, "batch": batch}

    def list_batches(
        self,
        status: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List all processing batches, optionally filtered by status.

        Args:
            status (str): [Optional] Filter by batch status ('active', 'closed').

        Returns:
            batches (List[Dict]): Batch summaries.
        """
        if status and status not in ("active", "closed"):
            return {"error": f"Invalid status '{status}'. Must be 'active' or 'closed'."}
        batches = self.batches
        if status:
            batches = [b for b in batches if b["status"] == status]
        return {"batches": batches}

    # ── Invoice management ─────────────────────────────────────────────────

    def add_invoice(
        self,
        batch_id: int,
        invoice_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Add an OCR-processed invoice to a batch.

        Args:
            batch_id (int): Target batch ID.
            invoice_data (Dict[str, Any]): OCR-extracted invoice information.
                Required fields:
                    - 'vendor' (str): Vendor/supplier name.
                    - 'amount' (float): Invoice total amount.
                    - 'date' (str): Invoice date (YYYY-MM-DD format).
                Optional fields:
                    - 'description' (str): Invoice description.
                    - 'currency' (str): Currency code (default: 'USD').
                    - 'tax_amount' (float): Tax amount if separate.
                    - 'items' (List[Dict]): Line item details.

        Returns:
            invoice_id (int): Unique invoice identifier.
            invoice (Dict): The added invoice record.
        """
        batch = self._find_batch(batch_id)
        if not batch:
            return {"error": f"Batch ID {batch_id} not found."}
        if batch["status"] != "active":
            return {"error": f"Batch {batch_id} is {batch['status']}, not active."}

        # Validate required fields
        required = ["vendor", "amount", "date"]
        for field in required:
            if field not in invoice_data:
                return {"error": f"Missing required field: {field}"}

        try:
            amount = float(invoice_data["amount"])
            if amount <= 0:
                return {"error": "Invoice amount must be positive."}
        except (ValueError, TypeError):
            return {"error": "Invoice amount must be a valid number."}

        invoice_id = self.invoice_counter
        self.invoice_counter += 1

        invoice = {
            "invoice_id": invoice_id,
            "batch_id": batch_id,
            "vendor": invoice_data["vendor"],
            "amount": amount,
            "date": invoice_data["date"],
            "description": invoice_data.get("description", ""),
            "currency": invoice_data.get("currency", "USD"),
            "tax_amount": invoice_data.get("tax_amount", 0.0),
            "items": invoice_data.get("items", []),
            "status": "pending",
            "added_time": self._current_timestamp(),
            "matched_transactions": [],
            "discrepancy": 0.0,
        }
        self.invoices.append(invoice)

        batch["invoice_count"] += 1
        self._log("invoice_added", {"invoice_id": invoice_id, "batch_id": batch_id, "amount": amount})
        return {"invoice_id": invoice_id, "invoice": invoice}

    def list_invoices(
        self,
        batch_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List invoices, optionally filtered by batch or status.

        Args:
            batch_id (int): [Optional] Filter by batch ID.
            status (str): [Optional] Filter by invoice status.

        Returns:
            invoices (List[Dict]): Matching invoice records.
        """
        if status and status not in VALID_INVOICE_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_INVOICE_STATUSES)}"}
        invoices = self.invoices
        if batch_id is not None:
            invoices = [i for i in invoices if i["batch_id"] == batch_id]
        if status:
            invoices = [i for i in invoices if i["status"] == status]
        return {"invoices": invoices}

    def validate_invoice(
        self,
        invoice_id: int,
        validation_result: str,
        notes: str = "",
    ) -> Dict[str, Any]:
        """
        Validate an invoice after OCR processing.

        Args:
            invoice_id (int): Invoice ID to validate.
            validation_result (str): 'verified' or 'rejected'.
            notes (str): [Optional] Validation notes or reason for rejection.

        Returns:
            invoice_id (int): The validated invoice ID.
            status (str): New invoice status.
        """
        invoice = self._find_invoice(invoice_id)
        if not invoice:
            return {"error": f"Invoice ID {invoice_id} not found."}
        if invoice["status"] != "pending":
            return {"error": f"Invoice {invoice_id} is {invoice['status']}, not pending."}
        if validation_result not in ("verified", "rejected"):
            return {"error": f"Invalid validation_result '{validation_result}'. Must be 'verified' or 'rejected'."}

        invoice["status"] = validation_result
        invoice["validation_notes"] = notes
        invoice["validated_time"] = self._current_timestamp()

        batch = self._find_batch(invoice["batch_id"])
        if batch and validation_result == "verified":
            batch["processed_count"] += 1

        self._log("invoice_validated", {"invoice_id": invoice_id, "result": validation_result})
        return {"invoice_id": invoice_id, "status": validation_result}

    # ── Transaction management ────────────────────────────────────────────

    def add_transaction(
        self,
        transaction_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Add a bank transaction record for reconciliation.

        Args:
            transaction_data (Dict[str, Any]): Bank transaction information.
                Required fields:
                    - 'transaction_id' (str): Bank's transaction ID.
                    - 'amount' (float): Transaction amount (positive for credit, negative for debit).
                    - 'date' (str): Transaction date (YYYY-MM-DD).
                Optional fields:
                    - 'description' (str): Transaction description.
                    - 'type' (str): Transaction type.
                    - 'counterparty' (str): Counterparty name.
                    - 'reference' (str): Payment reference.

        Returns:
            transaction_record_id (int): Internal transaction record ID.
            transaction (Dict): The added transaction record.
        """
        required = ["transaction_id", "amount", "date"]
        for field in required:
            if field not in transaction_data:
                return {"error": f"Missing required field: {field}"}

        try:
            amount = float(transaction_data["amount"])
        except (ValueError, TypeError):
            return {"error": "Transaction amount must be a valid number."}

        # Check for duplicate bank transaction ID
        existing = [t for t in self.transactions if t["bank_transaction_id"] == transaction_data["transaction_id"]]
        if existing:
            return {"error": f"Transaction ID {transaction_data['transaction_id']} already exists."}

        transaction_record_id = self.transaction_counter
        self.transaction_counter += 1

        transaction = {
            "transaction_record_id": transaction_record_id,
            "bank_transaction_id": transaction_data["transaction_id"],
            "amount": amount,
            "date": transaction_data["date"],
            "description": transaction_data.get("description", ""),
            "type": transaction_data.get("type", "payment"),
            "counterparty": transaction_data.get("counterparty", ""),
            "reference": transaction_data.get("reference", ""),
            "status": "unreconciled",
            "added_time": self._current_timestamp(),
            "matched_invoices": [],
        }
        self.transactions.append(transaction)

        self._log("transaction_added", {
            "transaction_record_id": transaction_record_id,
            "bank_transaction_id": transaction_data["transaction_id"],
            "amount": amount
        })
        return {"transaction_record_id": transaction_record_id, "transaction": transaction}

    def list_transactions(
        self,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List transaction records with optional filters.

        Args:
            status (str): [Optional] Filter by status ('unreconciled', 'matched', 'partial').
            start_date (str): [Optional] Start date filter (YYYY-MM-DD).
            end_date (str): [Optional] End date filter (YYYY-MM-DD).

        Returns:
            transactions (List[Dict]): Matching transaction records.
        """
        if status and status not in ("unreconciled", "matched", "partial"):
            return {"error": f"Invalid status '{status}'. Must be 'unreconciled', 'matched', or 'partial'."}
        transactions = self.transactions
        if status:
            transactions = [t for t in transactions if t["status"] == status]
        if start_date:
            transactions = [t for t in transactions if t["date"] >= start_date]
        if end_date:
            transactions = [t for t in transactions if t["date"] <= end_date]
        return {"transactions": transactions}

    # ── Reconciliation ────────────────────────────────────────────────────

    def reconcile_invoice(
        self,
        invoice_id: int,
        max_date_difference: int = 7,
    ) -> Dict[str, Any]:
        """
        Reconcile an invoice against available bank transactions.

        Compares invoice details with bank transactions to find matching or
        partially matching records. Calculates discrepancies and suggests
        reconciliation actions.

        Args:
            invoice_id (int): Invoice ID to reconcile.
            max_date_difference (int): Maximum allowed days between invoice and
                transaction dates. Defaults to 7.

        Returns:
            invoice_id (int): The reconciled invoice ID.
            matches (List[Dict]): Found transaction matches with scores.
            discrepancy (float): Total discrepancy amount.
            status (str): Reconciliation status.
        """
        invoice = self._find_invoice(invoice_id)
        if not invoice:
            return {"error": f"Invoice ID {invoice_id} not found."}
        if invoice["status"] != "verified":
            return {"error": f"Invoice {invoice_id} is {invoice['status']}, not verified."}

        # Find candidate transactions
        candidate_transactions = [
            t for t in self.transactions
            if t["status"] in ("unreconciled", "partial")
        ]

        matches = []
        total_matched = 0.0

        for transaction in candidate_transactions:
            score = self._compute_match_score(invoice, transaction, max_date_difference)

            if score["total_score"] >= 70:  # Threshold for potential match
                match_entry = {
                    "transaction_record_id": transaction["transaction_record_id"],
                    "bank_transaction_id": transaction["bank_transaction_id"],
                    "score": score["total_score"],
                    "amount_difference": score["amount_difference"],
                    "date_difference": score["date_difference"],
                    "vendor_match": score["vendor_match"],
                }
                matches.append(match_entry)

        # Sort by match score
        matches.sort(key=lambda m: m["score"], reverse=True)

        # Calculate total discrepancy
        discrepancy = invoice["amount"]
        if matches:
            best_match = matches[0]
            discrepancy = abs(best_match["amount_difference"])
            total_matched = abs(best_match["amount_difference"])

        # Determine reconciliation status
        if total_matched == 0:
            status = "unmatched"
        elif abs(discrepancy) <= invoice["amount"] * self.config["tolerance_percentage"]:
            status = "matched"
        else:
            status = "partial"

        # Create reconciliation record
        reconciliation_id = self.reconciliation_counter
        self.reconciliation_counter += 1

        reconciliation = {
            "reconciliation_id": reconciliation_id,
            "invoice_id": invoice_id,
            "batch_id": invoice["batch_id"],
            "status": status,
            "discrepancy": discrepancy,
            "matches": matches,
            "created_time": self._current_timestamp(),
            "auto_fill_applied": False,
            "requires_review": invoice["amount"] >= self.config["review_required_threshold"],
        }
        self.reconciliations.append(reconciliation)

        invoice["discrepancy"] = discrepancy
        invoice["status"] = "processing"
        invoice["matched_transactions"] = [m["bank_transaction_id"] for m in matches]

        self._log("invoice_reconciled", {
            "invoice_id": invoice_id,
            "reconciliation_id": reconciliation_id,
            "status": status,
            "match_count": len(matches),
            "discrepancy": discrepancy,
        })

        return {
            "invoice_id": invoice_id,
            "matches": matches,
            "discrepancy": discrepancy,
            "status": status,
            "reconciliation_id": reconciliation_id,
        }

    def auto_fill_expense_report(
        self,
        reconciliation_id: int,
        system_fields: Dict[str, str],
    ) -> Dict[str, Any]:
        """
        Auto-fill expense report in financial system based on reconciliation.

        Uses reconciled invoice data to automatically populate expense report
        fields in the financial system, reducing manual data entry.

        Args:
            reconciliation_id (int): Reconciliation ID to use for auto-fill.
            system_fields (Dict[str, str]): Mapping of financial system field names
                to invoice data fields. e.g. {
                    'vendor_field': 'vendor',
                    'amount_field': 'amount',
                    'date_field': 'date',
                    'description_field': 'description'
                }

        Returns:
            reconciliation_id (int): The processed reconciliation ID.
            filled_fields (Dict): The auto-filled field values.
            status (str): Auto-fill status.
        """
        reconciliation = self._find_reconciliation(reconciliation_id)
        if not reconciliation:
            return {"error": f"Reconciliation ID {reconciliation_id} not found."}
        if reconciliation["status"] not in ("matched", "partial"):
            return {"error": f"Cannot auto-fill: reconciliation is {reconciliation['status']}"}

        invoice = self._find_invoice(reconciliation["invoice_id"])
        if not invoice:
            return {"error": f"Cannot find invoice for reconciliation {reconciliation_id}"}

        if not self.config["auto_fill_enabled"]:
            return {"error": "Auto-fill is disabled in system configuration."}

        # Map invoice data to system fields
        filled_fields = {}
        invoice_data = {
            "vendor": invoice["vendor"],
            "amount": invoice["amount"],
            "date": invoice["date"],
            "description": invoice["description"],
            "currency": invoice["currency"],
            "discrepancy": reconciliation["discrepancy"],
        }

        for system_field, invoice_field in system_fields.items():
            if invoice_field in invoice_data:
                filled_fields[system_field] = invoice_data[invoice_field]
            else:
                filled_fields[system_field] = ""

        reconciliation["auto_fill_applied"] = True
        reconciliation["filled_fields"] = filled_fields
        reconciliation["auto_fill_time"] = self._current_timestamp()

        invoice["status"] = "filled"
        self._log("expense_report_filled", {
            "reconciliation_id": reconciliation_id,
            "invoice_id": invoice["invoice_id"],
            "field_count": len(filled_fields),
        })

        return {
            "reconciliation_id": reconciliation_id,
            "filled_fields": filled_fields,
            "status": "filled",
            "requires_approval": reconciliation["requires_review"],
        }

    def approve_reconciliation(
        self,
        reconciliation_id: int,
        approver: str,
        notes: str = "",
    ) -> Dict[str, Any]:
        """
        Approve a reconciliation for final processing.

        Args:
            reconciliation_id (int): Reconciliation ID to approve.
            approver (str): Name/ID of the approver.
            notes (str): [Optional] Approval notes or comments.

        Returns:
            reconciliation_id (int): The approved reconciliation ID.
            status (str): New reconciliation status.
        """
        reconciliation = self._find_reconciliation(reconciliation_id)
        if not reconciliation:
            return {"error": f"Reconciliation ID {reconciliation_id} not found."}

        if reconciliation["requires_review"] and not approver:
            return {"error": f"Approval required for reconciliation {reconciliation_id}"}

        # Update reconciliation status
        reconciliation["approved_by"] = approver
        reconciliation["approved_time"] = self._current_timestamp()
        reconciliation["approval_notes"] = notes
        reconciliation["status"] = "approved"

        # Update associated invoice
        invoice = self._find_invoice(reconciliation["invoice_id"])
        if invoice:
            invoice["status"] = "approved"

        # Update associated transactions if matched
        if reconciliation["matches"]:
            for match in reconciliation["matches"]:
                transaction = self._find_transaction_by_record(match["transaction_record_id"])
                if transaction:
                    transaction["status"] = "matched"
                    transaction["reconciliation_id"] = reconciliation_id

        self._log("reconciliation_approved", {
            "reconciliation_id": reconciliation_id,
            "approver": approver,
            "invoice_amount": invoice["amount"] if invoice else 0.0,
        })

        return {
            "reconciliation_id": reconciliation_id,
            "status": "approved",
            "approver": approver,
        }

    def list_reconciliations(
        self,
        batch_id: Optional[int] = None,
        status: Optional[str] = None,
        requires_review: Optional[bool] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List reconciliation records with optional filters.

        Args:
            batch_id (int): [Optional] Filter by batch ID.
            status (str): [Optional] Filter by reconciliation status.
            requires_review (bool): [Optional] Filter by review requirement.

        Returns:
            reconciliations (List[Dict]): Matching reconciliation records.
        """
        if status and status not in VALID_RECONCILIATION_STATUSES + ("approved",):
            return {"error": f"Invalid status '{status}'."}
        reconciliations = self.reconciliations
        if batch_id is not None:
            reconciliations = [r for r in reconciliations if r["batch_id"] == batch_id]
        if status:
            reconciliations = [r for r in reconciliations if r["status"] == status]
        if requires_review is not None:
            reconciliations = [r for r in reconciliations if r["requires_review"] == requires_review]
        return {"reconciliations": reconciliations}

    def get_discrepancy_summary(
        self,
        batch_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get summary statistics of reconciliation discrepancies.

        Args:
            batch_id (int): [Optional] Filter by batch ID.

        Returns:
            summary (Dict): Discrepancy statistics.
        """
        reconciliations = self.reconciliations
        if batch_id is not None:
            reconciliations = [r for r in reconciliations if r["batch_id"] == batch_id]

        total_invoices = len([i for i in self.invoices if not batch_id or i["batch_id"] == batch_id])
        reconciled_invoices = len([r for r in reconciliations if r["status"] in ("matched", "partial", "approved")])

        matched_count = len([r for r in reconciliations if r["status"] in ("matched", "approved")])
        partial_count = len([r for r in reconciliations if r["status"] == "partial"])
        unmatched_count = len([r for r in reconciliations if r["status"] == "unmatched"])

        total_discrepancy = sum(abs(r["discrepancy"]) for r in reconciliations)
        avg_discrepancy = total_discrepancy / len(reconciliations) if reconciliations else 0

        return {
            "total_invoices": total_invoices,
            "reconciled_invoices": reconciled_invoices,
            "matched_count": matched_count,
            "partial_count": partial_count,
            "unmatched_count": unmatched_count,
            "total_discrepancy": round(total_discrepancy, 2),
            "average_discrepancy": round(avg_discrepancy, 2),
            "reconciliation_rate": round(reconciled_invoices / total_invoices * 100, 1) if total_invoices else 0,
        }

    # ── Configuration ─────────────────────────────────────────────────────

    def update_config(
        self,
        config_updates: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Update system configuration parameters.

        Args:
            config_updates (Dict[str, Any]): Configuration updates.
                Supported fields:
                    - 'tolerance_percentage' (float): Allowed discrepancy percentage.
                    - 'auto_fill_enabled' (bool): Enable/disable auto-fill.
                    - 'review_required_threshold' (float): Amount threshold for review.

        Returns:
            config (Dict): Updated configuration.
        """
        valid_fields = {"tolerance_percentage", "auto_fill_enabled", "review_required_threshold"}

        for field, value in config_updates.items():
            if field not in valid_fields:
                return {"error": f"Invalid config field: {field}"}

            if field == "tolerance_percentage":
                if not isinstance(value, (int, float)) or value < 0 or value > 1:
                    return {"error": "tolerance_percentage must be between 0 and 1"}
                self.config[field] = float(value)
            elif field == "auto_fill_enabled":
                if not isinstance(value, bool):
                    return {"error": "auto_fill_enabled must be boolean"}
                self.config[field] = value
            elif field == "review_required_threshold":
                if not isinstance(value, (int, float)) or value < 0:
                    return {"error": "review_required_threshold must be non-negative number"}
                self.config[field] = float(value)

        self._log("config_updated", {"updates": config_updates})
        return {"config": self.config}

    # ── Helpers ───────────────────────────────────────────────────────────

    def _find_batch(self, batch_id: int) -> Optional[Dict[str, Any]]:
        for b in self.batches:
            if b["batch_id"] == batch_id:
                return b
        return None

    def _find_invoice(self, invoice_id: int) -> Optional[Dict[str, Any]]:
        for i in self.invoices:
            if i["invoice_id"] == invoice_id:
                return i
        return None

    def _find_transaction_by_record(self, transaction_record_id: int) -> Optional[Dict[str, Any]]:
        for t in self.transactions:
            if t["transaction_record_id"] == transaction_record_id:
                return t
        return None

    def _find_reconciliation(self, reconciliation_id: int) -> Optional[Dict[str, Any]]:
        for r in self.reconciliations:
            if r["reconciliation_id"] == reconciliation_id:
                return r
        return None

    @staticmethod
    def _compute_match_score(
        invoice: Dict[str, Any],
        transaction: Dict[str, Any],
        max_date_difference: int,
    ) -> Dict[str, Any]:
        """
        Compute match score between invoice and transaction.
        """
        score_components = {
            "amount_match": 0.0,
            "date_match": 0.0,
            "vendor_match": 0.0,
        }

        # Amount comparison (absolute values for payment matching)
        invoice_amount = abs(invoice["amount"])
        transaction_amount = abs(transaction["amount"])

        if invoice_amount > 0 and transaction_amount > 0:
            amount_ratio = min(invoice_amount, transaction_amount) / max(invoice_amount, transaction_amount)
            score_components["amount_match"] = amount_ratio * 40  # Weight: 40%

        # Date comparison
        try:
            inv_date = datetime.strptime(invoice["date"], "%Y-%m-%d")
            trans_date = datetime.strptime(transaction["date"], "%Y-%m-%d")
            date_diff = abs((inv_date - trans_date).days)

            if date_diff <= max_date_difference:
                date_score = 1.0 - (date_diff / max_date_difference)
                score_components["date_match"] = date_score * 30  # Weight: 30%
        except (ValueError, TypeError):
            pass

        # Vendor name comparison
        invoice_vendor = invoice["vendor"].lower().strip()
        transaction_counterparty = transaction.get("counterparty", "").lower().strip()
        trans_description = transaction.get("description", "").lower().strip()

        vendor_match = False
        if invoice_vendor in transaction_counterparty or invoice_vendor in trans_description:
            vendor_match = True
            score_components["vendor_match"] = 30  # Weight: 30%
        elif transaction_counterparty and invoice_vendor and transaction_counterparty in invoice_vendor:
            vendor_match = True
            score_components["vendor_match"] = 25  # Partial match

        total_score = sum(score_components.values())

        return {
            "total_score": round(total_score),
            "amount_difference": invoice_amount - transaction_amount,
            "date_difference": date_diff if 'date_diff' in locals() else None,
            "vendor_match": vendor_match,
            "components": score_components,
        }

    @staticmethod
    def _current_timestamp() -> str:
        """Generate current timestamp string."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _log(self, event: str, detail: Dict) -> None:
        """Add entry to audit log."""
        self.audit_log.append({
            "event": event,
            "detail": detail,
            "timestamp": self._current_timestamp(),
        })