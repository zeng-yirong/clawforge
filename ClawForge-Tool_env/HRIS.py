"""
Human Resources Information System (HRIS) Environment API

An HRIS is a centralized system used to manage and store employee data throughout 
their employment lifecycle. It maintains structured records including personal 
information, job titles, salaries, and employment status.
"""

from copy import deepcopy
from datetime import datetime
from typing import Dict, List, Optional, Any

DEFAULT_STATE: Dict[str, Any] = {
    "employees": {
        "EMP001": {
            "employee_id": "EMP001",
            "first_name": "John",
            "last_name": "Smith",
            "date_of_birth": "1985-03-15",
            "gender": "Male",
            "hire_date": "2020-01-15",
            "job_title": "Software Engineer",
            "department": "DEPT001",
            "manager_id": "EMP003",
            "employment_status": "active",
            "salary": 85000.00,
            "work_email": "john.smith@company.com",
            "phone_number": "+1-555-0101",
            "address": "123 Main St, New York, NY 10001"
        },
        "EMP002": {
            "employee_id": "EMP002",
            "first_name": "Sarah",
            "last_name": "Johnson",
            "date_of_birth": "1990-07-22",
            "gender": "Female",
            "hire_date": "2019-06-01",
            "job_title": "HR Specialist",
            "department": "DEPT002",
            "manager_id": "EMP004",
            "employment_status": "active",
            "salary": 65000.00,
            "work_email": "sarah.johnson@company.com",
            "phone_number": "+1-555-0102",
            "address": "456 Oak Ave, New York, NY 10002"
        },
        "EMP003": {
            "employee_id": "EMP003",
            "first_name": "Michael",
            "last_name": "Chen",
            "date_of_birth": "1978-11-08",
            "gender": "Male",
            "hire_date": "2015-03-20",
            "job_title": "Engineering Manager",
            "department": "DEPT001",
            "manager_id": None,
            "employment_status": "active",
            "salary": 120000.00,
            "work_email": "michael.chen@company.com",
            "phone_number": "+1-555-0103",
            "address": "789 Pine Rd, New York, NY 10003"
        },
        "EMP004": {
            "employee_id": "EMP004",
            "first_name": "Emily",
            "last_name": "Davis",
            "date_of_birth": "1982-05-30",
            "gender": "Female",
            "hire_date": "2016-09-12",
            "job_title": "HR Manager",
            "department": "DEPT002",
            "manager_id": None,
            "employment_status": "active",
            "salary": 95000.00,
            "work_email": "emily.davis@company.com",
            "phone_number": "+1-555-0104",
            "address": "321 Elm St, New York, NY 10004"
        },
        "EMP005": {
            "employee_id": "EMP005",
            "first_name": "Robert",
            "last_name": "Wilson",
            "date_of_birth": "1995-01-18",
            "gender": "Male",
            "hire_date": "2022-02-28",
            "job_title": "Junior Developer",
            "department": "DEPT001",
            "manager_id": "EMP003",
            "employment_status": "on_leave",
            "salary": 55000.00,
            "work_email": "robert.wilson@company.com",
            "phone_number": "+1-555-0105",
            "address": "654 Maple Dr, New York, NY 10005"
        }
    },
    "departments": {
        "DEPT001": {
            "department_id": "DEPT001",
            "department_name": "Engineering",
            "manager_id": "EMP003",
            "location": "Building A, Floor 3",
            "budget": 500000.0
        },
        "DEPT002": {
            "department_id": "DEPT002",
            "department_name": "Human Resources",
            "manager_id": "EMP004",
            "location": "Building B, Floor 1",
            "budget": 300000.0
        },
        "DEPT003": {
            "department_id": "DEPT003",
            "department_name": "Finance",
            "manager_id": None,
            "location": "Building A, Floor 2",
            "budget": 400000.0
        }
    },
    "job_positions": {
        "Software Engineer": {
            "job_title": "Software Engineer",
            "department_id": "DEPT001",
            "salary_range_min": 70000.00,
            "salary_range_max": 110000.00,
            "required_qualifications": "Bachelor's in Computer Science, 2+ years experience"
        },
        "Junior Developer": {
            "job_title": "Junior Developer",
            "department_id": "DEPT001",
            "salary_range_min": 45000.00,
            "salary_range_max": 65000.00,
            "required_qualifications": "Bachelor's in Computer Science or related field"
        },
        "Engineering Manager": {
            "job_title": "Engineering Manager",
            "department_id": "DEPT001",
            "salary_range_min": 100000.00,
            "salary_range_max": 150000.00,
            "required_qualifications": "Bachelor's in CS, 7+ years experience, 3+ years management"
        },
        "HR Specialist": {
            "job_title": "HR Specialist",
            "department_id": "DEPT002",
            "salary_range_min": 50000.00,
            "salary_range_max": 80000.00,
            "required_qualifications": "Bachelor's in HR or Business, 1+ years experience"
        },
        "HR Manager": {
            "job_title": "HR Manager",
            "department_id": "DEPT002",
            "salary_range_min": 80000.00,
            "salary_range_max": 120000.00,
            "required_qualifications": "Bachelor's in HR, 5+ years experience, 2+ years management"
        },
        "Financial Analyst": {
            "job_title": "Financial Analyst",
            "department_id": "DEPT003",
            "salary_range_min": 60000.00,
            "salary_range_max": 90000.00,
            "required_qualifications": "Bachelor's in Finance or Accounting, CPA preferred"
        }
    },
    "employment_statuses": {
        "active": {
            "status_type": "active",
            "description": "Employee is currently working and on payroll",
            "is_active": True
        },
        "on_leave": {
            "status_type": "on_leave",
            "description": "Employee is temporarily away (medical, personal, parental leave)",
            "is_active": True
        },
        "terminated": {
            "status_type": "terminated",
            "description": "Employee has been terminated or resigned",
            "is_active": False
        },
        "retired": {
            "status_type": "retired",
            "description": "Employee has retired from the organization",
            "is_active": False
        }
    },
    "current_user": {
        "user_id": "ADMIN001",
        "role": "hr_admin",
        "permissions": ["read", "write", "delete"]
    },
    "next_employee_id": 6,
    "audit_log": []
}


