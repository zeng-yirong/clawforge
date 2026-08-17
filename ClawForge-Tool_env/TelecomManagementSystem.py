import uuid
from copy import deepcopy
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Union

# 自定义初始状态
DEFAULT_STATE = {
    "customers": {
        "C001": {
            "customer_id": "C001",
            "full_name": "Alice Smith",
            "date_of_birth": "1990-05-15",
            "phone_number": "555-0100",
            "line_ids": ["L001"],
            "bill_ids": ["B001"],
            "balance": 500.0
        }
    },
    "lines": {
        "L001": {
            "line_id": "L001",
            "phone_number": "555-0100",
            "plan_id": "P001",
            "status": "active",
            "data_used_gb": 5.2,
            "data_refueling_gb": 0.0,
            "roaming_enabled": False,
            "suspension_start_date": None,
            "contract_end_date": "2027-01-01"
        }
    },
    "plans": {
        "P001": {
            "plan_id": "P001",
            "name": "Unlimited Basic",
            "price_per_month": 50.0,
            "data_limit_gb": 50.0,
            "data_refueling_price_per_gb": 10.0
        }
    },
    "devices": {
        "D001": {
            "device_id": "D001",
            "model": "iPhone 15",
            "status": "active"
        }
    },
    "bills": {
        "B001": {
            "bill_id": "B001",
            "customer_id": "C001",
            "period_start": "2026-02-01",
            "period_end": "2026-02-28",
            "issue_date": "2026-03-01",
            "due_date": "2026-03-15",
            "total_due": 50.0,
            "status": "paid",
            "line_items": [
                {"description": "Monthly Plan Charge", "amount": 50.0, "date": "2026-03-01", "item_type": "Charge"}
            ]
        }
    }
}


class IDGenerator:
    def __init__(self) -> None:
        self.id_counter = {}

    def reset(self) -> None:
        self.id_counter = {}

    def get_id(self, id_type: str, id_name: str = None) -> str:
        if id_type not in self.id_counter:
            self.id_counter[id_type] = 0
        self.id_counter[id_type] += 1
        id_name = id_name or id_type
        return f"{id_name}_{self.id_counter[id_type]}"

    def sync_counter(self, existing_ids: List[str]) -> None:
        for id_str in existing_ids:
            parts = id_str.rsplit('_', 1)
            if len(parts) == 2 and parts[1].isdigit():
                id_type = parts[0]
                counter_val = int(parts[1])
                if id_type not in self.id_counter or self.id_counter[id_type] < counter_val:
                    self.id_counter[id_type] = counter_val


