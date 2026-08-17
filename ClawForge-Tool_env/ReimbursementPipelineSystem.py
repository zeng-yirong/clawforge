from copy import deepcopy
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
import random
import hashlib

DEFAULT_STATE = {
    "receipts": {
        "receipt_1": {
            "id": "receipt_1",
            "filename": "receipt_20240515.jpg",
            "ocr_status": "pending",
            "ocr_data": None,
            "category": "office_supplies",
            "amount": 250.0,
            "currency": "CNY",
            "date": "2024-05-15",
            "merchant": "Office Depot",
            "tax_amount": 25.0,
            "employee_id": "EMP001",
            "verified": False
        },
        "receipt_2": {
            "id": "receipt_2",
            "filename": "invoice_travel.pdf",
            "ocr_status": "completed",
            "ocr_data": {
                "total_amount": 1200.0,
                "currency": "CNY",
                "date": "2024-05-10",
                "merchant": "Air China",
                "tax_id": "91110108785678901"
            },
            "category": "business_travel",
            "amount": 1200.0,
            "currency": "CNY",
            "date": "2024-05-10",
            "merchant": "Air China",
            "tax_amount": 0.0,
            "employee_id": "EMP002",
            "verified": True
        }
    },
    "bank_statements": {
        "statement_1": {
            "id": "statement_1",
            "bank_name": "ICBC",
            "account_number": "622202******1234",
            "period": "2024-05",
            "transactions": [
                {
                    "id": "txn_001",
                    "date": "2024-05-16",
                    "description": "OFFICE DEPOT",
                    "amount": -250.0,
                    "currency": "CNY",
                    "type": "debit",
                    "matched_receipt": None
                },
                {
                    "id": "txn_002",
                    "date": "2024-05-12",
                    "description": "AIR CHINA BOOKING",
                    "amount": -1200.0,
                    "currency": "CNY",
                    "type": "debit",
                    "matched_receipt": "receipt_2"
                }
            ],
            "uploaded_at": "2024-05-20T10:30:00"
        }
    },
    "expense_reports": {
        "report_1": {
            "id": "report_1",
            "employee_id": "EMP001",
            "period": "2024-05",
            "status": "draft",
            "total_amount": 1450.0,
            "approved_amount": 0.0,
            "items": [
                {
                    "receipt_id": "receipt_1",
                    "description": "Office Supplies",
                    "amount": 250.0,
                    "status": "pending"
                },
                {
                    "receipt_id": "receipt_2",
                    "description": "Business Travel",
                    "amount": 1200.0,
                    "status": "approved"
                }
            ],
            "created_at": "2024-05-20",
            "submitted_at": None,
            "approved_at": None
        }
    },
    "processing_log": [],
    "receipt_counter": 3,
    "report_counter": 2,
    "statement_counter": 2
}

VALID_OCR_STATUSES = ("pending", "processing", "completed", "failed")
VALID_REPORT_STATUSES = ("draft", "submitted", "under_review", "approved", "rejected", "paid")
VALID_CURRENCIES = ("CNY", "USD", "EUR", "JPY", "GBP")
VALID_RECEIPT_CATEGORIES = ("office_supplies", "business_travel", "meals", "transportation", "entertainment", "other")


