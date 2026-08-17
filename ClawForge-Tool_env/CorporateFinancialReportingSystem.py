"""
Corporate Financial Reporting System Environment API

A corporate financial reporting system that stores and manages financial documents
such as income statements, balance sheets, and annual reports.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime


DEFAULT_STATE: Dict[str, Any] = {
    "financial_reports": [
        {
            "report_id": "RPT001",
            "report_type": "annual_report",
            "fiscal_period": "FP2023",
            "generation_date": "2024-01-15T10:00:00",
            "status": "final",
            "version": 1,
            "summary": "Annual financial report for fiscal year 2023 showing strong revenue growth.",
            "author_department": "Finance"
        },
        {
            "report_id": "RPT002",
            "report_type": "quarterly_report",
            "fiscal_period": "FP2024Q1",
            "generation_date": "2024-04-10T14:30:00",
            "status": "final",
            "version": 1,
            "summary": "Q1 2024 quarterly report with improved operating margins.",
            "author_department": "Finance"
        },
        {
            "report_id": "RPT003",
            "report_type": "quarterly_report",
            "fiscal_period": "FP2024Q2",
            "generation_date": "2024-07-05T09:00:00",
            "status": "draft",
            "version": 1,
            "summary": "Q2 2024 draft report pending review.",
            "author_department": "Accounting"
        },
        {
            "report_id": "RPT004",
            "report_type": "income_statement",
            "fiscal_period": "FP2024Q1",
            "generation_date": "2024-04-08T11:00:00",
            "status": "final",
            "version": 2,
            "summary": "Revised Q1 2024 income statement.",
            "author_department": "Finance"
        }
    ],
    "financial_statements": [
        {
            "statement_id": "STMT001",
            "report_id": "RPT001",
            "statement_type": "income",
            "line_items": ["LI001", "LI002", "LI003"]
        },
        {
            "statement_id": "STMT002",
            "report_id": "RPT001",
            "statement_type": "balance_sheet",
            "line_items": ["LI004", "LI005"]
        },
        {
            "statement_id": "STMT003",
            "report_id": "RPT002",
            "statement_type": "income",
            "line_items": ["LI006", "LI007"]
        },
        {
            "statement_id": "STMT004",
            "report_id": "RPT003",
            "statement_type": "cash_flow",
            "line_items": ["LI008"]
        }
    ],
    "line_items": [
        {
            "item_id": "LI001",
            "statement_id": "STMT001",
            "category": "revenue",
            "value": 5000000.00,
            "currency": "USD",
            "time_period": "FP2023"
        },
        {
            "item_id": "LI002",
            "statement_id": "STMT001",
            "category": "operating_expense",
            "value": 3200000.00,
            "currency": "USD",
            "time_period": "FP2023"
        },
        {
            "item_id": "LI003",
            "statement_id": "STMT001",
            "category": "net_income",
            "value": 1800000.00,
            "currency": "USD",
            "time_period": "FP2023"
        },
        {
            "item_id": "LI004",
            "statement_id": "STMT002",
            "category": "assets",
            "value": 12000000.00,
            "currency": "USD",
            "time_period": "FP2023"
        },
        {
            "item_id": "LI005",
            "statement_id": "STMT002",
            "category": "liabilities",
            "value": 4500000.00,
            "currency": "USD",
            "time_period": "FP2023"
        },
        {
            "item_id": "LI006",
            "statement_id": "STMT003",
            "category": "revenue",
            "value": 1500000.00,
            "currency": "USD",
            "time_period": "FP2024Q1"
        },
        {
            "item_id": "LI007",
            "statement_id": "STMT003",
            "category": "operating_expense",
            "value": 900000.00,
            "currency": "EUR",
            "time_period": "FP2024Q1"
        },
        {
            "item_id": "LI008",
            "statement_id": "STMT004",
            "category": "cash_flow_operations",
            "value": 750000.00,
            "currency": "USD",
            "time_period": "FP2024Q2"
        }
    ],
    "fiscal_periods": [
        {
            "period_id": "FP2023",
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "period_type": "annual",
            "is_closed": True
        },
        {
            "period_id": "FP2024Q1",
            "start_date": "2024-01-01",
            "end_date": "2024-03-31",
            "period_type": "quarterly",
            "is_closed": True
        },
        {
            "period_id": "FP2024Q2",
            "start_date": "2024-04-01",
            "end_date": "2024-06-30",
            "period_type": "quarterly",
            "is_closed": False
        },
        {
            "period_id": "FP2024Q3",
            "start_date": "2024-07-01",
            "end_date": "2024-09-30",
            "period_type": "quarterly",
            "is_closed": False
        }
    ],
    "current_user": "finance_admin",
    "next_report_id": 5,
    "next_statement_id": 5,
    "next_line_item_id": 9
}


class CorporateFinancialReportingSystem:
    """
    A corporate financial reporting system environment that manages financial documents
    including income statements, balance sheets, and annual reports.
    
    This system maintains historical records organized by time periods and supports
    operations like retrieval, validation, and summarization for internal decision-making,
    regulatory compliance, and external communication with stakeholders.
    """

    def __init__(self) -> None:
        """
        Initialize the Corporate Financial Reporting System.
        
        Declares all state attributes with type hints and sets up the API description.
        
        Args:
            None
        
        Returns:
            None
        """
        self.financial_reports: List[Dict[str, Any]] = []
        self.financial_statements: List[Dict[str, Any]] = []
        self.line_items: List[Dict[str, Any]] = []
        self.fiscal_periods: List[Dict[str, Any]] = []
        self.current_user: str = ""
        self.next_report_id: int = 1
        self.next_statement_id: int = 1
        self.next_line_item_id: int = 1
        
        self._api_description: str = (
            "Corporate financial reporting system for managing financial documents "
            "such as income statements, balance sheets, and annual reports with "
            "period-based organization and compliance validation."
        )

    def _timestamp(self) -> str:
        """
        Generate a unified ISO format timestamp string.
        
        Args:
            None
        
        Returns:
            str: Current timestamp in ISO format (YYYY-MM-DDTHH:MM:SS).
        """
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: Dictionary containing the initial state to load.
            long_context: Flag for long context scenarios (unused in base implementation).
        
        Returns:
            None
        """
        if not scenario:
            scenario = {}
        for key in DEFAULT_STATE:
            if key in scenario:
                setattr(self, key, deepcopy(scenario[key]))
            else:
                setattr(self, key, deepcopy(DEFAULT_STATE[key]))

    def get_env_state(self) -> Dict[str, Any]:
        """
        Return the current environment state as a dictionary.
        
        Provides a complete snapshot of all internal state variables for
        inspection, debugging, or state persistence.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Dictionary containing all current state variables including:
                - financial_reports: List of all financial report records
                - financial_statements: List of all financial statement records
                - line_items: List of all line item records
                - fiscal_periods: List of all fiscal period records
                - current_user: Currently active user identifier
                - next_report_id: Counter for generating new report IDs
                - next_statement_id: Counter for generating new statement IDs
                - next_line_item_id: Counter for generating new line item IDs
        """
        return {
            "financial_reports": deepcopy(self.financial_reports),
            "financial_statements": deepcopy(self.financial_statements),
            "line_items": deepcopy(self.line_items),
            "fiscal_periods": deepcopy(self.fiscal_periods),
            "current_user": self.current_user,
            "next_report_id": self.next_report_id,
            "next_statement_id": self.next_statement_id,
            "next_line_item_id": self.next_line_item_id
        }

    # ==================== Query Operations ====================

    def get_all_finalized_reports(self) -> Dict[str, Any]:
        """
        Retrieve all financial reports with status 'final'.
        
        These reports are suitable for external communication as per constraint rules.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - reports: List of finalized report records
                - count: Number of finalized reports found
        """
        finalized = [r for r in self.financial_reports if r.get("status") == "final"]
        return {
            "reports": deepcopy(finalized),
            "count": len(finalized)
        }

    def get_latest_finalized_report(self) -> Dict[str, Any]:
        """
        Identify and return the most recent finalized report based on generation_date.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - report: The latest finalized report record, or None if no finalized reports exist
                - found: Boolean indicating if a finalized report was found
        """
        finalized = [r for r in self.financial_reports if r.get("status") == "final"]
        if not finalized:
            return {"report": None, "found": False}
        
        latest = max(finalized, key=lambda x: x.get("generation_date", ""))
        return {"report": deepcopy(latest), "found": True}

    def get_report_summary(self, report_id: str) -> Dict[str, Any]:
        """
        Retrieve the summary text of a given financial report.
        
        Args:
            report_id: The unique identifier of the report.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - report_id: The report identifier
                - summary: The report summary text, or
                - error: Error message if report not found
        """
        for report in self.financial_reports:
            if report.get("report_id") == report_id:
                return {
                    "report_id": report_id,
                    "summary": report.get("summary", "")
                }
        return {"error": f"Report with ID '{report_id}' not found"}

    def get_report_by_id(self, report_id: str) -> Dict[str, Any]:
        """
        Fetch full details of a financial report by its report_id.
        
        Args:
            report_id: The unique identifier of the report.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - report: The complete report record, or
                - error: Error message if report not found
        """
        for report in self.financial_reports:
            if report.get("report_id") == report_id:
                return {"report": deepcopy(report)}
        return {"error": f"Report with ID '{report_id}' not found"}

    def list_reports_by_fiscal_period(self, period_id: str) -> Dict[str, Any]:
        """
        Retrieve all reports associated with a specific fiscal period.
        
        Args:
            period_id: The unique identifier of the fiscal period.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - reports: List of reports for the specified period
                - count: Number of reports found
                - period_id: The queried period ID, or
                - error: Error message if fiscal period not found
        """
        period_exists = any(p.get("period_id") == period_id for p in self.fiscal_periods)
        if not period_exists:
            return {"error": f"Fiscal period '{period_id}' not found"}
        
        reports = [r for r in self.financial_reports if r.get("fiscal_period") == period_id]
        return {
            "reports": deepcopy(reports),
            "count": len(reports),
            "period_id": period_id
        }

    def list_reports_by_type(self, report_type: str) -> Dict[str, Any]:
        """
        Retrieve all reports of a specific type.
        
        Args:
            report_type: The type of report to filter by (e.g., 'annual_report', 'quarterly_report').
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - reports: List of reports matching the type
                - count: Number of reports found
                - report_type: The queried report type
        """
        reports = [r for r in self.financial_reports if r.get("report_type") == report_type]
        return {
            "reports": deepcopy(reports),
            "count": len(reports),
            "report_type": report_type
        }

    def get_report_statements(self, report_id: str) -> Dict[str, Any]:
        """
        List all financial statements linked to a report.
        
        Args:
            report_id: The unique identifier of the report.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - report_id: The report identifier
                - statements: List of financial statement records
                - count: Number of statements found, or
                - error: Error message if report not found
        """
        report_exists = any(r.get("report_id") == report_id for r in self.financial_reports)
        if not report_exists:
            return {"error": f"Report with ID '{report_id}' not found"}
        
        statements = [s for s in self.financial_statements if s.get("report_id") == report_id]
        return {
            "report_id": report_id,
            "statements": deepcopy(statements),
            "count": len(statements)
        }

    def get_statement_line_items(self, statement_id: str) -> Dict[str, Any]:
        """
        Retrieve detailed line items within a financial statement.
        
        Args:
            statement_id: The unique identifier of the financial statement.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - statement_id: The statement identifier
                - line_items: List of line item records
                - count: Number of line items found, or
                - error: Error message if statement not found
        """
        statement_exists = any(s.get("statement_id") == statement_id for s in self.financial_statements)
        if not statement_exists:
            return {"error": f"Statement with ID '{statement_id}' not found"}
        
        items = [li for li in self.line_items if li.get("statement_id") == statement_id]
        return {
            "statement_id": statement_id,
            "line_items": deepcopy(items),
            "count": len(items)
        }

    def get_fiscal_period_by_id(self, period_id: str) -> Dict[str, Any]:
        """
        Retrieve fiscal period details including start/end dates and closure status.
        
        Args:
            period_id: The unique identifier of the fiscal period.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - period: The fiscal period record, or
                - error: Error message if period not found
        """
        for period in self.fiscal_periods:
            if period.get("period_id") == period_id:
                return {"period": deepcopy(period)}
        return {"error": f"Fiscal period '{period_id}' not found"}

    def is_fiscal_period_closed(self, period_id: str) -> Dict[str, Any]:
        """
        Check whether a given fiscal period is closed.
        
        A closed fiscal period is a prerequisite for finalizing reports.
        
        Args:
            period_id: The unique identifier of the fiscal period.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - period_id: The queried period ID
                - is_closed: Boolean indicating closure status, or
                - error: Error message if period not found
        """
        for period in self.fiscal_periods:
            if period.get("period_id") == period_id:
                return {
                    "period_id": period_id,
                    "is_closed": period.get("is_closed", False)
                }
        return {"error": f"Fiscal period '{period_id}' not found"}

    def validate_statement_period_alignment(self, report_id: str) -> Dict[str, Any]:
        """
        Verify that all statements in a report correspond to the report's fiscal period.
        
        Args:
            report_id: The unique identifier of the report to validate.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - report_id: The validated report ID
                - is_valid: Boolean indicating if all statements align
                - misaligned_items: List of misaligned line items (if any), or
                - error: Error message if report not found
        """
        report = None
        for r in self.financial_reports:
            if r.get("report_id") == report_id:
                report = r
                break
        
        if not report:
            return {"error": f"Report with ID '{report_id}' not found"}
        
        report_period = report.get("fiscal_period")
        statements = [s for s in self.financial_statements if s.get("report_id") == report_id]
        
        misaligned = []
        for stmt in statements:
            stmt_id = stmt.get("statement_id")
            items = [li for li in self.line_items if li.get("statement_id") == stmt_id]
            for item in items:
                if item.get("time_period") != report_period:
                    misaligned.append({
                        "item_id": item.get("item_id"),
                        "statement_id": stmt_id,
                        "item_period": item.get("time_period"),
                        "report_period": report_period
                    })
        
        return {
            "report_id": report_id,
            "is_valid": len(misaligned) == 0,
            "misaligned_items": misaligned
        }

    def list_all_currencies_used(self) -> Dict[str, Any]:
        """
        Retrieve all currencies present in line items.
        
        Ensures compliance with monetary recording rules that all values must have
        a specified currency.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - currencies: List of unique currency codes used
                - count: Number of unique currencies
        """
        currencies = set()
        for item in self.line_items:
            currency = item.get("currency")
            if currency:
                currencies.add(currency)
        
        return {
            "currencies": sorted(list(currencies)),
            "count": len(currencies)
        }

    # ==================== State Change Operations ====================

    def create_draft_report(
        self,
        report_type: str,
        fiscal_period: str,
        author_department: str,
        summary: str = ""
    ) -> Dict[str, Any]:
        """
        Initialize a new financial report with status 'draft'.
        
        Args:
            report_type: Type of report (e.g., 'annual_report', 'quarterly_report').
            fiscal_period: The fiscal period ID this report covers.
            author_department: The department creating the report.
            summary: Optional initial summary text.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - report: The newly created report record
                - success: Boolean indicating success, or
                - error: Error message if fiscal period not found
        """
        period_exists = any(p.get("period_id") == fiscal_period for p in self.fiscal_periods)
        if not period_exists:
            return {"error": f"Fiscal period '{fiscal_period}' not found"}
        
        new_report_id = f"RPT{self.next_report_id:03d}"
        self.next_report_id += 1
        
        new_report = {
            "report_id": new_report_id,
            "report_type": report_type,
            "fiscal_period": fiscal_period,
            "generation_date": self._timestamp(),
            "status": "draft",
            "version": 1,
            "summary": summary,
            "author_department": author_department
        }
        
        self.financial_reports.append(new_report)
        return {"report": deepcopy(new_report), "success": True}

    def update_report_summary(self, report_id: str, summary: str) -> Dict[str, Any]:
        """
        Modify the summary field of a draft report.
        
        Args:
            report_id: The unique identifier of the report to update.
            summary: The new summary text.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - report: The updated report record
                - success: Boolean indicating success, or
                - error: Error message if report not found or not a draft
        """
        for report in self.financial_reports:
            if report.get("report_id") == report_id:
                if report.get("status") != "draft":
                    return {"error": f"Cannot update summary of non-draft report '{report_id}'"}
                
                report["summary"] = summary
                return {"report": deepcopy(report), "success": True}
        
        return {"error": f"Report with ID '{report_id}' not found"}

    def finalize_report(self, report_id: str) -> Dict[str, Any]:
        """
        Change report status from 'draft' to 'final'.
        
        Only succeeds if the fiscal period is closed and data is valid (all statements
        align with the report's fiscal period).
        
        Args:
            report_id: The unique identifier of the report to finalize.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - report: The finalized report record
                - success: Boolean indicating success, or
                - error: Error message if validation fails
        """
        report = None
        for r in self.financial_reports:
            if r.get("report_id") == report_id:
                report = r
                break
        
        if not report:
            return {"error": f"Report with ID '{report_id}' not found"}
        
        if report.get("status") != "draft":
            return {"error": f"Report '{report_id}' is not in draft status"}
        
        # Check if fiscal period is closed
        fiscal_period = report.get("fiscal_period")
        period_closed = False
        for period in self.fiscal_periods:
            if period.get("period_id") == fiscal_period:
                period_closed = period.get("is_closed", False)
                break
        
        if not period_closed:
            return {"error": f"Cannot finalize report: fiscal period '{fiscal_period}' is not closed"}
        
        # Validate statement period alignment
        validation = self.validate_statement_period_alignment(report_id)
        if not validation.get("is_valid", True):
            return {"error": "Cannot finalize report: statements do not align with report's fiscal period"}
        
        report["status"] = "final"
        report["generation_date"] = self._timestamp()
        return {"report": deepcopy(report), "success": True}

    def reopen_report(self, report_id: str) -> Dict[str, Any]:
        """
        Revert a finalized report back to 'draft' status for corrections.
        
        Args:
            report_id: The unique identifier of the report to reopen.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - report: The reopened report record
                - success: Boolean indicating success, or
                - error: Error message if report not found or not final
        """
        for report in self.financial_reports:
            if report.get("report_id") == report_id:
                if report.get("status") != "final":
                    return {"error": f"Report '{report_id}' is not finalized, cannot reopen"}
                
                report["status"] = "draft"
                return {"report": deepcopy(report), "success": True}
        
        return {"error": f"Report with ID '{report_id}' not found"}

    def generate_report_version(self, report_id: str) -> Dict[str, Any]:
        """
        Create a new version of an existing report, incrementing the version number.
        
        Creates a new draft report based on the existing report with an incremented version.
        
        Args:
            report_id: The unique identifier of the report to version.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - original_report: The original report record
                - new_report: The new versioned report record
                - success: Boolean indicating success, or
                - error: Error message if report not found
        """
        original = None
        for report in self.financial_reports:
            if report.get("report_id") == report_id:
                original = report
                break
        
        if not original:
            return {"error": f"Report with ID '{report_id}' not found"}
        
        new_report_id = f"RPT{self.next_report_id:03d}"
        self.next_report_id += 1
        
        new_report = {
            "report_id": new_report_id,
            "report_type": original.get("report_type"),
            "fiscal_period": original.get("fiscal_period"),
            "generation_date": self._timestamp(),
            "status": "draft",
            "version": original.get("version", 1) + 1,
            "summary": original.get("summary", ""),
            "author_department": original.get("author_department")
        }
        
        self.financial_reports.append(new_report)
        return {
            "original_report": deepcopy(original),
            "new_report": deepcopy(new_report),
            "success": True
        }

    def close_fiscal_period(self, period_id: str) -> Dict[str, Any]:
        """
        Mark a fiscal period as closed, enabling final report generation.
        
        Args:
            period_id: The unique identifier of the fiscal period to close.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - period: The updated fiscal period record
                - success: Boolean indicating success, or
                - error: Error message if period not found or already closed
        """
        for period in self.fiscal_periods:
            if period.get("period_id") == period_id:
                if period.get("is_closed"):
                    return {"error": f"Fiscal period '{period_id}' is already closed"}
                
                period["is_closed"] = True
                return {"period": deepcopy(period), "success": True}
        
        return {"error": f"Fiscal period '{period_id}' not found"}

    def add_statement_to_report(
        self,
        report_id: str,
        statement_type: str
    ) -> Dict[str, Any]:
        """
        Attach a new financial statement to a draft report.
        
        Args:
            report_id: The unique identifier of the report.
            statement_type: Type of statement ('income', 'balance_sheet', 'cash_flow').
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - statement: The newly created statement record
                - success: Boolean indicating success, or
                - error: Error message if report not found or not a draft
        """
        valid_types = ["income", "balance_sheet", "cash_flow"]
        if statement_type not in valid_types:
            return {"error": f"Invalid statement type '{statement_type}'. Must be one of: {valid_types}"}
        
        report = None
        for r in self.financial_reports:
            if r.get("report_id") == report_id:
                report = r
                break
        
        if not report:
            return {"error": f"Report with ID '{report_id}' not found"}
        
        if report.get("status") != "draft":
            return {"error": f"Cannot add statement to non-draft report '{report_id}'"}
        
        new_statement_id = f"STMT{self.next_statement_id:03d}"
        self.next_statement_id += 1
        
        new_statement = {
            "statement_id": new_statement_id,
            "report_id": report_id,
            "statement_type": statement_type,
            "line_items": []
        }
        
        self.financial_statements.append(new_statement)
        return {"statement": deepcopy(new_statement), "success": True}

    def add_line_item(
        self,
        statement_id: str,
        category: str,
        value: float,
        currency: str,
        time_period: str
    ) -> Dict[str, Any]:
        """
        Add a new line item to a financial statement.
        
        Args:
            statement_id: The unique identifier of the statement.
            category: The category of the line item (e.g., 'revenue', 'expense').
            value: The monetary value of the line item.
            currency: The currency code (e.g., 'USD', 'EUR').
            time_period: The fiscal period this line item applies to.
        
        Returns:
            Dict[str, Any]: Dictionary containing:
                - line_item: The newly created line item record
                - success: Boolean indicating success, or
                - error: Error message if statement not found
        """
        statement = None
        for s in self.financial_statements:
            if s.get("statement_id") == statement_id:
                statement = s
                break
        
        if not statement:
            return {"error": f"Statement with ID '{statement_id}' not found"}
        
        new_item_id = f"LI{self.next_line_item_id:03d}"
        self.next_line_item_id += 1
        
        new_line_item = {
            "item_id": new_item_id,
            "statement_id": statement_id,
            "category": category,
            "value": value,
            "currency": currency,
            "time_period": time_period
        }
        
        self.line_items.append(new_line_item)
        
        # Update statement's line_items list
        if "line_items" not in statement:
            statement["line_items"] = []
        statement["line_items"].append(new_item_id)
        
        return new_line_item
    
    def get_line_items(self, statement_id: str) -> list:
        """
        Get all line items for a specific financial statement.
        
        Args:
            statement_id: ID of the financial statement
            
        Returns:
            List of line items for the statement
        """
        return [item for item in self.line_items if item.get("statement_id") == statement_id]
    
    def calculate_total(self, statement_id: str, category: str = None) -> dict:
        """
        Calculate total value of line items for a statement.
        
        Args:
            statement_id: ID of the financial statement
            category: Optional category filter
            
        Returns:
            dict with total value and currency
        """
        items = self.get_line_items(statement_id)
        
        if category:
            items = [item for item in items if item.get("category") == category]
        
        if not items:
            return {"total": 0, "currency": "USD", "count": 0}
        
        total = sum(item.get("value", 0) for item in items)
        currency = items[0].get("currency", "USD") if items else "USD"
        
        return {"total": total, "currency": currency, "count": len(items)}
    
    def delete_statement(self, statement_id: str) -> dict:
        """
        Delete a financial statement and its associated line items.
        
        Args:
            statement_id: ID of the statement to delete
            
        Returns:
            dict with success status or error message
        """
        statement = None
        for s in self.financial_statements:
            if s.get("statement_id") == statement_id:
                statement = s
                break
        
        if not statement:
            return {"error": f"Statement with ID '{statement_id}' not found"}
        
        self.financial_statements.remove(statement)
        self.line_items = [item for item in self.line_items if item.get("statement_id") != statement_id]
        
        return {"success": True, "deleted_statement_id": statement_id}
    
    def get_statements_by_entity(self, entity_id: str) -> list:
        """
        Get all financial statements for a specific entity.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            List of financial statements for the entity
        """
        return [s for s in self.financial_statements if s.get("entity_id") == entity_id]
    
    def get_statements_by_type(self, statement_type: str) -> list:
        """
        Get all financial statements of a specific type.
        
        Args:
            statement_type: Type of statement (e.g., 'balance_sheet', 'income_statement')
            
        Returns:
            List of financial statements of the specified type
        """
        return [s for s in self.financial_statements if s.get("statement_type") == statement_type]