class TelecomAPI:
    def __init__(self):
        self.id_generator = IDGenerator()
        self.customers: Dict[str, dict] = {}
        self.lines: Dict[str, dict] = {}
        self.plans: Dict[str, dict] = {}
        self.devices: Dict[str, dict] = {}
        self.bills: Dict[str, dict] = {}
        self.current_user: Optional[str] = None
        self._api_description = "This tool belongs to the Telecom API, which is used to manage telecommunication services."

    def _load_scenario(self, scenario, long_context=False, **kwargs):
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)

        self.customers = deepcopy(scenario.get("customers", DEFAULT_STATE_COPY["customers"]))
        self.lines = deepcopy(scenario.get("lines", DEFAULT_STATE_COPY["lines"]))
        self.plans = deepcopy(scenario.get("plans", DEFAULT_STATE_COPY["plans"]))
        self.devices = deepcopy(scenario.get("devices", DEFAULT_STATE_COPY["devices"]))
        self.bills = deepcopy(scenario.get("bills", DEFAULT_STATE_COPY["bills"]))
        self.current_user = None
        self.id_generator.reset()

        all_ids = []
        for cust in self.customers.values():
            all_ids.append(cust["customer_id"])
            for line_id in cust.get("line_ids", []):
                all_ids.append(line_id)
            for bill_id in cust.get("bill_ids", []):
                all_ids.append(bill_id)
        for plan_id in self.plans.keys():
            all_ids.append(plan_id)
        for device_id in self.devices.keys():
            all_ids.append(device_id)
        self.id_generator.sync_counter(all_ids)

    def get_env_state(self) -> dict:
        return deepcopy({
            "customers": self.customers,
            "lines": self.lines,
            "plans": self.plans,
            "devices": self.devices,
            "bills": self.bills
        })

    def login(self, customer_id: str) -> dict:
        customer = self.customers.get(customer_id)
        if not customer:
            return {"success": False, "error": f"Customer {customer_id} not found"}
        self.current_user = customer_id
        return {"success": True, "data": {"message": f"Logged in as {customer_id}"}}

    def logout(self) -> dict:
        self.current_user = None
        return {"success": True, "data": {"message": "Logged out"}}

    def _check_auth(self, customer_id: str) -> Optional[dict]:
        if self.current_user is None:
            return {"success": False, "error": "Not logged in"}
        if self.current_user != customer_id:
            return {"success": False, "error": f"Unauthorized: cannot access customer {customer_id}"}
        return None

    def _timestamp(self) -> str:
        return "2026-03-03"

    def _get_line_by_phone(self, phone_number: str) -> dict:
        for line in self.lines.values():
            if line.get("phone_number") == phone_number:
                return {"success": True, "data": deepcopy(line)}
        return {"success": False, "error": f"Line with phone number {phone_number} not found"}

    def _get_line_by_id(self, line_id: str) -> dict:
        if line_id not in self.lines:
            return {"success": False, "error": f"Line with ID {line_id} not found"}
        return {"success": True, "data": deepcopy(self.lines[line_id])}

    def _get_plan_by_id(self, plan_id: str) -> dict:
        if plan_id not in self.plans:
            return {"success": False, "error": f"Plan with ID {plan_id} not found"}
        return {"success": True, "data": deepcopy(self.plans[plan_id])}

    def _get_device_by_id(self, device_id: str) -> dict:
        if device_id not in self.devices:
            return {"success": False, "error": f"Device with ID {device_id} not found"}
        return {"success": True, "data": deepcopy(self.devices[device_id])}

    def _get_bill_by_id(self, bill_id: str) -> dict:
        if bill_id not in self.bills:
            return {"success": False, "error": f"Bill with ID {bill_id} not found"}
        return {"success": True, "data": deepcopy(self.bills[bill_id])}

    def _get_target_line(self, customer_id: str, line_id: str) -> dict:
        customer = self.get_customer_by_id(customer_id)
        if not customer["success"]:
            return customer

        if line_id not in customer["data"]["line_ids"]:
            return {"success": False, "error": f"Line {line_id} not found for customer {customer_id}"}

        return self._get_line_by_id(line_id)

    def get_id(self, id_type: str, id_name: str = None) -> dict:
        return {"success": True, "data": {"id": self.id_generator.get_id(id_type, id_name)}}

    def get_customer_by_phone(self, phone_number: str) -> dict:
        if not phone_number:
            return {"success": False, "error": "Phone number cannot be empty"}

        for customer in self.customers.values():
            if customer.get("phone_number") == phone_number:
                return {"success": True, "data": deepcopy(customer)}

            for line_id in customer.get("line_ids", []):
                line = self.lines.get(line_id)
                if line and line.get("phone_number") == phone_number:
                    return {"success": True, "data": deepcopy(customer)}

        return {"success": False, "error": f"Customer with phone number {phone_number} not found"}

    def get_customer_by_id(self, customer_id: str) -> dict:
        if customer_id not in self.customers:
            return {"success": False, "error": f"Customer with ID {customer_id} not found"}
        return {"success": True, "data": deepcopy(self.customers[customer_id])}

    def get_customer_by_name(self, full_name: str, dob: str = None) -> dict:
        if not dob:
            return {"success": False, "error": "dob is required"}

        matching_customers = []
        for customer in self.customers.values():
            if (
                customer.get("full_name", "").lower() == full_name.lower()
                and customer.get("date_of_birth") == dob
            ):
                matching_customers.append(deepcopy(customer))
        return {"success": True, "data": matching_customers}

    def get_available_plan_ids(self) -> dict:
        return {"success": True, "data": list(self.plans.keys())}

    def get_details_by_id(self, id: str) -> dict:
        if id.startswith("L"):
            return self._get_line_by_id(id)
        elif id.startswith("D"):
            return self._get_device_by_id(id)
        elif id.startswith("B"):
            return self._get_bill_by_id(id)
        elif id.startswith("C"):
            return self.get_customer_by_id(id)
        elif id.startswith("P"):
            return self._get_plan_by_id(id)
        else:
            return {"success": False, "error": f"Unknown ID format or type: {id}"}

    def suspend_line(self, customer_id: str, line_id: str, reason: str) -> dict:
        auth_error = self._check_auth(customer_id)
        if auth_error:
            return auth_error

        if line_id not in self.lines:
            return {"success": False, "error": f"Line with ID {line_id} not found"}

        if line_id not in self.customers[customer_id]["line_ids"]:
            return {"success": False, "error": f"Line {line_id} not found for customer {customer_id}"}

        line = self.lines[line_id]
        if line["status"] != "active":
            return {"success": False, "error": "Line must be active to suspend"}

        line["status"] = "suspended"
        line["suspension_start_date"] = self._timestamp()

        charge_result = self._apply_one_time_charge(
            customer_id=customer_id,
            amount=5.0,
            description=f"Holding fee for suspended line {line_id} (Reason: {reason})"
        )

        if not charge_result["success"]:
            line["status"] = "active"
            line["suspension_start_date"] = None
            return {"success": False, "error": f"Failed to apply fee: {charge_result['error']}"}

        return {"success": True, "data": {"message": "Line suspended successfully. $5 holding fee applied.", "line": deepcopy(line)}}

    def resume_line(self, customer_id: str, line_id: str) -> dict:
        auth_error = self._check_auth(customer_id)
        if auth_error:
            return auth_error

        if line_id not in self.lines:
            return {"success": False, "error": f"Line with ID {line_id} not found"}

        if line_id not in self.customers[customer_id]["line_ids"]:
            return {"success": False, "error": f"Line {line_id} not found for customer {customer_id}"}

        line = self.lines[line_id]
        if line["status"] not in ["suspended", "pending_activation"]:
            return {"success": False, "error": "Line must be suspended to resume"}

        line["status"] = "active"
        line["suspension_start_date"] = None

        return {"success": True, "data": {"message": "Line resumed successfully", "line": deepcopy(line)}}

    def get_bills_for_customer(self, customer_id: str, limit: int = 12) -> dict:
        auth_error = self._check_auth(customer_id)
        if auth_error:
            return auth_error

        if not isinstance(limit, int):
            return {"success": False, "error": "Limit must be an integer"}
        if limit <= 0:
            return {"success": False, "error": "Limit must be positive"}

        customer = self.customers.get(customer_id)
        if not customer:
            return {"success": False, "error": f"Customer with ID {customer_id} not found"}

        bills = []
        for bill_id in customer["bill_ids"]:
            bill = self.bills.get(bill_id)
            if bill:
                bills.append(deepcopy(bill))

        sorted_bills = sorted(bills, key=lambda b: b["issue_date"], reverse=True)
        return {"success": True, "data": sorted_bills[:limit]}

    def send_payment_request(self, customer_id: str, bill_id: str) -> dict:
        auth_error = self._check_auth(customer_id)
        if auth_error:
            return auth_error

        customer = self.customers.get(customer_id)
        if not customer:
            return {"success": False, "error": f"Customer with ID {customer_id} not found"}

        bills_awaiting = self._get_bills_awaiting_payment(customer)
        if len(bills_awaiting) > 0:
            return {"success": False, "error": "A bill is already awaiting payment for this customer"}

        if bill_id not in customer["bill_ids"]:
            return {"success": False, "error": f"Bill {bill_id} not found for customer {customer_id}"}

        if bill_id not in self.bills:
            return {"success": False, "error": f"Bill {bill_id} not found"}

        bill = self.bills[bill_id]
        if bill["status"] == "paid":
            return {"success": False, "error": "Bill is already paid"}

        bill["status"] = "awaiting_payment"
        return {"success": True, "data": {"message": f"Payment request sent to the customer for bill {bill_id}"}}

    def pay_bill(self, customer_id: str, bill_id: str) -> dict:
        auth_error = self._check_auth(customer_id)
        if auth_error:
            return auth_error

        customer = self.customers.get(customer_id)
        if not customer:
            return {"success": False, "error": f"Customer with ID {customer_id} not found"}

        if bill_id not in customer["bill_ids"]:
            return {"success": False, "error": f"Bill {bill_id} not found for customer {customer_id}"}

        if bill_id not in self.bills:
            return {"success": False, "error": f"Bill {bill_id} not found"}

        bill = self.bills[bill_id]
        if bill["status"] == "paid":
            return {"success": False, "error": "Bill is already paid"}

        if customer["balance"] < bill["total_due"]:
            return {"success": False, "error": "Insufficient balance to pay the bill"}

        customer["balance"] -= bill["total_due"]
        bill["status"] = "paid"

        return {"success": True, "data": {"message": f"Bill {bill_id} paid successfully. Remaining balance: ${customer['balance']:.2f}"}}

    def add_balance(self, customer_id: str, amount: float) -> dict:
        auth_error = self._check_auth(customer_id)
        if auth_error:
            return auth_error

        if amount <= 0:
            return {"success": False, "error": "Amount must be positive"}

        customer = self.customers.get(customer_id)
        if not customer:
            return {"success": False, "error": f"Customer with ID {customer_id} not found"}

        customer["balance"] += amount
        return {"success": True, "data": {"message": f"Added ${amount:.2f} to balance. New balance: ${customer['balance']:.2f}"}}

    def _get_bills_awaiting_payment(self, customer: dict) -> list:
        bills = []
        for bill_id in customer.get("bill_ids", []):
            bill = self.bills.get(bill_id)
            if bill and bill.get("status") == "awaiting_payment":
                bills.append(bill)
        return bills

    def _apply_one_time_charge(self, customer_id: str, amount: float, description: str) -> dict:
        customer = self.customers.get(customer_id)
        if not customer:
            return {"success": False, "error": f"Customer with ID {customer_id} not found"}

        today_date = datetime.strptime(self._timestamp(), "%Y-%m-%d").date()
        if today_date.month == 12:
            next_month = date(today_date.year + 1, 1, 1)
        else:
            next_month = date(today_date.year, today_date.month + 1, 1)

        if next_month.month == 12:
            period_end = date(next_month.year + 1, 1, 1) - timedelta(days=1)
        else:
            period_end = date(next_month.year, next_month.month + 1, 1) - timedelta(days=1)

        expected_period_start = next_month.strftime("%Y-%m-%d")

        draft_bill = None
        for bill_id in customer["bill_ids"]:
            bill = self.bills.get(bill_id)
            if bill and bill["status"] == "draft" and bill["period_start"] == expected_period_start:
                draft_bill = bill
                break

        if not draft_bill:
            new_bill_id = f"B{uuid.uuid4().hex[:8]}"
            draft_bill = {
                "bill_id": new_bill_id,
                "customer_id": customer_id,
                "period_start": expected_period_start,
                "period_end": period_end.strftime("%Y-%m-%d"),
                "issue_date": expected_period_start,
                "total_due": 0.0,
                "due_date": (next_month + timedelta(days=14)).strftime("%Y-%m-%d"),
                "status": "draft",
                "line_items": []
            }
            self.bills[new_bill_id] = draft_bill
            customer["bill_ids"].append(new_bill_id)

        line_item = {
            "description": description,
            "amount": amount,
            "date": self._timestamp(),
            "item_type": "Credit" if amount < 0 else "Charge"
        }
        draft_bill["line_items"].append(line_item)
        draft_bill["total_due"] += amount

        return {"success": True, "data": {"message": "Charge applied"}}

    def get_data_usage(self, customer_id: str, line_id: str) -> dict:
        auth_error = self._check_auth(customer_id)
        if auth_error:
            return auth_error

        target_line_result = self._get_target_line(customer_id, line_id)
        if not target_line_result["success"]:
            return target_line_result

        target_line = self.lines[line_id]
        plan = self.plans.get(target_line["plan_id"])
        if not plan:
            return {"success": False, "error": "Plan not found for this line"}

        today_date = datetime.strptime(self._timestamp(), "%Y-%m-%d").date()
        if today_date.month == 12:
            cycle_end_date = date(today_date.year + 1, 1, 1) - timedelta(days=1)
        else:
            cycle_end_date = date(today_date.year, today_date.month + 1, 1) - timedelta(days=1)

        return {
            "success": True,
            "data": {
                "line_id": line_id,
                "data_used_gb": target_line["data_used_gb"],
                "data_limit_gb": plan["data_limit_gb"],
                "data_refueling_gb": target_line["data_refueling_gb"],
                "cycle_end_date": cycle_end_date.strftime("%Y-%m-%d"),
            }
        }

    def set_data_usage(self, customer_id: str, line_id: str, data_used_gb: float) -> dict:
        auth_error = self._check_auth(customer_id)
        if auth_error:
            return auth_error

        if data_used_gb < 0:
            return {"success": False, "error": "Data usage cannot be negative"}

        if line_id not in self.lines:
            return {"success": False, "error": f"Line with ID {line_id} not found"}

        if line_id not in self.customers[customer_id]["line_ids"]:
            return {"success": False, "error": f"Line {line_id} not found for customer {customer_id}"}

        self.lines[line_id]["data_used_gb"] = data_used_gb
        return {"success": True, "data": {"message": f"Data usage set to {data_used_gb} GB for line {line_id}"}}

    def enable_roaming(self, customer_id: str, line_id: str) -> dict:
        auth_error = self._check_auth(customer_id)
        if auth_error:
            return auth_error

        if line_id not in self.lines:
            return {"success": False, "error": f"Line with ID {line_id} not found"}

        if line_id not in self.customers[customer_id]["line_ids"]:
            return {"success": False, "error": f"Line {line_id} not found for customer {customer_id}"}

        if self.lines[line_id].get("roaming_enabled"):
            return {"success": True, "data": {"message": "Roaming was already enabled"}}

        self.lines[line_id]["roaming_enabled"] = True
        return {"success": True, "data": {"message": "Roaming enabled successfully"}}

    def disable_roaming(self, customer_id: str, line_id: str) -> dict:
        auth_error = self._check_auth(customer_id)
        if auth_error:
            return auth_error

        if line_id not in self.lines:
            return {"success": False, "error": f"Line with ID {line_id} not found"}

        if line_id not in self.customers[customer_id]["line_ids"]:
            return {"success": False, "error": f"Line {line_id} not found for customer {customer_id}"}

        if not self.lines[line_id].get("roaming_enabled"):
            return {"success": True, "data": {"message": "Roaming was already disabled"}}

        self.lines[line_id]["roaming_enabled"] = False
        return {"success": True, "data": {"message": "Roaming disabled successfully"}}

    def transfer_to_human_agents(self, summary: str) -> dict:
        return {"success": True, "data": {"message": "Transfer successful"}}

    def refuel_data(self, customer_id: str, line_id: str, gb_amount: float) -> dict:
        auth_error = self._check_auth(customer_id)
        if auth_error:
            return auth_error

        if line_id not in self.lines:
            return {"success": False, "error": f"Line with ID {line_id} not found"}

        if line_id not in self.customers[customer_id]["line_ids"]:
            return {"success": False, "error": f"Line {line_id} not found for customer {customer_id}"}

        if gb_amount <= 0:
            return {"success": False, "error": "Refuel amount must be positive"}

        plan = self.plans.get(self.lines[line_id]["plan_id"])
        if not plan:
            return {"success": False, "error": "Plan not found for this line"}

        charge_amount = gb_amount * plan["data_refueling_price_per_gb"]

        charge_result = self._apply_one_time_charge(
            customer_id,
            charge_amount,
            f"Data refueling: {gb_amount} GB at ${plan['data_refueling_price_per_gb']}/GB",
        )

        if not charge_result["success"]:
            return charge_result

        self.lines[line_id]["data_refueling_gb"] += gb_amount

        return {
            "success": True,
            "data": {
                "message": f"Successfully added {gb_amount} GB of data for line {line_id} for ${charge_amount:.2f}",
                "new_data_refueling_gb": self.lines[line_id]["data_refueling_gb"],
                "charge": charge_amount,
            }
        }

    def use_data(self, customer_id: str, line_id: str, gb_amount: float) -> dict:
        auth_error = self._check_auth(customer_id)
        if auth_error:
            return auth_error

        if line_id not in self.lines:
            return {"success": False, "error": f"Line with ID {line_id} not found"}

        if line_id not in self.customers[customer_id]["line_ids"]:
            return {"success": False, "error": f"Line {line_id} not found for customer {customer_id}"}

        if gb_amount <= 0:
            return {"success": False, "error": "Data amount must be positive"}

        line = self.lines[line_id]
        available_refuel = line["data_refueling_gb"]
        plan = self.plans.get(line["plan_id"])
        plan_limit = plan["data_limit_gb"] if plan else 0
        used = line["data_used_gb"]
        remaining_plan = max(0, plan_limit - used)
        total_available = available_refuel + remaining_plan

        if gb_amount > total_available:
            return {"success": False, "error": f"Insufficient data. Available: {total_available} GB, requested: {gb_amount} GB"}

        if gb_amount <= remaining_plan:
            line["data_used_gb"] += gb_amount
        else:
            line["data_used_gb"] = plan_limit
            excess = gb_amount - remaining_plan
            line["data_refueling_gb"] -= excess

        return {"success": True, "data": {"message": f"Used {gb_amount} GB of data for line {line_id}"}}

    def suspend_line_for_overdue_bill(self, customer_id: str, line_id: str, new_bill_id: str, contract_ended: bool) -> dict:
        auth_error = self._check_auth(customer_id)
        if auth_error:
            return auth_error

        if line_id not in self.lines:
            return {"success": False, "error": f"Line with ID {line_id} not found"}

        line = self.lines[line_id]
        if line["status"] != "active":
            return {"success": False, "error": "Line must be active to suspend for unpaid bill"}

        plan = self.plans.get(line["plan_id"])
        if not plan:
            return {"success": False, "error": "Plan not found for this line"}

        amount = plan["price_per_month"]
        if amount <= 0:
            return {"success": False, "error": "Amount must be positive for overdue bill"}

        customer = self.customers.get(customer_id)
        if not customer:
            return {"success": False, "error": f"Customer with ID {customer_id} not found"}

        if new_bill_id in self.bills:
            return {"success": False, "error": f"Critical Error: Bill ID '{new_bill_id}' already exists in the system. Operation aborted to prevent data corruption."}

        for bill_id in customer["bill_ids"]:
            bill = self.bills.get(bill_id)
            if bill and bill["status"] == "overdue":
                return {"success": False, "error": "Customer already has an overdue bill"}

        today_date = datetime.strptime(self._timestamp(), "%Y-%m-%d").date()

        first_day_this_month = today_date.replace(day=1)
        last_day_of_last_month = first_day_this_month - timedelta(days=1)
        first_day_of_last_month = last_day_of_last_month.replace(day=1)

        overdue_bill = {
            "bill_id": new_bill_id,
            "customer_id": customer_id,
            "period_start": first_day_of_last_month.strftime("%Y-%m-%d"),
            "period_end": last_day_of_last_month.strftime("%Y-%m-%d"),
            "issue_date": first_day_of_last_month.strftime("%Y-%m-%d"),
            "total_due": amount,
            "due_date": (first_day_of_last_month + timedelta(days=14)).strftime("%Y-%m-%d"),
            "status": "overdue",
            "line_items": [
                {
                    "description": f"Charge for line {line['line_id']}",
                    "amount": amount,
                    "date": self._timestamp(),
                    "item_type": "Charge" if amount > 0 else "Credit"
                }
            ]
        }

        self.bills[new_bill_id] = overdue_bill
        customer["bill_ids"].append(new_bill_id)

        line["status"] = "suspended"
        line["suspension_start_date"] = self._timestamp()
        if contract_ended:
            line["contract_end_date"] = last_day_of_last_month.strftime("%Y-%m-%d")

        return {"success": True, "data": {"message": f"Line {line_id} suspended for unpaid bill {new_bill_id}. Contract ended: {contract_ended}"}}