class HRISEnvironment:
    """
    Human Resources Information System (HRIS) Environment API.
    
    This class provides a comprehensive API for managing employee data throughout
    their employment lifecycle, including personal information, job assignments,
    salary management, and employment status tracking.
    """
    
    def __init__(self) -> None:
        """
        Initialize the HRIS environment with default state attributes.
        
        Returns:
            None
        """
        self._api_description: str = "HRIS API for managing employee records, departments, job positions, and employment lifecycle operations."
        
        self.employees: Dict[str, Dict[str, Any]] = {}
        self.departments: Dict[str, Dict[str, Any]] = {}
        self.job_positions: Dict[str, Dict[str, Any]] = {}
        self.employment_statuses: Dict[str, Dict[str, Any]] = {}
        self.current_user: Dict[str, Any] = {}
        self.next_employee_id: int = 1
        self.audit_log: List[Dict[str, Any]] = []
    
    def _timestamp(self) -> str:
        """
        Generate a standardized ISO format timestamp.
        
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
            scenario: Dictionary containing initial state values for the environment.
            long_context: Flag for extended context loading (reserved for future use).
        
        Returns:
            None
        """
        if not scenario:
            return
        for key in DEFAULT_STATE:
            if key in scenario:
                setattr(self, key, deepcopy(scenario[key]))
            else:
                setattr(self, key, deepcopy(DEFAULT_STATE[key]))
    
    def get_env_state(self) -> Dict[str, Any]:
        """
        Return the current state of all environment variables.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing the complete current state including:
                - employees: All employee records
                - departments: All department records
                - job_positions: All job position definitions
                - employment_statuses: All employment status types
                - current_user: Current authenticated user info
                - next_employee_id: Next available employee ID counter
                - audit_log: List of all audit log entries
        """
        return {
            "employees": deepcopy(self.employees),
            "departments": deepcopy(self.departments),
            "job_positions": deepcopy(self.job_positions),
            "employment_statuses": deepcopy(self.employment_statuses),
            "current_user": deepcopy(self.current_user),
            "next_employee_id": self.next_employee_id,
            "audit_log": deepcopy(self.audit_log)
        }
    
    def _add_audit_log(self, action: str, entity_type: str, entity_id: str, details: str) -> None:
        """
        Add an entry to the audit log.
        
        Args:
            action: The action performed (create, update, delete).
            entity_type: Type of entity affected (employee, department, etc.).
            entity_id: ID of the affected entity.
            details: Description of the changes made.
        
        Returns:
            None
        """
        self.audit_log.append({
            "timestamp": self._timestamp(),
            "user_id": self.current_user.get("user_id", "system"),
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "details": details
        })
    
    # ==================== QUERY OPERATIONS ====================
    
    def get_employee_by_id(self, employee_id: str) -> Dict[str, Any]:
        """
        Retrieve full details of an employee using their unique employee_id.
        
        Args:
            employee_id: The unique identifier of the employee to retrieve.
        
        Returns:
            Dict[str, Any]: Success status and employee details if found, or error dictionary.
        """
        if employee_id not in self.employees:
            return {"error": f"Employee with ID '{employee_id}' not found"}
        return {"success": True, "employee": deepcopy(self.employees[employee_id])}
    
    def get_employee_by_work_email(self, work_email: str) -> Dict[str, Any]:
        """
        Retrieve employee information using their work email address.
        
        Args:
            work_email: The work email address of the employee to find.
        
        Returns:
            Dict[str, Any]: Success status and employee details if found, or error dictionary.
        """
        for emp_id, emp_data in self.employees.items():
            if emp_data.get("work_email", "").lower() == work_email.lower():
                return {"success": True, "employee": deepcopy(emp_data)}
        return {"error": f"Employee with email '{work_email}' not found"}
    
    def list_employees_by_department(self, department_id: str) -> Dict[str, Any]:
        """
        Retrieve all employees assigned to a specific department.
        
        Args:
            department_id: The unique identifier of the department.
        
        Returns:
            Dict[str, Any]: Success status, list of employees, and count; or error if department not found.
        """
        if department_id not in self.departments:
            return {"error": f"Department with ID '{department_id}' not found"}
        
        employees = [
            deepcopy(emp) for emp in self.employees.values()
            if emp.get("department") == department_id
        ]
        return {"success": True, "employees": employees, "count": len(employees)}
    
    def list_employees_by_job_title(self, job_title: str) -> Dict[str, Any]:
        """
        Retrieve all employees holding a specific job title.
        
        Args:
            job_title: The job title to filter employees by.
        
        Returns:
            Dict[str, Any]: Success status, list of employees, and count.
        """
        employees = [
            deepcopy(emp) for emp in self.employees.values()
            if emp.get("job_title") == job_title
        ]
        return {"success": True, "employees": employees, "count": len(employees)}
    
    def list_employees_by_employment_status(self, status: str) -> Dict[str, Any]:
        """
        Retrieve employees filtered by their current employment status.
        
        Args:
            status: The employment status to filter by (e.g., 'active', 'on_leave').
        
        Returns:
            Dict[str, Any]: Success status, list of employees, and count; or error if invalid status.
        """
        if status not in self.employment_statuses:
            return {"error": f"Invalid employment status '{status}'. Valid statuses: {list(self.employment_statuses.keys())}"}
        
        employees = [
            deepcopy(emp) for emp in self.employees.values()
            if emp.get("employment_status") == status
        ]
        return {"success": True, "employees": employees, "count": len(employees)}
    
    def get_department_by_id(self, department_id: str) -> Dict[str, Any]:
        """
        Retrieve information about a department using its department_id.
        
        Args:
            department_id: The unique identifier of the department.
        
        Returns:
            Dict[str, Any]: Success status and department details if found, or error dictionary.
        """
        if department_id not in self.departments:
            return {"error": f"Department with ID '{department_id}' not found"}
        return {"success": True, "department": deepcopy(self.departments[department_id])}
    
    def get_department_by_name(self, department_name: str) -> Dict[str, Any]:
        """
        Retrieve department details by department name.
        
        Args:
            department_name: The name of the department to find.
        
        Returns:
            Dict[str, Any]: Success status and department details if found, or error dictionary.
        """
        for dept_id, dept_data in self.departments.items():
            if dept_data.get("department_name", "").lower() == department_name.lower():
                return {"success": True, "department": deepcopy(dept_data)}
        return {"error": f"Department with name '{department_name}' not found"}
    
    def get_job_position_by_title(self, job_title: str) -> Dict[str, Any]:
        """
        Retrieve salary range and department info for a given job title.
        
        Args:
            job_title: The job title to look up.
        
        Returns:
            Dict[str, Any]: Success status and job position details if found, or error dictionary.
        """
        if job_title not in self.job_positions:
            return {"error": f"Job position '{job_title}' not found"}
        return {"success": True, "job_position": deepcopy(self.job_positions[job_title])}
    
    def get_employment_status_info(self, status_type: str) -> Dict[str, Any]:
        """
        Retrieve details of a predefined employment status type.
        
        Args:
            status_type: The status type to look up (e.g., 'active', 'terminated').
        
        Returns:
            Dict[str, Any]: Success status and status details if found, or error dictionary.
        """
        if status_type not in self.employment_statuses:
            return {"error": f"Employment status '{status_type}' not found. Valid statuses: {list(self.employment_statuses.keys())}"}
        return {"success": True, "employment_status": deepcopy(self.employment_statuses[status_type])}
    
    def check_employee_eligibility_for_action(self, employee_id: str, action: str) -> Dict[str, Any]:
        """
        Determine if an employee is eligible for HR actions based on active status.
        
        Args:
            employee_id: The unique identifier of the employee.
            action: The HR action to check eligibility for (e.g., 'promotion', 'bonus').
        
        Returns:
            Dict[str, Any]: Success status, eligibility status and reason, or error dictionary.
        """
        if employee_id not in self.employees:
            return {"error": f"Employee with ID '{employee_id}' not found"}
        
        employee = self.employees[employee_id]
        status = employee.get("employment_status")
        status_info = self.employment_statuses.get(status, {})
        is_active = status_info.get("is_active", False)
        
        actions_requiring_active = ["promotion", "bonus", "salary_increase", "transfer", "training"]
        
        if action.lower() in actions_requiring_active:
            if is_active and status == "active":
                return {
                    "success": True,
                    "eligible": True,
                    "employee_id": employee_id,
                    "action": action,
                    "reason": "Employee is active and eligible for this action"
                }
            else:
                return {
                    "success": True,
                    "eligible": False,
                    "employee_id": employee_id,
                    "action": action,
                    "reason": f"Employee status is '{status}'. Only active employees are eligible for {action}"
                }
        
        return {
            "success": True,
            "eligible": True,
            "employee_id": employee_id,
            "action": action,
            "reason": f"Action '{action}' does not require active status"
        }
    
    def validate_salary_against_job(self, job_title: str, salary: float) -> Dict[str, Any]:
        """
        Check whether a given salary falls within the defined range for a job title.
        
        Args:
            job_title: The job title to validate salary against.
            salary: The salary amount to validate.
        
        Returns:
            Dict[str, Any]: Success status, validation result with valid flag and salary range info, or error dictionary.
        """
        if job_title not in self.job_positions:
            return {"error": f"Job position '{job_title}' not found"}
        
        position = self.job_positions[job_title]
        min_salary = position.get("salary_range_min", 0)
        max_salary = position.get("salary_range_max", float('inf'))
        
        is_valid = min_salary <= salary <= max_salary
        
        return {
            "success": True,
            "valid": is_valid,
            "job_title": job_title,
            "salary": salary,
            "salary_range_min": min_salary,
            "salary_range_max": max_salary,
            "message": "Salary is within valid range" if is_valid else f"Salary must be between {min_salary} and {max_salary}"
        }
    
    def list_all_departments(self) -> Dict[str, Any]:
        """
        Retrieve a list of all departments in the organization.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Success status, list of all department records, and count.
        """
        departments = list(deepcopy(self.departments).values())
        return {"success": True, "departments": departments, "count": len(departments)}
    
    def list_all_job_positions(self) -> Dict[str, Any]:
        """
        Retrieve all defined job positions in the system.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Success status, list of all job position records, and count.
        """
        positions = list(deepcopy(self.job_positions).values())
        return {"success": True, "job_positions": positions, "count": len(positions)}
    
    # ==================== STATE CHANGE OPERATIONS ====================
    
    def add_employee(
        self,
        first_name: str,
        last_name: str,
        date_of_birth: str,
        gender: str,
        hire_date: str,
        job_title: str,
        department: str,
        salary: float,
        work_email: str,
        phone_number: str,
        address: str,
        manager_id: Optional[str] = None,
        employee_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a new employee to the system, validating all constraints.
        
        Args:
            first_name: Employee's first name.
            last_name: Employee's last name.
            date_of_birth: Employee's date of birth (YYYY-MM-DD format).
            gender: Employee's gender.
            hire_date: Employee's hire date (YYYY-MM-DD format).
            job_title: Employee's job title (must exist in job_positions).
            department: Department ID (must exist in departments).
            salary: Employee's salary (must be within job's salary range).
            work_email: Employee's work email address.
            phone_number: Employee's phone number.
            address: Employee's address.
            manager_id: Optional manager's employee ID.
            employee_id: Optional custom employee ID (auto-generated if not provided).
        
        Returns:
            Dict[str, Any]: Success status with new employee data, or error dictionary.
        """
        # Generate employee ID if not provided
        if employee_id is None:
            employee_id = f"EMP{self.next_employee_id:03d}"
        
        # Validate unique employee_id
        if employee_id in self.employees:
            return {"error": f"Employee ID '{employee_id}' already exists"}
        
        # Validate department exists
        if department not in self.departments:
            return {"error": f"Department '{department}' does not exist"}
        
        # Validate job title exists
        if job_title not in self.job_positions:
            return {"error": f"Job title '{job_title}' does not exist"}
        
        # Validate hire_date is not in the future
        try:
            hire_date_obj = datetime.strptime(hire_date, "%Y-%m-%d")
            current_date = datetime.strptime(self._timestamp().split("T")[0], "%Y-%m-%d")
            if hire_date_obj > current_date:
                return {"error": "Hire date cannot be in the future"}
        except ValueError:
            return {"error": "Invalid hire_date format. Use YYYY-MM-DD"}
        
        # Validate salary within job range
        salary_validation = self.validate_salary_against_job(job_title, salary)
        if not salary_validation.get("valid"):
            return {"error": salary_validation.get("message")}
        
        # Validate manager_id if provided
        if manager_id is not None and manager_id not in self.employees:
            return {"error": f"Manager with ID '{manager_id}' does not exist"}
        
        # Check for duplicate work email
        for emp in self.employees.values():
            if emp.get("work_email", "").lower() == work_email.lower():
                return {"error": f"Work email '{work_email}' is already in use"}
        
        # Create new employee record
        new_employee = {
            "employee_id": employee_id,
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": date_of_birth,
            "gender": gender,
            "hire_date": hire_date,
            "job_title": job_title,
            "department": department,
            "manager_id": manager_id,
            "employment_status": "active",
            "salary": salary,
            "work_email": work_email,
            "phone_number": phone_number,
            "address": address
        }
        
        self.employees[employee_id] = new_employee
        self.next_employee_id += 1
        
        self._add_audit_log("create", "employee", employee_id, f"Added new employee: {first_name} {last_name}")
        
        return {"success": True, "employee": deepcopy(new_employee)}
    
    def update_employee_info(
        self,
        employee_id: str,
        phone_number: Optional[str] = None,
        address: Optional[str] = None,
        work_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Modify non-status employee attributes (e.g., phone number, address).
        
        Args:
            employee_id: The unique identifier of the employee to update.
            phone_number: Optional new phone number.
            address: Optional new address.
            work_email: Optional new work email.
        
        Returns:
            Dict[str, Any]: Success status with updated employee data, or error dictionary.
        """
        if employee_id not in self.employees:
            return {"error": f"Employee with ID '{employee_id}' not found"}
        
        employee = self.employees[employee_id]
        updates = []
        
        if work_email is not None:
            # Check for duplicate work email
            for emp_id, emp in self.employees.items():
                if emp_id != employee_id and emp.get("work_email", "").lower() == work_email.lower():
                    return {"error": f"Work email '{work_email}' is already in use by another employee"}
            employee["work_email"] = work_email
            updates.append("work_email")
        
        if phone_number is not None:
            employee["phone_number"] = phone_number
            updates.append("phone_number")
        
        if address is not None:
            employee["address"] = address
            updates.append("address")
        
        if not updates:
            return {"error": "No fields provided for update"}
        
        self._add_audit_log("update", "employee", employee_id, f"Updated fields: {', '.join(updates)}")
        
        return {"success": True, "employee": deepcopy(employee), "updated_fields": updates}
    
    def update_employee_job_title(
        self,
        employee_id: str,
        new_job_title: str,
        new_salary: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Promote or change an employee's job title, validating new salary and department alignment.
        
        Args:
            employee_id: The unique identifier of the employee.
            new_job_title: The new job title to assign.
            new_salary: Optional new salary (must be within new job's range).
        
        Returns:
            Dict[str, Any]: Success status with updated employee data, or error dictionary.
        """
        if employee_id not in self.employees:
            return {"error": f"Employee with ID '{employee_id}' not found"}
        
        if new_job_title not in self.job_positions:
            return {"error": f"Job title '{new_job_title}' does not exist"}
        
        employee = self.employees[employee_id]
        
        # Check employee is active
        eligibility = self.check_employee_eligibility_for_action(employee_id, "promotion")
        if not eligibility.get("eligible"):
            return {"error": eligibility.get("reason")}
        
        job_position = self.job_positions[new_job_title]
        
        # Determine salary
        if new_salary is not None:
            salary_to_set = new_salary
        else:
            # Keep current salary if within new range, otherwise set to minimum
            current_salary = employee.get("salary", 0)
            min_sal = job_position.get("salary_range_min", 0)
            max_sal = job_position.get("salary_range_max", float('inf'))
            if min_sal <= current_salary <= max_sal:
                salary_to_set = current_salary
            else:
                salary_to_set = min_sal
        
        # Validate salary against new job
        salary_validation = self.validate_salary_against_job(new_job_title, salary_to_set)
        if not salary_validation.get("valid"):
            return {"error": salary_validation.get("message")}
        
        old_title = employee["job_title"]
        employee["job_title"] = new_job_title
        employee["salary"] = salary_to_set
        employee["department"] = job_position.get("department_id", employee["department"])
        
        self._add_audit_log(
            "update", "employee", employee_id,
            f"Changed job title from '{old_title}' to '{new_job_title}', salary: {salary_to_set}"
        )
        
        return {"success": True, "employee": deepcopy(employee)}
    
    def transfer_employee_to_department(self, employee_id: str, new_department_id: str) -> Dict[str, Any]:
        """
        Move an employee to a different department.
        
        Args:
            employee_id: The unique identifier of the employee.
            new_department_id: The ID of the target department.
        
        Returns:
            Dict[str, Any]: Success status with updated employee data, or error dictionary.
        """
        if employee_id not in self.employees:
            return {"error": f"Employee with ID '{employee_id}' not found"}
        
        if new_department_id not in self.departments:
            return {"error": f"Department with ID '{new_department_id}' does not exist"}
        
        employee = self.employees[employee_id]
        
        # Check employee eligibility for transfer
        eligibility = self.check_employee_eligibility_for_action(employee_id, "transfer")
        if not eligibility.get("eligible"):
            return {"error": eligibility.get("reason")}
        
        old_department = employee["department"]
        employee["department"] = new_department_id
        
        self._add_audit_log(
            "update", "employee", employee_id,
            f"Transferred from department '{old_department}' to '{new_department_id}'"
        )
        
        return {"success": True, "employee": deepcopy(employee)}
    
    def update_employee_salary(self, employee_id: str, new_salary: float) -> Dict[str, Any]:
        """
        Adjust an employee's salary, ensuring it falls within the range of their current job title.
        
        Args:
            employee_id: The unique identifier of the employee.
            new_salary: The new salary amount.
        
        Returns:
            Dict[str, Any]: Success status with updated employee data, or error dictionary.
        """
        if employee_id not in self.employees:
            return {"error": f"Employee with ID '{employee_id}' not found"}
        
        employee = self.employees[employee_id]
        job_title = employee["job_title"]
        
        if job_title not in self.job_positions:
            return {"error": f"Job title '{job_title}' not found in system"}
        
        position = self.job_positions[job_title]
        min_salary = position["salary_range_min"]
        max_salary = position["salary_range_max"]
        
        if new_salary < min_salary or new_salary > max_salary:
            return {
                "error": f"Salary {new_salary} is outside the valid range [{min_salary}, {max_salary}] for job title '{job_title}'"
            }
        
        old_salary = employee["salary"]
        employee["salary"] = new_salary
        
        self._add_audit_log(
            "update", "employee", employee_id,
            f"Updated salary from {old_salary} to {new_salary}"
        )
        
        return {"success": True, "employee": deepcopy(employee)}
    
    def get_department_budget_usage(self, department_id: str) -> Dict[str, Any]:
        """
        Calculate the total salary expenditure for a department.
        
        Args:
            department_id: The unique identifier of the department.
        
        Returns:
            Dict[str, Any]: Success status with budget usage info, or error dictionary.
        """
        if department_id not in self.departments:
            return {"error": f"Department with ID '{department_id}' not found"}
        
        department = self.departments[department_id]
        total_salaries = sum(
            emp["salary"] for emp in self.employees.values()
            if emp.get("department") == department_id
        )
        
        budget = department.get("budget", 0)
        remaining = budget - total_salaries
        usage_percentage = (total_salaries / budget * 100) if budget > 0 else 0
        
        return {
            "success": True,
            "department_id": department_id,
            "budget": budget,
            "total_salaries": total_salaries,
            "remaining_budget": remaining,
            "usage_percentage": usage_percentage
        }
    
    def terminate_employee(self, employee_id: str) -> Dict[str, Any]:
        """
        Set an employee's employment status to 'terminated' (records are kept for historical purposes).
        
        Args:
            employee_id: The unique identifier of the employee.
        
        Returns:
            Dict[str, Any]: Success status with updated employee data, or error dictionary.
        """
        if employee_id not in self.employees:
            return {"error": f"Employee with ID '{employee_id}' not found"}
        
        employee = self.employees[employee_id]
        
        if employee["employment_status"] == "terminated":
            return {"error": f"Employee '{employee_id}' is already terminated"}
        
        old_status = employee["employment_status"]
        employee["employment_status"] = "terminated"
        employee_name = f"{employee['first_name']} {employee['last_name']}"
        
        self._add_audit_log(
            "update", "employee", employee_id,
            f"Terminated employee '{employee_name}' (status changed from '{old_status}' to 'terminated')"
        )
        
        return {"success": True, "employee": deepcopy(employee)}
    
    def get_audit_log(self) -> Dict[str, Any]:
        """
        Retrieve the complete audit log.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Success status and copy of the audit log entries.
        """
        return {"success": True, "audit_log": deepcopy(self.audit_log)}


__TEST_CASES__ = [
    # Test case 1: Add employee successfully
    {
        "input": {
            "method": "add_employee",
            "args": {
                "first_name": "Alice",
                "last_name": "Brown",
                "date_of_birth": "1992-04-20",
                "gender": "Female",
                "hire_date": "2023-01-10",
                "job_title": "Software Engineer",
                "department": "DEPT001",
                "salary": 85000.0,
                "work_email": "alice.brown@company.com",
                "phone_number": "+1-555-0201",
                "address": "123 New St, New York, NY 10010"
            }
        },
        "expected_output_contains": {"success": True}
    },
    # Test case 2: Add employee with existing ID
    {
        "input": {
            "method": "add_employee",
            "args": {
                "employee_id": "EMP001",
                "first_name": "Bob",
                "last_name": "White",
                "date_of_birth": "1988-07-12",
                "gender": "Male",
                "hire_date": "2022-06-01",
                "job_title": "HR Specialist",
                "department": "DEPT002",
                "salary": 60000.0,
                "work_email": "bob.white@company.com",
                "phone_number": "+1-555-0202",
                "address": "456 Old Ave, New York, NY 10011"
            }
        },
        "expected_output_contains": {"error": "Employee ID 'EMP001' already exists"}
    },
    # Test case 3: Add employee with invalid department
    {
        "input": {
            "method": "add_employee",
            "args": {
                "first_name": "Charlie",
                "last_name": "Davis",
                "date_of_birth": "1990-11-30",
                "gender": "Male",
                "hire_date": "2023-03-15",
                "job_title": "Financial Analyst",
                "department": "DEPT999",
                "salary": 70000.0,
                "work_email": "charlie.davis@company.com",
                "phone_number": "+1-555-0203",
                "address": "789 Fake St, New York, NY 10012"
            }
        },
        "expected_output_contains": {"error": "Department 'DEPT999' does not exist"}
    },
    # Test case 4: Add employee with salary out of range
    {
        "input": {
            "method": "add_employee",
            "args": {
                "first_name": "Diana",
                "last_name": "Evans",
                "date_of_birth": "1995-09-05",
                "gender": "Female",
                "hire_date": "2023-08-20",
                "job_title": "Junior Developer",
                "department": "DEPT001",
                "salary": 100000.0,  # Exceeds max 65000
                "work_email": "diana.evans@company.com",
                "phone_number": "+1-555-0204",
                "address": "321 High Rd, New York, NY 10013"
            }
        },
        "expected_output_contains": {"error": "Salary must be between"}
    },
    # Test case 5: Get employee by ID
    {
        "input": {"method": "get_employee_by_id", "args": {"employee_id": "EMP001"}},
        "expected_output_contains": {"success": True, "employee": {"employee_id": "EMP001"}}
    },
    # Test case 6: Get non-existent employee
    {
        "input": {"method": "get_employee_by_id", "args": {"employee_id": "EMP999"}},
        "expected_output_contains": {"error": "Employee with ID 'EMP999' not found"}
    },
    # Test case 7: Update employee info
    {
        "input": {"method": "update_employee_info", "args": {"employee_id": "EMP001", "phone_number": "+1-555-9999"}},
        "expected_output_contains": {"success": True, "updated_fields": ["phone_number"]}
    },
    # Test case 8: Update job title successfully
    {
        "input": {"method": "update_employee_job_title", "args": {"employee_id": "EMP005", "new_job_title": "Software Engineer", "new_salary": 75000.0}},
        "expected_output_contains": {"success": True, "employee": {"job_title": "Software Engineer", "salary": 75000.0}}
    },
    # Test case 9: Update job title with invalid title
    {
        "input": {"method": "update_employee_job_title", "args": {"employee_id": "EMP001", "new_job_title": "Astronaut"}},
        "expected_output_contains": {"error": "Job title 'Astronaut' does not exist"}
    },
    # Test case 10: Update salary successfully
    {
        "input": {"method": "update_employee_salary", "args": {"employee_id": "EMP002", "new_salary": 70000.0}},
        "expected_output_contains": {"success": True, "employee": {"salary": 70000.0}}
    },
    # Test case 11: Update salary out of range
    {
        "input": {"method": "update_employee_salary", "args": {"employee_id": "EMP002", "new_salary": 200000.0}},
        "expected_output_contains": {"error": "Salary 200000.0 is outside the valid range"}
    },
    # Test case 12: Transfer employee
    {
        "input": {"method": "transfer_employee_to_department", "args": {"employee_id": "EMP001", "new_department_id": "DEPT003"}},
        "expected_output_contains": {"success": True, "employee": {"department": "DEPT003"}}
    },
    # Test case 13: Transfer to non-existent department
    {
        "input": {"method": "transfer_employee_to_department", "args": {"employee_id": "EMP001", "new_department_id": "DEPT999"}},
        "expected_output_contains": {"error": "Department with ID 'DEPT999' does not exist"}
    },
    # Test case 14: List employees by department
    {
        "input": {"method": "list_employees_by_department", "args": {"department_id": "DEPT001"}},
        "expected_output_contains": {"success": True, "count": 3}
    },
    # Test case 15: Get department budget usage
    {
        "input": {"method": "get_department_budget_usage", "args": {"department_id": "DEPT001"}},
        "expected_output_contains": {"success": True, "department_id": "DEPT001"}
    },
    # Test case 16: Terminate employee successfully
    {
        "input": {"method": "terminate_employee", "args": {"employee_id": "EMP001"}},
        "expected_output_contains": {"success": True, "employee": {"employment_status": "terminated"}}
    },
    # Test case 17: Terminate already terminated employee
    {
        "input": {"method": "terminate_employee", "args": {"employee_id": "EMP001"}},
        "setup": {"employees": {"EMP001": {"employee_id": "EMP001", "first_name": "X", "last_name": "Y", "employment_status": "terminated"}}},
        "expected_output_contains": {"error": "is already terminated"}
    },
    # Test case 18: Get audit log
    {
        "input": {"method": "get_audit_log", "args": {}},
        "expected_output_contains": {"success": True}
    },
    # Test case 19: Validate salary
    {
        "input": {"method": "validate_salary_against_job", "args": {"job_title": "Software Engineer", "salary": 85000.0}},
        "expected_output_contains": {"success": True, "valid": True}
    },
    # Test case 20: List all departments
    {
        "input": {"method": "list_all_departments", "args": {}},
        "expected_output_contains": {"success": True, "count": 3}
    }
]