__TEST_CASES__ = [
    {
        "name": "test_create_financial_statement",
        "setup": "env = FinancialReportingEnvironment()",
        "action": "env.create_financial_statement('E001', 'balance_sheet', '2024-Q1')",
        "expected_keys": ["statement_id", "entity_id", "statement_type", "period"]
    },
    {
        "name": "test_add_line_item",
        "setup": "env = FinancialReportingEnvironment(); stmt = env.create_financial_statement('E001', 'income_statement', '2024-Q1')",
        "action": "env.add_line_item(stmt['statement_id'], 'revenue', 150000.00)",
        "expected_keys": ["item_id", "statement_id", "category", "value", "currency"]
    },
    {
        "name": "test_get_line_items",
        "setup": "env = FinancialReportingEnvironment(); stmt = env.create_financial_statement('E001', 'balance_sheet', '2024-Q1'); env.add_line_item(stmt['statement_id'], 'assets', 500000)",
        "action": "env.get_line_items(stmt['statement_id'])",
        "expected_type": "list"
    },
    {
        "name": "test_calculate_total",
        "setup": "env = FinancialReportingEnvironment(); stmt = env.create_financial_statement('E001', 'income_statement', '2024-Q1'); env.add_line_item(stmt['statement_id'], 'revenue', 100000); env.add_line_item(stmt['statement_id'], 'revenue', 50000)",
        "action": "env.calculate_total(stmt['statement_id'], 'revenue')",
        "expected_keys": ["total", "currency", "count"]
    },
    {
        "name": "test_delete_statement",
        "setup": "env = FinancialReportingEnvironment(); stmt = env.create_financial_statement('E001', 'balance_sheet', '2024-Q1')",
        "action": "env.delete_statement(stmt['statement_id'])",
        "expected_keys": ["success", "deleted_statement_id"]
    },
    {
        "name": "test_get_statements_by_entity",
        "setup": "env = FinancialReportingEnvironment(); env.create_financial_statement('E001', 'balance_sheet', '2024-Q1'); env.create_financial_statement('E001', 'income_statement', '2024-Q1')",
        "action": "env.get_statements_by_entity('E001')",
        "expected_type": "list"
    },
    {
        "name": "test_statement_not_found",
        "setup": "env = FinancialReportingEnvironment()",
        "action": "env.add_line_item('INVALID_ID', 'revenue', 1000)",
        "expected_keys": ["error"]
    }
]