__TEST_CASES__ = [
    {
        'name': 'Normal Path - Customer Lookups & Plans',
        'steps': [
            {'expect_success': True, 'tool_call': "env['telecom'].get_customer_by_phone(phone_number='555-0100')"},
            {'expect_success': True, 'tool_call': "env['telecom'].get_customer_by_name(full_name='Alice Smith', dob='1990-05-15')"},
            {'expect_success': True, 'tool_call': "env['telecom'].get_customer_by_id(customer_id='C001')"},
            {'expect_success': True, 'tool_call': "env['telecom'].get_available_plan_ids()"},
            {'expect_success': True, 'tool_call': "env['telecom'].get_details_by_id(id='P001')"}
        ]
    },
    {
        'name': 'State-change verification - Roaming',
        'steps': [
            {'expect_success': True, 'tool_call': "env['telecom'].enable_roaming(customer_id='C001', line_id='L001')"},
            {'expect_success': True, 'tool_call': "env['telecom'].get_details_by_id(id='L001')"},
            {'expect_success': True, 'tool_call': "env['telecom'].disable_roaming(customer_id='C001', line_id='L001')"},
            {'expect_success': True, 'tool_call': "env['telecom'].get_details_by_id(id='L001')"}
        ]
    },
    {
        'name': 'State-change verification - Data Usage & Refuel',
        'steps': [
            {'expect_success': True, 'tool_call': "env['telecom'].get_data_usage(customer_id='C001', line_id='L001')"},
            {'expect_success': True, 'tool_call': "env['telecom'].set_data_usage(customer_id='C001', line_id='L001', data_used_gb=10.5)"},
            {'expect_success': True, 'tool_call': "env['telecom'].refuel_data(customer_id='C001', line_id='L001', gb_amount=5.0)"},
        ]
    },
    {
        'name': 'Cross-method workflow - Suspension and Resumption',
        'steps': [
            {'expect_success': True, 'tool_call': "env['telecom'].suspend_line(customer_id='C001', line_id='L001', reason='Lost phone')"},
            {'expect_success': True, 'tool_call': "env['telecom'].resume_line(customer_id='C001', line_id='L001')"},
        ]
    },
    {
        'name': 'Cross-method workflow - Billing & Payment',
        'steps': [
            {'expect_success': True, 'tool_call': "env['telecom'].get_bills_for_customer(customer_id='C001', limit=5)"},
            {'expect_success': True, 'tool_call': "env['telecom'].send_payment_request(customer_id='C001', bill_id='B001')"},
            {'expect_success': True, 'tool_call': "env['telecom'].pay_bill(customer_id='C001', bill_id='B001')"},
        ]
    },
    {
        'name': 'Error path - Invalid IDs, Missing Fields, Wrong Types',
        'steps': [
            {'expect_success': False, 'tool_call': "env['telecom'].get_customer_by_id(customer_id='C999')"},
            {'expect_success': False, 'tool_call': "env['telecom'].get_details_by_id(id='INVALID')"},
            {'expect_success': False, 'tool_call': "env['telecom'].get_customer_by_name(full_name='Alice Smith')"},
            {'expect_success': False, 'tool_call': "env['telecom'].get_bills_for_customer(customer_id='C001', limit='five')"}
        ]
    },
    {
        'name': 'Error path - Invalid Data Types & Boundaries',
        'steps': [
            {'expect_success': False, 'tool_call': "env['telecom'].set_data_usage(customer_id='C001', line_id='L001', data_used_gb=-5.0)"},
            {'expect_success': False, 'tool_call': "env['telecom'].refuel_data(customer_id='C001', line_id='L001', gb_amount=-10.0)"},
            {'expect_success': False, 'tool_call': "env['telecom'].get_customer_by_phone(phone_number='')"}
        ]
    },
    {
        'name': 'Boundary values - Extremely large inputs and 0',
        'steps': [
            {'expect_success': True, 'tool_call': "env['telecom'].set_data_usage(customer_id='C001', line_id='L001', data_used_gb=9999999.99)"},
            {'expect_success': True, 'tool_call': "env['telecom'].get_bills_for_customer(customer_id='C001', limit=10000)"},
            {'expect_success': True, 'tool_call': "env['telecom'].transfer_to_human_agents(summary='A very long summary that exceeds normal limits to test boundary conditions of the text field processing in the system.')"}
        ]
    },
    {
        'name': 'Cross-method workflow - Suspend for overdue bill',
        'steps': [
            {'expect_success': True, 'tool_call': "env['telecom'].suspend_line_for_overdue_bill(customer_id='C001', line_id='L001', new_bill_id='B002', contract_ended=False)"},
        ]
    },
    {
        'name': 'Authentication and Authorization Tests',
        'steps': [
            {'expect_success': False, 'tool_call': "env['telecom'].suspend_line(customer_id='C001', line_id='L001', reason='Test')"},
            {'expect_success': True, 'tool_call': "env['telecom'].login(customer_id='C001')"},
            {'expect_success': True, 'tool_call': "env['telecom'].suspend_line(customer_id='C001', line_id='L001', reason='Test')"},
            {'expect_success': True, 'tool_call': "env['telecom'].logout()"},
            {'expect_success': False, 'tool_call': "env['telecom'].suspend_line(customer_id='C001', line_id='L001', reason='Test')"},
        ]
    }
]