class AutomatedReconciliationEnv:
    """
    An automated expense reconciliation pipeline environment.

    This class models an end-to-end expense reimbursement workflow that covers:
    OCR recognition of receipt information → bank statement matching → 
    automated expense report generation → financial system integration.
    Agents can upload receipts and bank statements, run OCR processing,
    match transactions, generate expense reports, and reconcile differences.

    Attributes:
        receipts (Dict): Registry of uploaded receipts with OCR data.
        bank_statements (Dict): Bank statement records with transactions.
        expense_reports (Dict): Generated expense reports with status tracking.
        processing_log (List[Dict]): Audit log of all processing operations.
        receipt_counter (int): Auto-incrementing receipt ID counter.
        report_counter (int): Auto-incrementing report ID counter.
        statement_counter (int): Auto-incrementing statement ID counter.
    """

    def __init__(self):
        self.receipts: Dict[str, Dict[str, Any]]
        self.bank_statements: Dict[str, Dict[str, Any]]
        self.expense_reports: Dict[str, Dict[str, Any]]
        self.processing_log: List[Dict[str, Any]]
        self.receipt_counter: int
        self.report_counter: int
        self.statement_counter: int
        self._api_description = (
            "This tool provides an automated expense reconciliation pipeline covering "
            "OCR receipt processing, bank statement matching, expense report generation, "
            "and financial system integration for automated reimbursement."
        )

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        """
        Load initial state from a scenario dictionary.

        Args:
            scenario (dict): Dictionary containing scenario configuration.
            long_context (bool): [Optional] Flag for extended context scenarios.
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.receipts = scenario.get("receipts", DEFAULT_STATE_COPY["receipts"])
        self.bank_statements = scenario.get("bank_statements", DEFAULT_STATE_COPY["bank_statements"])
        self.expense_reports = scenario.get("expense_reports", DEFAULT_STATE_COPY["expense_reports"])
        self.processing_log = scenario.get("processing_log", DEFAULT_STATE_COPY["processing_log"])
        self.receipt_counter = scenario.get("receipt_counter", DEFAULT_STATE_COPY["receipt_counter"])
        self.report_counter = scenario.get("report_counter", DEFAULT_STATE_COPY["report_counter"])
        self.statement_counter = scenario.get("statement_counter", DEFAULT_STATE_COPY["statement_counter"])

    def get_env_state(self) -> dict:
        """
        Return the current internal state of the environment.

        Returns:
            dict: All environment state variables including receipts, 
                  bank_statements, expense_reports, processing_log, and counters.
        """
        return {
            "receipts": self.receipts,
            "bank_statements": self.bank_statements,
            "expense_reports": self.expense_reports,
            "processing_log": self.processing_log,
            "receipt_counter": self.receipt_counter,
            "report_counter": self.report_counter,
            "statement_counter": self.statement_counter,
        }

    # ── Receipt Management ───────────────────────────────────────────────

    def upload_receipt(
        self, 
        filename: str, 
        employee_id: str, 
        category: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upload a new receipt for processing.

        Args:
            filename (str): Name of the receipt file.
            employee_id (str): Employee identifier.
            category (str): Expense category. Must be one of VALID_RECEIPT_CATEGORIES.
            metadata (Dict): [Optional] Additional metadata for the receipt.

        Returns:
            receipt_id (str): Unique receipt identifier.
            receipt (Dict): The uploaded receipt entry.
        """
        if category not in VALID_RECEIPT_CATEGORIES:
            return {"error": f"Invalid category '{category}'. Must be one of: {', '.join(VALID_RECEIPT_CATEGORIES)}"}

        receipt_id = f"receipt_{self.receipt_counter}"
        self.receipt_counter += 1

        receipt = {
            "id": receipt_id,
            "filename": filename,
            "ocr_status": "pending",
            "ocr_data": None,
            "category": category,
            "amount": 0.0,
            "currency": "CNY",
            "date": None,
            "merchant": None,
            "tax_amount": 0.0,
            "employee_id": employee_id,
            "verified": False,
            "metadata": metadata or {}
        }
        
        self.receipts[receipt_id] = receipt
        self._log("receipt_uploaded", {"receipt_id": receipt_id, "employee_id": employee_id, "category": category})
        
        return {"receipt_id": receipt_id, "receipt": receipt}

    def run_ocr_processing(
        self, 
        receipt_id: str, 
        language: str = "zh-CN",
        auto_verify: bool = False
    ) -> Dict[str, Any]:
        """
        Run OCR processing on an uploaded receipt.

        Args:
            receipt_id (str): The receipt ID to process.
            language (str): [Optional] Language for OCR. Defaults to 'zh-CN'.
            auto_verify (bool): [Optional] Automatically verify OCR results. Defaults to False.

        Returns:
            receipt_id (str): Processed receipt ID.
            status (str): Processing status.
            ocr_data (Dict): Extracted OCR data.
        """
        if receipt_id not in self.receipts:
            return {"error": f"Receipt ID '{receipt_id}' not found."}

        receipt = self.receipts[receipt_id]
        if receipt["ocr_status"] not in ("pending", "failed"):
            return {"error": f"Receipt {receipt_id} is already {receipt['ocr_status']}."}

        receipt["ocr_status"] = "processing"
        self._log("ocr_started", {"receipt_id": receipt_id, "language": language})

        # Simulate OCR processing
        ocr_data = self._simulate_ocr_extraction(receipt["filename"], language)
        
        receipt["ocr_status"] = "completed"
        receipt["ocr_data"] = ocr_data
        
        # Update receipt fields from OCR data
        receipt["amount"] = ocr_data.get("total_amount", 0.0)
        receipt["currency"] = ocr_data.get("currency", "CNY")
        receipt["date"] = ocr_data.get("date", datetime.now().strftime("%Y-%m-%d"))
        receipt["merchant"] = ocr_data.get("merchant", "Unknown")
        receipt["tax_amount"] = ocr_data.get("tax_amount", 0.0)
        
        if auto_verify:
            receipt["verified"] = True
            self._log("receipt_auto_verified", {"receipt_id": receipt_id})

        self._log("ocr_completed", {"receipt_id": receipt_id, "amount_extracted": receipt["amount"]})
        return {"receipt_id": receipt_id, "status": "completed", "ocr_data": ocr_data}

    def list_receipts(
        self, 
        employee_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List uploaded receipts, optionally filtered by employee or status.

        Args:
            employee_id (str): [Optional] Filter by employee ID.
            status (str): [Optional] Filter by OCR status.

        Returns:
            receipts (List[Dict]): Matching receipt entries.
        """
        if status and status not in VALID_OCR_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_OCR_STATUSES)}"}

        result = []
        for receipt_id, receipt in self.receipts.items():
            if employee_id and receipt["employee_id"] != employee_id:
                continue
            if status and receipt["ocr_status"] != status:
                continue
            
            result.append({
                "receipt_id": receipt_id,
                "filename": receipt["filename"],
                "employee_id": receipt["employee_id"],
                "category": receipt["category"],
                "amount": receipt["amount"],
                "ocr_status": receipt["ocr_status"],
                "verified": receipt["verified"]
            })
        
        return {"receipts": result}

    # ── Bank Statement Management ───────────────────────────────────────

    def upload_bank_statement(
        self,
        bank_name: str,
        account_number: str,
        period: str,
        transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Upload a bank statement for reconciliation.

        Args:
            bank_name (str): Name of the bank.
            account_number (str): Account number (masked).
            period (str): Statement period (e.g., "2024-05").
            transactions (List[Dict]): List of transaction records.

        Returns:
            statement_id (str): Unique statement identifier.
            statement (Dict): The uploaded statement entry.
        """
        statement_id = f"statement_{self.statement_counter}"
        self.statement_counter += 1

        # Validate transactions
        for txn in transactions:
            if "date" not in txn or "amount" not in txn or "description" not in txn:
                return {"error": "Each transaction must have date, amount, and description fields."}

        statement = {
            "id": statement_id,
            "bank_name": bank_name,
            "account_number": account_number,
            "period": period,
            "transactions": transactions,
            "uploaded_at": datetime.now().isoformat()
        }
        
        self.bank_statements[statement_id] = statement
        self._log("statement_uploaded", {
            "statement_id": statement_id,
            "bank_name": bank_name,
            "transaction_count": len(transactions)
        })
        
        return {"statement_id": statement_id, "statement": statement}

    def match_receipts_to_transactions(
        self,
        statement_id: str,
        matching_strategy: str = "fuzzy_date_amount"
    ) -> Dict[str, Any]:
        """
        Match receipts to bank statement transactions.

        Args:
            statement_id (str): The statement ID to match against.
            matching_strategy (str): [Optional] Matching strategy. Defaults to 'fuzzy_date_amount'.

        Returns:
            statement_id (str): Processed statement ID.
            matches (List[Dict]): List of matched pairs.
            unmatched_receipts (List[str]): List of unmatched receipt IDs.
        """
        if statement_id not in self.bank_statements:
            return {"error": f"Statement ID '{statement_id}' not found."}

        statement = self.bank_statements[statement_id]
        matches = []
        matched_receipts = set()
        unmatched_receipts = []

        # Get receipts that need matching
        for receipt_id, receipt in self.receipts.items():
            if not receipt["verified"]:
                continue
                
            best_match = None
            best_score = 0
            
            for txn in statement["transactions"]:
                if txn.get("matched_receipt"):
                    continue  # Already matched
                
                score = self._calculate_match_score(receipt, txn, matching_strategy)
                if score > best_score and score > 0.5:  # Threshold
                    best_score = score
                    best_match = txn
            
            if best_match:
                best_match["matched_receipt"] = receipt_id
                matches.append({
                    "receipt_id": receipt_id,
                    "transaction_id": best_match["id"],
                    "receipt_amount": receipt["amount"],
                    "transaction_amount": abs(best_match["amount"]),
                    "match_score": best_score,
                    "date_diff": self._date_diff(receipt["date"], best_match["date"])
                })
                matched_receipts.add(receipt_id)
            else:
                unmatched_receipts.append(receipt_id)

        self._log("matching_completed", {
            "statement_id": statement_id,
            "total_matches": len(matches),
            "unmatched_count": len(unmatched_receipts)
        })
        
        eligible_count = sum(1 for r in self.receipts.values() if r["verified"])
        return {
            "statement_id": statement_id,
            "matches": matches,
            "unmatched_receipts": unmatched_receipts,
            "match_rate": len(matches) / max(eligible_count, 1)
        }

    # ── Expense Report Management ──────────────────────────────────────

    def create_expense_report(
        self,
        employee_id: str,
        period: str,
        receipt_ids: List[str],
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Create a new expense report.

        Args:
            employee_id (str): Employee identifier.
            period (str): Report period (e.g., "2024-05").
            receipt_ids (List[str]): List of receipt IDs to include.
            description (str): [Optional] Report description.

        Returns:
            report_id (str): Unique report identifier.
            report (Dict): The created report entry.
        """
        # Validate receipts
        invalid_receipts = []
        total_amount = 0.0
        items = []
        
        for receipt_id in receipt_ids:
            if receipt_id not in self.receipts:
                invalid_receipts.append(receipt_id)
                continue
                
            receipt = self.receipts[receipt_id]
            if not receipt["verified"]:
                return {"error": f"Receipt {receipt_id} is not verified. Verify it first."}
            
            total_amount += receipt["amount"]
            items.append({
                "receipt_id": receipt_id,
                "description": receipt["category"].replace("_", " ").title(),
                "amount": receipt["amount"],
                "status": "pending"
            })
        
        if invalid_receipts:
            return {"error": f"Invalid receipt IDs: {', '.join(invalid_receipts)}"}

        report_id = f"report_{self.report_counter}"
        self.report_counter += 1

        report = {
            "id": report_id,
            "employee_id": employee_id,
            "period": period,
            "status": "draft",
            "total_amount": total_amount,
            "approved_amount": 0.0,
            "items": items,
            "description": description or f"Expense Report {period}",
            "created_at": datetime.now().strftime("%Y-%m-%d"),
            "submitted_at": None,
            "approved_at": None
        }
        
        self.expense_reports[report_id] = report
        self._log("report_created", {
            "report_id": report_id,
            "employee_id": employee_id,
            "receipt_count": len(receipt_ids),
            "total_amount": total_amount
        })
        
        return {"report_id": report_id, "report": report}

    def submit_expense_report(self, report_id: str) -> Dict[str, Any]:
        """
        Submit an expense report for approval.

        Args:
            report_id (str): The report ID to submit.

        Returns:
            report_id (str): Submitted report ID.
            status (str): New report status.
        """
        if report_id not in self.expense_reports:
            return {"error": f"Report ID '{report_id}' not found."}
        
        report = self.expense_reports[report_id]
        if report["status"] != "draft":
            return {"error": f"Report {report_id} is already {report['status']}. Only drafts can be submitted."}
        
        report["status"] = "submitted"
        report["submitted_at"] = datetime.now().strftime("%Y-%m-%d")
        
        self._log("report_submitted", {
            "report_id": report_id,
            "employee_id": report["employee_id"],
            "total_amount": report["total_amount"]
        })
        
        return {"report_id": report_id, "status": "submitted"}

    def review_expense_report(
        self,
        report_id: str,
        action: str,
        notes: Optional[str] = None,
        approved_amounts: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Review and approve/reject an expense report.

        Args:
            report_id (str): The report ID to review.
            action (str): Review action - 'approve' or 'reject'.
            notes (str): [Optional] Review notes.
            approved_amounts (Dict): [Optional] Approved amounts per item.

        Returns:
            report_id (str): Reviewed report ID.
            status (str): New report status.
            total_approved (float): Total approved amount.
        """
        if report_id not in self.expense_reports:
            return {"error": f"Report ID '{report_id}' not found."}
        
        report = self.expense_reports[report_id]
        if report["status"] != "submitted":
            return {"error": f"Report {report_id} is {report['status']}. Only submitted reports can be reviewed."}
        
        if action not in ("approve", "reject"):
            return {"error": f"Invalid action '{action}'. Must be 'approve' or 'reject'."}
        
        if action == "approve":
            report["status"] = "approved"
            report["approved_at"] = datetime.now().strftime("%Y-%m-%d")
            
            # Calculate approved amount
            if approved_amounts:
                total_approved = 0.0
                for item in report["items"]:
                    receipt_id = item["receipt_id"]
                    if receipt_id in approved_amounts:
                        approved = approved_amounts[receipt_id]
                        item["status"] = "approved" if approved > 0 else "rejected"
                        item["approved_amount"] = approved
                        total_approved += approved
                    else:
                        item["status"] = "approved"
                        item["approved_amount"] = item["amount"]
                        total_approved += item["amount"]
                report["approved_amount"] = total_approved
            else:
                report["approved_amount"] = report["total_amount"]
                for item in report["items"]:
                    item["status"] = "approved"
                    item["approved_amount"] = item["amount"]
        else:
            report["status"] = "rejected"
            for item in report["items"]:
                item["status"] = "rejected"
                item["approved_amount"] = 0.0
        
        self._log("report_reviewed", {
            "report_id": report_id,
            "action": action,
            "approved_amount": report.get("approved_amount", 0)
        })
        
        return {
            "report_id": report_id,
            "status": report["status"],
            "total_approved": report.get("approved_amount", 0),
            "notes": notes
        }

    def list_expense_reports(
        self,
        employee_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        List expense reports, optionally filtered by employee or status.

        Args:
            employee_id (str): [Optional] Filter by employee ID.
            status (str): [Optional] Filter by report status.

        Returns:
            reports (List[Dict]): Matching report summaries.
        """
        if status and status not in VALID_REPORT_STATUSES:
            return {"error": f"Invalid status '{status}'. Must be one of: {', '.join(VALID_REPORT_STATUSES)}"}

        result = []
        for report_id, report in self.expense_reports.items():
            if employee_id and report["employee_id"] != employee_id:
                continue
            if status and report["status"] != status:
                continue
            
            result.append({
                "report_id": report_id,
                "employee_id": report["employee_id"],
                "period": report["period"],
                "status": report["status"],
                "total_amount": report["total_amount"],
                "approved_amount": report["approved_amount"],
                "item_count": len(report["items"]),
                "created_at": report["created_at"]
            })
        
        return {"reports": result}

    # ── Reconciliation ────────────────────────────────────────────────

    def reconcile_payments(
        self,
        report_id: str,
        statement_id: str
    ) -> Dict[str, Any]:
        """
        Reconcile approved expenses with bank payments.

        Args:
            report_id (str): The approved expense report ID.
            statement_id (str): The bank statement ID.

        Returns:
            reconciliation_id (str): Unique reconciliation identifier.
            status (str): Reconciliation status.
            discrepancies (List[Dict]): List of discrepancies found.
        """
        if report_id not in self.expense_reports:
            return {"error": f"Report ID '{report_id}' not found."}
        if statement_id not in self.bank_statements:
            return {"error": f"Statement ID '{statement_id}' not found."}
        
        report = self.expense_reports[report_id]
        statement = self.bank_statements[statement_id]
        
        if report["status"] != "approved":
            return {"error": f"Report {report_id} is {report['status']}. Only approved reports can be reconciled."}
        
        reconciliation_id = f"recon_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        discrepancies = []
        matched_payments = []
        
        # Find matching payments in statement
        for item in report["items"]:
            if item["status"] != "approved":
                continue
                
            receipt_id = item["receipt_id"]
            approved_amount = item.get("approved_amount", item["amount"])
            
            # Look for matching transaction
            matched = False
            for txn in statement["transactions"]:
                if txn.get("matched_receipt") == receipt_id:
                    payment_amount = abs(txn["amount"])
                    if abs(payment_amount - approved_amount) > 0.01:  # Tolerance
                        discrepancies.append({
                            "receipt_id": receipt_id,
                            "expected": approved_amount,
                            "actual": payment_amount,
                            "difference": payment_amount - approved_amount,
                            "transaction_id": txn["id"]
                        })
                    else:
                        matched_payments.append({
                            "receipt_id": receipt_id,
                            "amount": approved_amount,
                            "transaction_id": txn["id"],
                            "date": txn["date"]
                        })
                    matched = True
                    break
            
            if not matched:
                discrepancies.append({
                    "receipt_id": receipt_id,
                    "expected": approved_amount,
                    "actual": 0.0,
                    "difference": -approved_amount,
                    "transaction_id": None,
                    "note": "No matching payment found"
                })
        
        status = "complete" if not discrepancies else "discrepancies_found"
        
        self._log("reconciliation_completed", {
            "reconciliation_id": reconciliation_id,
            "report_id": report_id,
            "matched_payments": len(matched_payments),
            "discrepancies": len(discrepancies)
        })
        
        return {
            "reconciliation_id": reconciliation_id,
            "status": status,
            "total_approved": report["approved_amount"],
            "matched_payments": matched_payments,
            "discrepancies": discrepancies,
            "discrepancy_total": sum(d.get("difference", 0) for d in discrepancies)
        }

    # ── Helper Methods ────────────────────────────────────────────────

    def _simulate_ocr_extraction(self, filename: str, language: str) -> Dict[str, Any]:
        """
        Simulate OCR extraction from receipt images/documents.
        """

        random.seed(int(hashlib.md5(filename.encode()).hexdigest(), 16))
        
        # Generate realistic OCR data based on filename
        base_amount = random.uniform(50.0, 5000.0)
        rounded_amount = round(base_amount / 10) * 10  # Round to nearest 10
        
        merchants = ["Starbucks", "Amazon", "Uber", "China Eastern", "JD.com", "Meituan", "Didi", "Apple Store"]
        merchant = random.choice(merchants)
        
        return {
            "total_amount": rounded_amount,
            "currency": random.choice(VALID_CURRENCIES),
            "date": f"2024-05-{random.randint(1, 28):02d}",
            "merchant": merchant,
            "tax_amount": round(rounded_amount * random.uniform(0.05, 0.2), 2),
            "tax_id": f"91110{random.randint(100000000, 999999999)}" if random.random() > 0.3 else None,
            "confidence": round(random.uniform(0.85, 0.99), 3),
            "items": [
                {"description": f"Item {i+1}", "quantity": random.randint(1, 5), "price": round(rounded_amount/3, 2)}
                for i in range(random.randint(1, 5))
            ]
        }

    def _calculate_match_score(
        self, 
        receipt: Dict[str, Any], 
        transaction: Dict[str, Any],
        strategy: str
    ) -> float:
        """
        Calculate match score between receipt and transaction.
        """
        receipt_amount = receipt["amount"]
        transaction_amount = abs(transaction["amount"])  # Bank amounts are negative for debits
        
        # Amount match (40% weight)
        amount_diff = abs(receipt_amount - transaction_amount)
        amount_score = max(0, 1 - (amount_diff / max(receipt_amount, transaction_amount, 1)))
        
        # Date match (30% weight)
        date_score = 0
        if receipt["date"] and transaction.get("date"):
            days_diff = self._date_diff(receipt["date"], transaction["date"])
            date_score = max(0, 1 - (days_diff / 30))  # 30-day window
        
        # Merchant/description match (30% weight)
        desc_score = 0
        receipt_merchant = receipt.get("merchant", "").lower()
        txn_desc = transaction.get("description", "").lower()
        
        if receipt_merchant and txn_desc:
            # Simple keyword matching
            common_words = set(receipt_merchant.split()) & set(txn_desc.split())
            if common_words:
                desc_score = len(common_words) / max(len(receipt_merchant.split()), len(txn_desc.split()))
        
        if strategy == "strict":
            return 1.0 if amount_score > 0.95 and date_score > 0.9 else 0.0
        else:  # fuzzy_date_amount
            return (amount_score * 0.4 + date_score * 0.3 + desc_score * 0.3)

    def _date_diff(self, date1_str: str, date2_str: str) -> int:
        """Calculate absolute difference in days between two dates."""
        try:
            d1 = datetime.strptime(date1_str, "%Y-%m-%d")
            d2 = datetime.strptime(date2_str, "%Y-%m-%d")
            return abs((d1 - d2).days)
        except (ValueError, TypeError):
            return 30  # Default to max difference

    def _log(self, event: str, detail: Dict) -> None:
        """Append an entry to the processing audit log."""
        self.processing_log.append({
            "event": event,
            "detail": detail,
            "timestamp": datetime.now().isoformat()
        })