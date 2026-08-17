"""
Software Test Management System Environment API

A software test management system is a stateful environment designed to store,
organize, and retrieve information about test cases, executions, and results.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import csv
import io


DEFAULT_STATE: Dict[str, Any] = {
    "test_cases": {
        "TC001": {
            "_id": "TC001",
            "title": "Login with valid credentials",
            "description": "Verify user can login with valid username and password",
            "created_at": "2024-01-15T10:00:00",
            "updated_at": "2024-01-15T10:00:00",
            "author": "alice",
            "tags": ["login", "authentication", "smoke"],
            "precondition": "User account exists in the system",
            "steps": [
                "Navigate to login page",
                "Enter valid username",
                "Enter valid password",
                "Click login button"
            ],
            "expected_result": "User is redirected to dashboard"
        },
        "TC002": {
            "_id": "TC002",
            "title": "Login with invalid password",
            "description": "Verify error message when invalid password is entered",
            "created_at": "2024-01-15T11:00:00",
            "updated_at": "2024-01-15T11:00:00",
            "author": "alice",
            "tags": ["login", "authentication", "negative"],
            "precondition": "User account exists in the system",
            "steps": [
                "Navigate to login page",
                "Enter valid username",
                "Enter invalid password",
                "Click login button"
            ],
            "expected_result": "Error message displayed: Invalid credentials"
        },
        "TC003": {
            "_id": "TC003",
            "title": "Create new user account",
            "description": "Verify admin can create a new user account",
            "created_at": "2024-01-16T09:00:00",
            "updated_at": "2024-01-16T09:00:00",
            "author": "bob",
            "tags": ["user_management", "admin", "smoke"],
            "precondition": "Admin is logged in",
            "steps": [
                "Navigate to user management",
                "Click create user button",
                "Fill in user details",
                "Click save"
            ],
            "expected_result": "New user account is created and visible in user list"
        },
        "TC004": {
            "_id": "TC004",
            "title": "Search products by keyword",
            "description": "Verify search functionality returns relevant products",
            "created_at": "2024-01-17T14:00:00",
            "updated_at": "2024-01-17T14:00:00",
            "author": "charlie",
            "tags": ["search", "products", "functional"],
            "precondition": "Products exist in the catalog",
            "steps": [
                "Navigate to search page",
                "Enter search keyword",
                "Click search button"
            ],
            "expected_result": "Relevant products are displayed in results"
        }
    },
    "test_executions": {
        "EX001": {
            "execution_id": "EX001",
            "test_id": "TC001",
            "execution_status": "Pass",
            "executed_at": "2024-01-20T10:30:00",
            "executor": "alice",
            "actual_result": "User successfully logged in and redirected to dashboard",
            "comments": "Test passed on first attempt",
            "environment": "staging"
        },
        "EX002": {
            "execution_id": "EX002",
            "test_id": "TC002",
            "execution_status": "Pass",
            "executed_at": "2024-01-20T11:00:00",
            "executor": "alice",
            "actual_result": "Error message displayed correctly",
            "comments": "",
            "environment": "staging"
        },
        "EX003": {
            "execution_id": "EX003",
            "test_id": "TC001",
            "execution_status": "Fail",
            "executed_at": "2024-01-21T09:00:00",
            "executor": "bob",
            "actual_result": "Login button not responding",
            "comments": "UI bug reported",
            "environment": "production"
        },
        "EX004": {
            "execution_id": "EX004",
            "test_id": "TC003",
            "execution_status": "Blocked",
            "executed_at": "2024-01-21T10:00:00",
            "executor": "charlie",
            "actual_result": "Could not access admin panel",
            "comments": "Permission issue",
            "environment": "staging"
        }
    },
    "test_suites": {
        "TS001": {
            "_id": "TS001",
            "name": "Login Test Suite",
            "description": "All tests related to login functionality",
            "test_ids": ["TC001", "TC002"],
            "created_at": "2024-01-15T12:00:00",
            "owner": "alice"
        },
        "TS002": {
            "_id": "TS002",
            "name": "Admin Functions Suite",
            "description": "Tests for administrative functions",
            "test_ids": ["TC003"],
            "created_at": "2024-01-16T10:00:00",
            "owner": "bob"
        },
        "TS003": {
            "_id": "TS003",
            "name": "Smoke Test Suite",
            "description": "Quick smoke tests for basic functionality",
            "test_ids": ["TC001", "TC003"],
            "created_at": "2024-01-17T08:00:00",
            "owner": "charlie"
        }
    },
    "current_user": "admin",
    "next_test_case_num": 5,
    "next_execution_num": 5,
    "next_suite_num": 4
}

VALID_EXECUTION_STATUSES = ["Pass", "Fail", "Blocked", "Skipped"]


class SoftwareTestManagementSystem:
    """
    A software test management system API for storing, organizing, and retrieving
    information about test cases, executions, and results.
    
    This environment supports operations like querying, filtering, and exporting
    test data in various formats, enabling QA teams to track software quality
    across releases.
    """
    
    def __init__(self) -> None:
        """
        Initialize the Software Test Management System with default state.
        
        Declares all state attributes and sets up the API description.
        
        Args:
            None
        
        Returns:
            None
        """
        self.test_cases: Dict[str, Dict[str, Any]] = {}
        self.test_executions: Dict[str, Dict[str, Any]] = {}
        self.test_suites: Dict[str, Dict[str, Any]] = {}
        self.current_user: str = ""
        self.next_test_case_num: int = 1
        self.next_execution_num: int = 1
        self.next_suite_num: int = 1
        
        self._api_description = (
            "A software test management system for storing, organizing, "
            "and retrieving test cases, executions, and results."
        )
    
    def _timestamp(self) -> str:
        """
        Generate a timestamp in ISO format.
        
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
            scenario: Dictionary containing initial state values.
            long_context: Flag for long context scenarios (unused but required).
        
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
        Get the current state of the environment.
        
        Returns a dictionary containing all internal state variables including
        test cases, test executions, test suites, and metadata.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary with the following keys:
                - test_cases: All test case records
                - test_executions: All test execution records
                - test_suites: All test suite records
                - current_user: The current active user
                - next_test_case_num: Counter for next test case ID
                - next_execution_num: Counter for next execution ID
                - next_suite_num: Counter for next suite ID
        """
        return {
            "test_cases": deepcopy(self.test_cases),
            "test_executions": deepcopy(self.test_executions),
            "test_suites": deepcopy(self.test_suites),
            "current_user": self.current_user,
            "next_test_case_num": self.next_test_case_num,
            "next_execution_num": self.next_execution_num,
            "next_suite_num": self.next_suite_num
        }
    
    # ========== QUERY OPERATIONS ==========
    
    def get_test_case_by_id(self, test_id: str) -> Dict[str, Any]:
        """
        Retrieve full details of a test case by its unique _id.
        
        Args:
            test_id: The unique identifier of the test case.
        
        Returns:
            Dict[str, Any]: The test case data if found, or an error dict
                           if the test case does not exist.
        """
        if test_id not in self.test_cases:
            return {"error": f"Test case with ID '{test_id}' not found"}
        return deepcopy(self.test_cases[test_id])
    
    def get_test_execution_by_id(self, execution_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific test execution record by execution_id.
        
        Args:
            execution_id: The unique identifier of the test execution.
        
        Returns:
            Dict[str, Any]: The test execution data if found, or an error dict
                           if the execution does not exist.
        """
        if execution_id not in self.test_executions:
            return {"error": f"Test execution with ID '{execution_id}' not found"}
        return deepcopy(self.test_executions[execution_id])
    
    def list_test_executions_by_test_id(self, test_id: str) -> Dict[str, Any]:
        """
        Retrieve all execution records associated with a given test case _id.
        
        Args:
            test_id: The unique identifier of the test case.
        
        Returns:
            Dict[str, Any]: A dictionary containing a list of executions for
                           the specified test case, or an error if the test
                           case does not exist.
        """
        if test_id not in self.test_cases:
            return {"error": f"Test case with ID '{test_id}' not found"}
        
        executions = [
            deepcopy(ex) for ex in self.test_executions.values()
            if ex["test_id"] == test_id
        ]
        return {"test_id": test_id, "executions": executions, "count": len(executions)}
    
    def get_test_suite_by_id(self, suite_id: str) -> Dict[str, Any]:
        """
        Retrieve a test suite by its unique _id, including associated test case IDs.
        
        Args:
            suite_id: The unique identifier of the test suite.
        
        Returns:
            Dict[str, Any]: The test suite data if found, or an error dict
                           if the suite does not exist.
        """
        if suite_id not in self.test_suites:
            return {"error": f"Test suite with ID '{suite_id}' not found"}
        return deepcopy(self.test_suites[suite_id])
    
    def list_all_test_cases(self) -> Dict[str, Any]:
        """
        Retrieve a list of all test cases in the system.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing a list of all test cases
                           and the total count.
        """
        test_cases = list(deepcopy(self.test_cases).values())
        return {"test_cases": test_cases, "count": len(test_cases)}
    
    def list_all_test_executions(self) -> Dict[str, Any]:
        """
        Retrieve all test execution records.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing a list of all test executions
                           and the total count.
        """
        executions = list(deepcopy(self.test_executions).values())
        return {"executions": executions, "count": len(executions)}
    
    def list_all_test_suites(self) -> Dict[str, Any]:
        """
        Retrieve a list of all test suites.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing a list of all test suites
                           and the total count.
        """
        suites = list(deepcopy(self.test_suites).values())
        return {"test_suites": suites, "count": len(suites)}
    
    def search_test_cases_by_tag(self, tag: str) -> Dict[str, Any]:
        """
        Find test cases that match a specific tag.
        
        Args:
            tag: The tag to search for.
        
        Returns:
            Dict[str, Any]: A dictionary containing matching test cases and count.
        """
        matching_cases = [
            deepcopy(tc) for tc in self.test_cases.values()
            if tag in tc.get("tags", [])
        ]
        return {"tag": tag, "test_cases": matching_cases, "count": len(matching_cases)}
    
    def search_test_cases_by_author(self, author: str) -> Dict[str, Any]:
        """
        Retrieve test cases created by a specific author.
        
        Args:
            author: The author name to search for.
        
        Returns:
            Dict[str, Any]: A dictionary containing test cases by the author.
        """
        matching_cases = [
            deepcopy(tc) for tc in self.test_cases.values()
            if tc.get("author") == author
        ]
        return {"author": author, "test_cases": matching_cases, "count": len(matching_cases)}
    
    def export_test_case_json(
        self, 
        test_id: str, 
        include_executions: bool = False
    ) -> Dict[str, Any]:
        """
        Export the data of a test case (and optionally its executions) in JSON format.
        
        Args:
            test_id: The unique identifier of the test case.
            include_executions: Whether to include execution records.
        
        Returns:
            Dict[str, Any]: A dictionary containing the JSON string export,
                           or an error if the test case is not found.
        """
        if test_id not in self.test_cases:
            return {"error": f"Test case with ID '{test_id}' not found"}
        
        export_data = deepcopy(self.test_cases[test_id])
        
        if include_executions:
            executions = [
                deepcopy(ex) for ex in self.test_executions.values()
                if ex["test_id"] == test_id
            ]
            export_data["executions"] = executions
        
        json_str = json.dumps(export_data, indent=2)
        return {"format": "json", "test_id": test_id, "data": json_str}
    
    def export_test_case_csv(
        self, 
        test_id: str, 
        include_executions: bool = False
    ) -> Dict[str, Any]:
        """
        Export the data of a test case (and optionally its executions) in CSV format.
        
        Args:
            test_id: The unique identifier of the test case.
            include_executions: Whether to include execution records.
        
        Returns:
            Dict[str, Any]: A dictionary containing the CSV string export,
                           or an error if the test case is not found.
        """
        if test_id not in self.test_cases:
            return {"error": f"Test case with ID '{test_id}' not found"}
        
        tc = self.test_cases[test_id]
        output = io.StringIO()
        
        # Export test case
        tc_fields = ["_id", "title", "description", "created_at", "updated_at", 
                     "author", "tags", "precondition", "steps", "expected_result"]
        writer = csv.DictWriter(output, fieldnames=tc_fields)
        writer.writeheader()
        
        row = {k: tc.get(k, "") for k in tc_fields}
        row["tags"] = ";".join(tc.get("tags", []))
        row["steps"] = ";".join(tc.get("steps", []))
        writer.writerow(row)
        
        csv_data = output.getvalue()
        
        if include_executions:
            output_ex = io.StringIO()
            ex_fields = ["execution_id", "test_id", "execution_status", "executed_at",
                        "executor", "actual_result", "comments", "environment"]
            writer_ex = csv.DictWriter(output_ex, fieldnames=ex_fields)
            writer_ex.writeheader()
            
            for ex in self.test_executions.values():
                if ex["test_id"] == test_id:
                    writer_ex.writerow({k: ex.get(k, "") for k in ex_fields})
            
            csv_data += "\n--- Executions ---\n" + output_ex.getvalue()
        
        return {"format": "csv", "test_id": test_id, "data": csv_data}
    
    def get_test_case_summary(self, test_id: str) -> Dict[str, Any]:
        """
        Retrieve a summary of a test case including latest execution status and metadata.
        
        Args:
            test_id: The unique identifier of the test case.
        
        Returns:
            Dict[str, Any]: A summary dictionary with test case info and
                           latest execution status, or an error if not found.
        """
        if test_id not in self.test_cases:
            return {"error": f"Test case with ID '{test_id}' not found"}
        
        tc = self.test_cases[test_id]
        
        # Find executions for this test case
        executions = [
            ex for ex in self.test_executions.values()
            if ex["test_id"] == test_id
        ]
        
        latest_execution = None
        latest_status = "Not Executed"
        total_executions = len(executions)
        pass_count = sum(1 for ex in executions if ex["execution_status"] == "Pass")
        fail_count = sum(1 for ex in executions if ex["execution_status"] == "Fail")
        
        if executions:
            # Sort by executed_at to find the latest
            sorted_executions = sorted(executions, key=lambda x: x["executed_at"], reverse=True)
            latest_execution = sorted_executions[0]
            latest_status = latest_execution["execution_status"]
        
        return {
            "_id": tc["_id"],
            "title": tc["title"],
            "author": tc["author"],
            "tags": tc["tags"],
            "created_at": tc["created_at"],
            "latest_status": latest_status,
            "total_executions": total_executions,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "latest_execution": deepcopy(latest_execution) if latest_execution else None
        }
    
    # ========== STATE CHANGE OPERATIONS ==========
    
    def create_test_case(
        self,
        title: str,
        description: str,
        author: str,
        tags: Optional[List[str]] = None,
        precondition: str = "",
        steps: Optional[List[str]] = None,
        expected_result: str = ""
    ) -> Dict[str, Any]:
        """
        Add a new test case to the system with all required metadata.
        
        Args:
            title: The title of the test case.
            description: Detailed description of the test case.
            author: The author creating the test case.
            tags: Optional list of tags for categorization.
            precondition: Optional preconditions for the test.
            steps: Optional list of test steps.
            expected_result: Expected outcome of the test.
        
        Returns:
            Dict[str, Any]: The created test case data with its new ID,
                           or an error if validation fails.
        """
        if not title or not title.strip():
            return {"error": "Test case title is required"}
        if not description or not description.strip():
            return {"error": "Test case description is required"}
        if not author or not author.strip():
            return {"error": "Test case author is required"}
        
        # Generate unique ID
        test_id = f"TC{self.next_test_case_num:03d}"
        while test_id in self.test_cases:
            self.next_test_case_num += 1
            test_id = f"TC{self.next_test_case_num:03d}"
        
        timestamp = self._timestamp()
        
        new_test_case = {
            "_id": test_id,
            "title": title.strip(),
            "description": description.strip(),
            "created_at": timestamp,
            "updated_at": timestamp,
            "author": author.strip(),
            "tags": tags if tags else [],
            "precondition": precondition,
            "steps": steps if steps else [],
            "expected_result": expected_result
        }
        
        self.test_cases[test_id] = new_test_case
        self.next_test_case_num += 1
        
        return {"success": True, "test_case": deepcopy(new_test_case)}
    
    def create_test_execution(
        self,
        test_id: str,
        execution_status: str,
        executor: str,
        actual_result: str = "",
        comments: str = "",
        environment: str = ""
    ) -> Dict[str, Any]:
        """
        Record a new test execution for an existing test case.
        
        Args:
            test_id: The ID of the test case being executed.
            execution_status: Status of the execution (Pass/Fail/Blocked/Skipped).
            executor: The person running the test.
            actual_result: The actual outcome observed.
            comments: Optional comments about the execution.
            environment: The environment where the test was run.
        
        Returns:
            Dict[str, Any]: The created execution record, or an error if
                           validation fails.
        """
        # Validate test_id exists
        if test_id not in self.test_cases:
            return {"error": f"Test case with ID '{test_id}' not found"}
        
        # Validate execution_status
        if execution_status not in VALID_EXECUTION_STATUSES:
            return {
                "error": f"Invalid execution status '{execution_status}'. "
                        f"Must be one of: {', '.join(VALID_EXECUTION_STATUSES)}"
            }
        
        if not executor or not executor.strip():
            return {"error": "Executor is required"}
        
        # Generate unique execution ID
        execution_id = f"EX{self.next_execution_num:03d}"
        while execution_id in self.test_executions:
            self.next_execution_num += 1
            execution_id = f"EX{self.next_execution_num:03d}"
        
        new_execution = {
            "execution_id": execution_id,
            "test_id": test_id,
            "execution_status": execution_status,
            "executed_at": self._timestamp(),
            "executor": executor.strip(),
            "actual_result": actual_result,
            "comments": comments,
            "environment": environment
        }
        
        self.test_executions[execution_id] = new_execution
        self.next_execution_num += 1
        
        return {"success": True, "execution": deepcopy(new_execution)}
    
    def update_test_execution(
        self,
        execution_id: str,
        execution_status: Optional[str] = None,
        actual_result: Optional[str] = None,
        comments: Optional[str] = None,
        environment: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update an existing test execution (e.g., after a re-run).
        
        Args:
            execution_id: The ID of the execution to update.
            execution_status: Optional new status.
            actual_result: Optional new actual result.
            comments: Optional new comments.
            environment: Optional new environment.
        
        Returns:
            Dict[str, Any]: The updated execution record, or an error if
                           validation fails.
        """
        if execution_id not in self.test_executions:
            return {"error": f"Test execution with ID '{execution_id}' not found"}
        
        if execution_status is not None and execution_status not in VALID_EXECUTION_STATUSES:
            return {
                "error": f"Invalid execution status '{execution_status}'. "
                        f"Must be one of: {', '.join(VALID_EXECUTION_STATUSES)}"
            }
        
        execution = self.test_executions[execution_id]
        
        if execution_status is not None:
            execution["execution_status"] = execution_status
        if actual_result is not None:
            execution["actual_result"] = actual_result
        if comments is not None:
            execution["comments"] = comments
        if environment is not None:
            execution["environment"] = environment
        
        # Update timestamp for re-run
        execution["executed_at"] = self._timestamp()
        
        return {"success": True, "execution": deepcopy(execution)}
    
    def create_test_suite(
        self,
        name: str,
        description: str,
        owner: str,
        test_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a new test suite and associate it with existing test case IDs.
        
        Args:
            name: The name of the test suite.
            description: Description of the suite's purpose.
            owner: The owner of the test suite.
            test_ids: Optional list of test case IDs to include.
        
        Returns:
            Dict[str, Any]: The created test suite, or an error if validation fails.
        """
        if not name or not name.strip():
            return {"error": "Test suite name is required"}
        if not owner or not owner.strip():
            return {"error": "Test suite owner is required"}
        
        # Validate all test_ids exist
        test_ids = test_ids if test_ids else []
        for tid in test_ids:
            if tid not in self.test_cases:
                return {"error": f"Test case with ID '{tid}' not found"}
        
        # Generate unique suite ID
        suite_id = f"TS{self.next_suite_num:03d}"
        while suite_id in self.test_suites:
            self.next_suite_num += 1
            suite_id = f"TS{self.next_suite_num:03d}"
        
        new_suite = {
            "_id": suite_id,
            "name": name.strip(),
            "description": description,
            "test_ids": list(test_ids),
            "created_at": self._timestamp(),
            "owner": owner.strip()
        }
        
        self.test_suites[suite_id] = new_suite
        self.next_suite_num += 1
        
        return {"success": True, "test_suite": deepcopy(new_suite)}
    
    def add_test_case_to_suite(self, suite_id: str, test_id: str) -> Dict[str, Any]:
        """
        Add an existing test case to a specified test suite.
        
        Args:
            suite_id: The ID of the test suite.
            test_id: The ID of the test case to add.
        
        Returns:
            Dict[str, Any]: The updated test suite, or an error if validation fails.
        """
        if suite_id not in self.test_suites:
            return {"error": f"Test suite with ID '{suite_id}' not found"}
        if test_id not in self.test_cases:
            return {"error": f"Test case with ID '{test_id}' not found"}
        
        suite = self.test_suites[suite_id]
        
        if test_id in suite["test_ids"]:
            return {"error": f"Test case '{test_id}' is already in suite '{suite_id}'"}
        
        suite["test_ids"].append(test_id)
        
        return {"success": True, "test_suite": deepcopy(suite)}
    
    def remove_test_case_from_suite(self, suite_id: str, test_id: str) -> Dict[str, Any]:
        """
        Remove a test case from a test suite without deleting the test case itself.
        
        Args:
            suite_id: The ID of the test suite.
            test_id: The ID of the test case to remove.
        
        Returns:
            Dict[str, Any]: The updated test suite, or an error if validation fails.
        """
        if suite_id not in self.test_suites:
            return {"error": f"Test suite with ID '{suite_id}' not found"}
        
        suite = self.test_suites[suite_id]
        
        if test_id not in suite["test_ids"]:
            return {"error": f"Test case '{test_id}' is not in suite '{suite_id}'"}
        
        suite["test_ids"].remove(test_id)
        
        return {"success": True, "test_suite": deepcopy(suite)}


__TEST_CASES__ = [
    {
        "name": "Create and execute test case workflow",
        "steps": [
            {"tool_call": "create_test_case(title='API endpoint test', description='Test REST API response', author='tester1', tags=['api', 'integration'])", "expect_success": True},
            {"tool_call": "create_test_execution(test_id='TC005', execution_status='Pass', executor='tester1', environment='staging')", "expect_success": True},
            {"tool_call": "get_test_case_summary(test_id='TC005')", "expect_success": True}
        ]
    },
    {
        "name": "Test suite management workflow",
        "steps": [
            {"tool_call": "create_test_suite(name='Regression Suite', description='Full regression tests', owner='qa_lead', test_ids=['TC001', 'TC002'])", "expect_success": True},
            {"tool_call": "add_test_case_to_suite(suite_id='TS004', test_id='TC003')", "expect_success": True},
            {"tool_call": "get_test_suite_by_id(suite_id='TS004')", "expect_success": True},
            {"tool_call": "remove_test_case_from_suite(suite_id='TS004', test_id='TC002')", "expect_success": True}
        ]
    },
    {
        "name": "Query and export test executions by status",
        "steps": [
            {"tool_call": "list_test_executions_by_status(status='Pass')", "expect_success": True},
            {"tool_call": "list_test_executions_by_status(status='Fail')", "expect_success": True},
            {"tool_call": "export_test_results(test_id='TC001', format='json')", "expect_success": True}
        ]
    },
    {
        "name": "Test case update and delete workflow",
        "steps": [
            {"tool_call": "create_test_case(title='Temp test', description='Temporary test case', author='tester2', tags=['temp'])", "expect_success": True},
            {"tool_call": "update_test_case(test_id='TC005', title='Updated temp test', description='Updated description', tags=['temp', 'updated'])", "expect_success": True},
            {"tool_call": "delete_test_case(test_id='TC005')", "expect_success": True},
            {"tool_call": "get_test_case_by_id(test_id='TC005')", "expect_success": False}
        ]
    },
    {
        "name": "Error handling for invalid operations",
        "steps": [
            {"tool_call": "get_test_case_by_id(test_id='INVALID_ID')", "expect_success": False},
            {"tool_call": "create_test_execution(test_id='INVALID_ID', execution_status='Pass', executor='tester1', environment='staging')", "expect_success": False},
            {"tool_call": "add_test_case_to_suite(suite_id='INVALID_SUITE', test_id='TC001')", "expect_success": False},
            {"tool_call": "update_test_case(test_id='INVALID_ID', title='New title')", "expect_success": False}
        ]
    },
    {
        "name": "Search and filter test cases",
        "steps": [
            {"tool_call": "search_test_cases_by_tag(tag='smoke')", "expect_success": True},
            {"tool_call": "search_test_cases_by_author(author='qa_engineer')", "expect_success": True},
            {"tool_call": "list_all_test_cases()", "expect_success": True}
        ]
    },
    {
        "name": "Test suite deletion workflow",
        "steps": [
            {"tool_call": "create_test_suite(name='Temp Suite', description='Temporary suite', owner='qa_lead', test_ids=['TC001'])", "expect_success": True},
            {"tool_call": "delete_test_suite(suite_id='TS004')", "expect_success": True},
            {"tool_call": "get_test_suite_by_id(suite_id='TS004')", "expect_success": False}
        ]
    },
    {
        "name": "Execution history and statistics",
        "steps": [
            {"tool_call": "get_test_execution_history(test_id='TC001')", "expect_success": True},
            {"tool_call": "get_test_statistics()", "expect_success": True},
            {"tool_call": "get_suite_execution_summary(suite_id='TS001')", "expect_success": True}
        ]
    }
]