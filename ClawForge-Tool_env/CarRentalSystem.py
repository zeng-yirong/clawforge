from copy import deepcopy
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, date, timedelta

# 默认状态，用于初始化环境
DEFAULT_STATE = {
    "vehicles": {
        "CAR-001": {
            "make": "Toyota",
            "model": "Camry",
            "type": "Sedan",
            "status": "Available",  # Available, Rented, Maintenance
            "price_per_day": 60.00,
            "fuel_level": 100,  # Percentage
            "mileage": 15000
        },
        "SUV-001": {
            "make": "Ford",
            "model": "Explorer",
            "type": "SUV",
            "status": "Rented",
            "price_per_day": 95.00,
            "fuel_level": 85,
            "mileage": 22000
        },
        "VAN-001": {
            "make": "Mercedes",
            "model": "Sprinter",
            "type": "Van",
            "status": "Maintenance",
            "price_per_day": 120.00,
            "fuel_level": 100,
            "mileage": 35000
        }
    },
    "bookings": {
        10001: {
            "booking_id": 10001,
            "customer": "customer_a",
            "vehicle_id": "SUV-001",
            "start_date": "2026-05-01",
            "end_date": "2026-05-05",
            "status": "Active",  # Reserved, Active, Completed, Cancelled
            "total_estimated_cost": 380.00,
            "pickup_fuel": 85,
            "return_details": {}
        }
    },
    "booking_counter": 10002,
    "system_date": "2026-05-03",  # 用于模拟时间推进
    "current_user": None,
    "customers": {
        "customer_a": {"name": "Alice Smith", "license_valid_until": "2030-01-01", "balance": 1000.00},
        "customer_b": {"name": "Bob Jones", "license_valid_until": "2026-06-01", "balance": 50.00}
    }
}


class AdvancedCarRentalAPI:
    """
    An advanced Car Rental API for managing vehicle inventory, customer bookings,
    pickups, returns, and complex status transitions.

    Attributes:
        vehicles (Dict): Inventory of vehicles keyed by license plate (ID).
        bookings (Dict): Dictionary of rental bookings keyed by booking ID.
        booking_counter (int): Counter for generating unique booking IDs.
        system_date (str): Simulated current date for logical calculations (YYYY-MM-DD).
        current_user (Optional[str]): Currently authenticated user/system agent.
        customers (Dict): Database of user accounts, license validity, and balance.
    """

    def __init__(self):
        self.vehicles: Dict[str, Dict[str, Union[str, float, int]]]
        self.bookings: Dict[int, Dict[str, Union[int, str, float, dict]]]
        self.booking_counter: int
        self.system_date: str
        self.current_user: Optional[str]
        self.customers: Dict[str, Dict[str, Union[str, float]]]

        # 内部业务规则参数
        self.fuel_penalty_per_percent = 2.00  # 少 1% 燃油扣费
        self.overdue_fine_per_day = 1.5  # 1.5倍日租金作为逾期罚款

        self._api_description = "Advanced system tool for managing car rentals, availability search, bookings, and returns."

    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Loads a specific scenario into the environment state.

        Args:
            scenario (dict): The scenario definition to load.
            long_context (bool): Unused context parameter.
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.vehicles = scenario.get("vehicles", DEFAULT_STATE_COPY["vehicles"])
        self.bookings = scenario.get("bookings", DEFAULT_STATE_COPY["bookings"])
        self.booking_counter = scenario.get("booking_counter", DEFAULT_STATE_COPY["booking_counter"])
        self.system_date = scenario.get("system_date", DEFAULT_STATE_COPY["system_date"])
        self.current_user = scenario.get("current_user", DEFAULT_STATE_COPY["current_user"])
        self.customers = scenario.get("customers", DEFAULT_STATE_COPY["customers"])

    def get_env_state(self) -> Dict[str, Any]:
        """
        Returns the current state of the environment.

        Returns:
            Dict[str, Any]: A dictionary containing the current environment state.
        """
        return {
            "vehicles": self.vehicles,
            "bookings": self.bookings,
            "booking_counter": self.booking_counter,
            "system_date": self.system_date,
            "current_user": self.current_user,
            "customers": self.customers
        }

    # 辅助方法：处理日期
    def _get_date(self, date_str: str) -> date:
        """
        Converts a date string to a date object.

        Args:
            date_str (str): The date string in YYYY-MM-DD format.

        Returns:
            date: The parsed date object.
        """
        return datetime.strptime(date_str, "%Y-%m-%d").date()

    def _get_sys_date(self) -> date:
        """
        Returns the system date as a date object.

        Returns:
            date: The parsed system date object.
        """
        return self._get_date(self.system_date)

    # 认证机制
    def login(self, username: str) -> Dict[str, str]:
        """
        Authenticate as a customer or staff member.

        Args:
            username (str): The username to authenticate.

        Returns:
            Dict[str, str]: Success message or an error dictionary.
        """
        if username not in self.customers:
            return {"error": f"Customer {username} not found."}
        self.current_user = username
        return {"status": f"Logged in as {username}."}

    # 业务逻辑方法

    def search_available_vehicles(self, start_date: str, end_date: str, car_type: Optional[str] = None) -> Dict[str, Union[str, dict]]:
        """
        Search for available vehicles within a specific date range, optionally filtered by car type.
        This performs a complex check against existing bookings for conflicts.

        Args:
            start_date (str): The requested start date in YYYY-MM-DD format.
            end_date (str): The requested end date in YYYY-MM-DD format.
            car_type (Optional[str]): The optional car type filter.

        Returns:
            Dict[str, Union[str, dict]]: Dictionary containing available vehicles or error/message.
        """
        if not self.current_user:
            return {"error": "Authentication required for transactional search."}

        if car_type and (not isinstance(car_type, str) or len(car_type) > 50):
            return {"error": "Invalid car type specified."}

        try:
            req_start = self._get_date(start_date)
            req_end = self._get_date(end_date)
            sys_date = self._get_sys_date()
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD."}

        if req_start < sys_date or req_end <= req_start:
            return {"error": "Invalid date range. Cannot search in the past, and end date must be after start date."}

        available_cars = {}

        # 遍历所有车辆
        for vid, vdetails in self.vehicles.items():
            # 基础状态检查
            if vdetails["status"] == "Maintenance":
                continue
            if car_type and vdetails["type"].lower() != car_type.lower():
                continue

            # 复杂的预订冲突检查
            is_conflicted = False
            for bid, bdetails in self.bookings.items():
                if bdetails["vehicle_id"] == vid and bdetails["status"] in ["Reserved", "Active"]:
                    book_start = self._get_date(bdetails["start_date"])
                    book_end = self._get_date(bdetails["end_date"])

                    # 检查日期重叠情况
                    if (req_start < book_end) and (req_end > book_start):
                        is_conflicted = True
                        break

            if not is_conflicted:
                available_cars[vid] = vdetails

        if not available_cars:
            return {"message": "No vehicles available for the selected dates."}
        return {"results": available_cars}

    def create_booking(self, vehicle_id: str, start_date: str, end_date: str) -> Dict[str, Union[str, int, float]]:
        """
        Create a reservation for a vehicle.
        Performs complex validation including drivers license validity and inventory locking.

        Args:
            vehicle_id (str): The ID of the vehicle to book.
            start_date (str): The start date of the booking in YYYY-MM-DD format.
            end_date (str): The end date of the booking in YYYY-MM-DD format.

        Returns:
            Dict[str, Union[str, int, float]]: Booking status and ID or error.
        """
        if not self.current_user:
            return {"error": "Authentication required."}

        customer_data = self.customers[self.current_user]
        if customer_data["balance"] < 0:
            return {"error": f"Cannot create booking. You have an outstanding debt of ${abs(customer_data['balance']):.2f}. Please settle your account first."}
        
        try:
            req_end = self._get_date(end_date)
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD."}

        # 1. 验证驾驶执照
        if self._get_date(customer_data["license_valid_until"]) <= req_end:
            return {"error": "Cannot book. Your drivers license will be expired at the end of the rental."}

        # 2. 再次验证车辆可用性（防止竞争条件）
        search_res = self.search_available_vehicles(start_date, end_date)
        if "error" in search_res or "message" in search_res or vehicle_id not in search_res.get("results", {}):
            return {"error": f"Vehicle {vehicle_id} is not available for these dates."}

        # 3. 计算预估费用
        days = (req_end - self._get_date(start_date)).days
        price_per_day = self.vehicles[vehicle_id]["price_per_day"]
        estimated_cost = days * price_per_day

        if customer_data["balance"] < estimated_cost:
            return {"error": f"Insufficient balance for estimated cost ${estimated_cost:.2f}."}

        # 4. 创建预订
        booking_id = self.booking_counter
        self.bookings[booking_id] = {
            "booking_id": booking_id,
            "customer": self.current_user,
            "vehicle_id": vehicle_id,
            "start_date": start_date,
            "end_date": end_date,
            "status": "Reserved",
            "total_estimated_cost": estimated_cost,
            "pickup_fuel": None,  # Filled at pickup
            "return_details": {}
        }

        self.booking_counter += 1
        return {
            "status": "Reservation created.",
            "booking_id": booking_id,
            "total_estimated_cost": estimated_cost
        }

    def cancel_booking(self, booking_id: int) -> Dict[str, str]:
        """
        Cancel a reservation before it becomes active.

        Args:
            booking_id (int): The ID of the booking to cancel.

        Returns:
            Dict[str, str]: Success status or error.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
        if booking_id not in self.bookings:
            return {"error": "Booking not found."}

        booking_data = self.bookings[booking_id]
        if booking_data["customer"] != self.current_user:
            return {"error": "Unauthorized access to this booking."}

        if booking_data["status"] != "Reserved":
            return {"error": f"Cannot cancel booking with status '{booking_data['status']}'."}

        booking_data["status"] = "Cancelled"
        return {"status": f"Booking {booking_id} cancelled successfully."}

    def pickup_vehicle(self, booking_id: int) -> Dict[str, Union[str, int]]:
        """
        Transition booking from 'Reserved' to 'Active'.
        Requires physical verification (simulated by system date and initial fuel level).

        Args:
            booking_id (int): The ID of the booking for pickup.

        Returns:
            Dict[str, Union[str, int]]: Pickup status and initial fuel or error.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
        if booking_id not in self.bookings:
            return {"error": "Booking not found."}

        booking_data = self.bookings[booking_id]
        if booking_data["status"] != "Reserved":
            return {"error": f"Cannot pickup for booking in '{booking_data['status']}' status."}

        # 必须在开始日期取车
        if booking_data["start_date"] != self.system_date:
            return {
                "error": f"Pickup date ({self.system_date}) does not match scheduled start date ({booking_data['start_date']})."}

        # 锁定车辆物理状态
        vehicle_id = booking_data["vehicle_id"]
        current_fuel = self.vehicles[vehicle_id]["fuel_level"]

        booking_data["status"] = "Active"
        booking_data["pickup_fuel"] = current_fuel
        self.vehicles[vehicle_id]["status"] = "Rented"  # 同时更新车辆主库存状态

        return {"status": "Pickup successful. Vehicle rented.", "recorded_pickup_fuel": current_fuel}

    def return_vehicle(self, booking_id: int, return_fuel_level: int, added_mileage: int) -> Dict[str, Union[str, float]]:
        """
        Return a vehicle and process the final billing.
        Decoupled state machine: Vehicle is ALWAYS returned to inventory, even if the customer defaults on payment.

        Args:
            booking_id (int): The ID of the booking to be returned.
            return_fuel_level (int): The final fuel level percentage (0-100).
            added_mileage (int): The mileage added to the vehicle during the rental.

        Returns:
            Dict[str, Union[str, float]]: Status, payment status, and charged amount or error.
        """
        if return_fuel_level < 0 or added_mileage < 0:
            return {"error": "Invalid input: fuel level and mileage cannot be negative."}

        if not self.current_user:
            return {"error": "Authentication required."}
        if booking_id not in self.bookings:
            return {"error": "Booking not found."}

        booking_data = self.bookings[booking_id]
        if booking_data["status"] != "Active":
            return {"error": f"Cannot return for booking in '{booking_data['status']}' status."}

        if booking_data["customer"] != self.current_user:
            return {"error": "Unauthorized operation."}

        vehicle_id = booking_data["vehicle_id"]
        customer_id = booking_data["customer"]

        # ==========================================
        # 1. 物理资产层：无条件优先回收车辆！
        # ==========================================
        self.vehicles[vehicle_id]["status"] = "Available"
        self.vehicles[vehicle_id]["fuel_level"] = return_fuel_level
        self.vehicles[vehicle_id]["mileage"] += added_mileage

        # ==========================================
        # 2. 财务计费层：计算账单
        # ==========================================
        final_bill = 0.0
        scheduled_end = self._get_date(booking_data["end_date"])
        actual_return = self._get_sys_date()

        price_per_day = self.vehicles[vehicle_id]["price_per_day"]

        # 计算租金与逾期
        if actual_return <= scheduled_end:
            final_bill += booking_data["total_estimated_cost"]
        else:
            overdue_days = (actual_return - scheduled_end).days
            regular_rent = booking_data["total_estimated_cost"]
            fines = overdue_days * price_per_day * self.overdue_fine_per_day
            final_bill += regular_rent + fines

        # 计算燃油罚金
        fuel_charge = 0.0
        if return_fuel_level < booking_data["pickup_fuel"]:
            fuel_diff_percent = booking_data["pickup_fuel"] - return_fuel_level
            fuel_charge = fuel_diff_percent * self.fuel_penalty_per_percent
            final_bill += fuel_charge

        # ==========================================
        # 3. 财务结算层：解耦扣款逻辑
        # ==========================================
        current_balance = self.customers[customer_id]["balance"]

        # 无论余额够不够，都直接扣减（允许出现负数余额/债务）
        self.customers[customer_id]["balance"] -= final_bill

        # 根据结算结果设置最终的订单状态
        if current_balance >= final_bill:
            booking_data["status"] = "Completed"
            payment_msg = "Payment successful."
        else:
            booking_data["status"] = "Completed_With_Debt"
            payment_msg = f"Insufficient balance. Account is now overdrawn by ${abs(self.customers[customer_id]['balance']):.2f}."

        booking_data["return_details"] = {
            "actual_return_date": self.system_date,
            "return_fuel": return_fuel_level,
            "fuel_charge_incurred": fuel_charge,
            "total_final_paid": final_bill
        }

        return {
            "status": "Vehicle physically returned.",
            "payment_status": payment_msg,
            "total_charged": final_bill,
            "new_balance": self.customers[customer_id]["balance"]
        }

    # ==========================================
    # 补充的新功能方法
    # ==========================================

    def advance_time(self, days: int) -> Dict[str, Union[str, int]]:
        """
        Advance the simulated system date by a specified number of days.
        
        Args:
            days (int): The number of days to advance. Must be greater than 0.
            
        Returns:
            Dict[str, Union[str, int]]: Status message and new system date, or error.
        """
        if not isinstance(days, int) or days <= 0:
            return {"error": "Days to advance must be a positive integer."}
        
        try:
            current_date = self._get_sys_date()
            new_date = current_date + timedelta(days=days)
            self.system_date = new_date.strftime("%Y-%m-%d")
            return {"status": "Time advanced successfully.", "new_system_date": self.system_date, "days_advanced": days}
        except Exception as e:
            return {"error": f"Failed to advance time: {str(e)}"}

    def add_funds(self, amount: float) -> Dict[str, Union[str, float]]:
        """
        Add funds to the current authenticated user's account balance.
        
        Args:
            amount (float): The amount to add. Must be greater than 0.
            
        Returns:
            Dict[str, Union[str, float]]: Status message and new balance, or error.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
        
        if not isinstance(amount, (int, float)) or amount <= 0:
            return {"error": "Amount must be a positive number."}
            
        self.customers[self.current_user]["balance"] += float(amount)
        return {
            "status": f"Successfully added ${amount:.2f} to account.",
            "new_balance": self.customers[self.current_user]["balance"]
        }

    def renew_drivers_license(self, new_expiry_date: str) -> Dict[str, str]:
        """
        Renew or update the drivers license validity date for the current user.
        
        Args:
            new_expiry_date (str): The new expiration date in YYYY-MM-DD format.
            
        Returns:
            Dict[str, str]: Status message or error.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
            
        try:
            new_date = self._get_date(new_expiry_date)
            sys_date = self._get_sys_date()
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD."}
            
        if new_date <= sys_date:
            return {"error": "New expiry date must be in the future relative to the system date."}
            
        self.customers[self.current_user]["license_valid_until"] = new_expiry_date
        return {"status": f"Drivers license renewed until {new_expiry_date}."}

    def get_my_bookings(self) -> Dict[str, Union[str, List[dict]]]:
        """
        Retrieve all historical and active bookings for the current authenticated user.
        
        Returns:
            Dict[str, Union[str, List[dict]]]: List of bookings or error.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
            
        user_bookings = []
        for bid, bdetails in self.bookings.items():
            if bdetails["customer"] == self.current_user:
                user_bookings.append(bdetails)
                
        if not user_bookings:
            return {"message": "No bookings found for the current user."}
            
        return {"results": user_bookings}

    def get_vehicle_details(self, vehicle_id: str) -> Dict[str, Union[str, dict]]:
        """
        Retrieve detailed information for a specific vehicle by its ID.
        
        Args:
            vehicle_id (str): The ID of the vehicle to query.
            
        Returns:
            Dict[str, Union[str, dict]]: Vehicle details or error.
        """
        if vehicle_id not in self.vehicles:
            return {"error": f"Vehicle {vehicle_id} not found."}
            
        return {"results": self.vehicles[vehicle_id]}

    def set_vehicle_maintenance_status(self, vehicle_id: str, under_maintenance: bool) -> Dict[str, str]:
        """
        System/admin operation to set a vehicle into or out of maintenance.
        
        Args:
            vehicle_id (str): The ID of the vehicle.
            under_maintenance (bool): True to set to Maintenance, False to set to Available.
            
        Returns:
            Dict[str, str]: Status message or error.
        """
        if vehicle_id not in self.vehicles:
            return {"error": f"Vehicle {vehicle_id} not found."}
            
        current_status = self.vehicles[vehicle_id]["status"]
        
        if under_maintenance:
            if current_status == "Maintenance":
                return {"error": f"Vehicle {vehicle_id} is already in Maintenance."}
            elif current_status == "Rented":
                return {"error": f"Cannot put vehicle {vehicle_id} into maintenance while it is rented."}
                
            self.vehicles[vehicle_id]["status"] = "Maintenance"
            return {"status": f"Vehicle {vehicle_id} is now under maintenance."}
        else:
            if current_status != "Maintenance":
                return {"error": f"Vehicle {vehicle_id} is not currently under maintenance."}
                
            self.vehicles[vehicle_id]["status"] = "Available"
            return {"status": f"Vehicle {vehicle_id} is now available."}

    def modify_booking_dates(self, booking_id: int, new_start_date: str, new_end_date: str) -> Dict[str, Union[str, float]]:
        """
        Modify the dates of a booking that has not yet started.
        
        Args:
            booking_id (int): The ID of the booking to modify.
            new_start_date (str): The new start date in YYYY-MM-DD format.
            new_end_date (str): The new end date in YYYY-MM-DD format.
            
        Returns:
            Dict[str, Union[str, float]]: Status message and new estimated cost, or error.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
            
        if booking_id not in self.bookings:
            return {"error": "Booking not found."}
            
        booking_data = self.bookings[booking_id]
        if booking_data["customer"] != self.current_user:
            return {"error": "Unauthorized access to this booking."}
            
        if booking_data["status"] != "Reserved":
            return {"error": f"Cannot modify dates for booking with status '{booking_data['status']}'."}
            
        try:
            req_start = self._get_date(new_start_date)
            req_end = self._get_date(new_end_date)
            sys_date = self._get_sys_date()
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD."}
            
        if req_start < sys_date or req_end <= req_start:
            return {"error": "Invalid date range. Cannot search in the past, and end date must be after start date."}
            
        customer_data = self.customers[self.current_user]
        if self._get_date(customer_data["license_valid_until"]) <= req_end:
            return {"error": "Cannot modify. Your drivers license will be expired at the end of the rental."}

        vehicle_id = booking_data["vehicle_id"]
        vdetails = self.vehicles[vehicle_id]
        
        if vdetails["status"] == "Maintenance":
            return {"error": f"Vehicle {vehicle_id} is currently under maintenance."}

        # Check for conflicts, ignoring the current booking
        is_conflicted = False
        for bid, bdetails in self.bookings.items():
            if bid == booking_id:
                continue
            if bdetails["vehicle_id"] == vehicle_id and bdetails["status"] in ["Reserved", "Active"]:
                book_start = self._get_date(bdetails["start_date"])
                book_end = self._get_date(bdetails["end_date"])
                if (req_start < book_end) and (req_end > book_start):
                    is_conflicted = True
                    break
                    
        if is_conflicted:
            return {"error": f"Vehicle {vehicle_id} is not available for these dates due to a conflict."}
            
        # Calculate new cost
        days = (req_end - req_start).days
        price_per_day = vdetails["price_per_day"]
        new_estimated_cost = days * price_per_day
        
        if customer_data["balance"] < new_estimated_cost:
            return {"error": f"Insufficient balance for new estimated cost ${new_estimated_cost:.2f}."}
            
        booking_data["start_date"] = new_start_date
        booking_data["end_date"] = new_end_date
        booking_data["total_estimated_cost"] = new_estimated_cost
        
        return {
            "status": "Booking dates modified successfully.",
            "new_start_date": new_start_date,
            "new_end_date": new_end_date,
            "new_total_estimated_cost": new_estimated_cost
        }

    def get_all_bookings(self, status_filter: Optional[str] = None) -> Dict[str, Union[str, List[dict]]]:
        """
        Retrieve all bookings in the system, optionally filtered by status.
        
        Args:
            status_filter (Optional[str]): The status to filter by (e.g., 'Active', 'Completed_With_Debt').
            
        Returns:
            Dict[str, Union[str, List[dict]]]: List of bookings or error.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
            
        results = []
        for bid, bdetails in self.bookings.items():
            if status_filter:
                if bdetails["status"].lower() == status_filter.lower():
                    results.append(bdetails)
            else:
                results.append(bdetails)
                
        return {"results": results}

    def update_vehicle_price(self, vehicle_id: str, new_price_per_day: float) -> Dict[str, Union[str, float]]:
        """
        Update the daily rental price of a specific vehicle.
        
        Args:
            vehicle_id (str): The ID of the vehicle.
            new_price_per_day (float): The new price per day.
            
        Returns:
            Dict[str, Union[str, float]]: Status message and new price, or error.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
            
        if vehicle_id not in self.vehicles:
            return {"error": f"Vehicle {vehicle_id} not found."}
            
        if not isinstance(new_price_per_day, (int, float)) or new_price_per_day <= 0:
            return {"error": "Price must be a positive number."}
            
        self.vehicles[vehicle_id]["price_per_day"] = float(new_price_per_day)
        return {
            "status": f"Successfully updated price for {vehicle_id}.",
            "new_price_per_day": float(new_price_per_day)
        }

    def list_all_vehicles(self, sort_by: Optional[str] = None) -> Dict[str, Union[str, List[dict]]]:
        """
        List all vehicles in the fleet, optionally sorted.
        
        Args:
            sort_by (Optional[str]): Field to sort by ('price_per_day', 'mileage', 'status').
            
        Returns:
            Dict[str, Union[str, List[dict]]]: Sorted list of all vehicles or error.
        """
        vehicles_list = []
        for vid, vdetails in self.vehicles.items():
            v_copy = deepcopy(vdetails)
            v_copy["vehicle_id"] = vid
            vehicles_list.append(v_copy)
            
        if sort_by:
            if sort_by not in ['price_per_day', 'mileage', 'status']:
                return {"error": "Invalid sort field. Use 'price_per_day', 'mileage', or 'status'."}
            try:
                vehicles_list.sort(key=lambda x: x[sort_by])
            except Exception as e:
                return {"error": f"Sorting failed: {str(e)}"}
                
        return {"results": vehicles_list}

    def pay_outstanding_debt(self) -> Dict[str, Union[str, float]]:
        """
        Pay off any outstanding debt (negative balance) for the current user.
        
        Returns:
            Dict[str, Union[str, float]]: Status message and amount paid, or error.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
            
        current_balance = self.customers[self.current_user]["balance"]
        if current_balance >= 0:
            return {"message": "No outstanding debt to pay.", "balance": current_balance}
            
        amount_to_pay = abs(current_balance)
        self.customers[self.current_user]["balance"] = 0.0
        
        return {
            "status": "Outstanding debt paid successfully.",
            "amount_paid": amount_to_pay,
            "new_balance": 0.0
        }


__TEST_CASES__ = [
    {
        'name': 'Normal path - Search and Create Booking',
        'steps': [
            {'expect_success': True, 'tool_call': "env['car_rental'].login(username='customer_a')"},
            {
                'expect_success': True,
                'tool_call': "env['car_rental'].search_available_vehicles(start_date='2026-05-10', end_date='2026-05-15', car_type=None)"
            },
            {
                'expect_success': True,
                'tool_call': "env['car_rental'].search_available_vehicles(start_date='2026-05-10', end_date='2026-05-15', car_type='Sedan')"
            },
            {
                'expect_success': True,
                'tool_call': "env['car_rental'].create_booking(vehicle_id='CAR-001', start_date='2026-05-10', end_date='2026-05-15')"
            }
        ]
    },
    {
        'name': 'Normal path and Boundary values - Return active vehicle with zero added mileage',
        'steps': [
            {'expect_success': True, 'tool_call': "env['car_rental'].login(username='customer_a')"},
            {
                'expect_success': True,
                'tool_call': "env['car_rental'].return_vehicle(booking_id=10001, return_fuel_level=0, added_mileage=0)"
            }
        ]
    },
    {
        'name': 'Cross-method workflow - Full lifecycle from create to return',
        'steps': [
            {'expect_success': True, 'tool_call': "env['car_rental'].login(username='customer_a')"},
            {
                'expect_success': True,
                'tool_call': "env['car_rental'].create_booking(vehicle_id='CAR-001', start_date='2026-05-03', end_date='2026-05-06')"
            },
            {'expect_success': True, 'tool_call': "env['car_rental'].pickup_vehicle(booking_id=10002)"},
            {
                'expect_success': True,
                'tool_call': "env['car_rental'].return_vehicle(booking_id=10002, return_fuel_level=90, added_mileage=50)"
            }
        ]
    },
    {
        'name': 'Cross-method workflow - Create and cancel booking',
        'steps': [
            {'expect_success': True, 'tool_call': "env['car_rental'].login(username='customer_a')"},
            {
                'expect_success': True,
                'tool_call': "env['car_rental'].create_booking(vehicle_id='CAR-001', start_date='2026-06-01', end_date='2026-06-05')"
            },
            {'expect_success': True, 'tool_call': "env['car_rental'].cancel_booking(booking_id=10002)"}
        ]
    },
    {
        'name': 'Error path - Create Booking with Insufficient Balance',
        'steps': [
            {'expect_success': True, 'tool_call': "env['car_rental'].login(username='customer_b')"},
            {
                'expect_success': False,
                'tool_call': "env['car_rental'].create_booking(vehicle_id='CAR-001', start_date='2026-05-10', end_date='2026-05-20')"
            }
        ]
    },
    {
        'name': 'Error path - Invalid IDs and non-existent records',
        'steps': [
            {'expect_success': True, 'tool_call': "env['car_rental'].login(username='customer_a')"},
            {
                'expect_success': False,
                'tool_call': "env['car_rental'].create_booking(vehicle_id='CAR-999', start_date='2026-05-10', end_date='2026-05-15')"
            },
            {'expect_success': False, 'tool_call': "env['car_rental'].cancel_booking(booking_id=99999)"},
            {'expect_success': False, 'tool_call': "env['car_rental'].pickup_vehicle(booking_id=99999)"},
            {
                'expect_success': False,
                'tool_call': "env['car_rental'].return_vehicle(booking_id=99999, return_fuel_level=100, added_mileage=100)"
            }
        ]
    },
    {
        'name': 'Error path - Unauthenticated access to protected methods',
        'steps': [
            {
                'expect_success': False,
                'tool_call': "env['car_rental'].create_booking(vehicle_id='CAR-001', start_date='2026-05-10', end_date='2026-05-15')"
            },
            {'expect_success': False, 'tool_call': "env['car_rental'].pickup_vehicle(booking_id=10001)"}
        ]
    },
    {
        'name': 'Boundary values - Empty strings, negative values, and invalid dates',
        'steps': [
            {'expect_success': True, 'tool_call': "env['car_rental'].login(username='customer_a')"},
            {
                'expect_success': False,
                'tool_call': "env['car_rental'].search_available_vehicles(start_date='', end_date='', car_type='')"
            },
            {
                'expect_success': False,
                'tool_call': "env['car_rental'].create_booking(vehicle_id='CAR-001', start_date='2026-05-15', end_date='2026-05-10')"
            },
            {
                'expect_success': False,
                'tool_call': "env['car_rental'].return_vehicle(booking_id=10001, return_fuel_level=-10, added_mileage=-50)"
            },
            {
                'expect_success': False,
                'tool_call': "env['car_rental'].search_available_vehicles(start_date='2026-05-10', end_date='2026-05-15', car_type='A_VERY_LONG_CAR_TYPE_STRING_THAT_EXCEEDS_NORMAL_LENGTH_LIMITS')"
            }
        ]
    },
    {
        'name': 'Error path - Pickup vehicle before start date',
        'steps': [
            {'expect_success': True, 'tool_call': "env['car_rental'].login(username='customer_a')"},
            {
                'expect_success': True,
                'tool_call': "env['car_rental'].create_booking(vehicle_id='CAR-001', start_date='2026-05-10', end_date='2026-05-15')"
            },
            {'expect_success': False, 'tool_call': "env['car_rental'].pickup_vehicle(booking_id=10002)"}
        ]
    },
    {
        'name': 'State-change verification - Create booking and verify state',
        'steps': [
            {'expect_success': True, 'tool_call': "env['car_rental'].login(username='customer_a')"},
            {
                'expect_success': True,
                'tool_call': "env['car_rental'].create_booking(vehicle_id='CAR-001', start_date='2026-05-04', end_date='2026-05-05')"
            },
            {'expect_success': True, 'tool_call': "env['car_rental'].get_env_state()"}
        ]
    },
    {
        'name': 'New Method - advance_time',
        'steps': [
            {'expect_success': True, 'tool_call': "env['car_rental'].advance_time(days=2)"},
            {'expect_success': False, 'tool_call': "env['car_rental'].advance_time(days=-1)"}
        ]
    },
    {
        'name': 'New Method - add_funds',
        'steps': [
            {'expect_success': True, 'tool_call': "env['car_rental'].login(username='customer_b')"},
            {'expect_success': True, 'tool_call': "env['car_rental'].add_funds(amount=100.0)"},
            {'expect_success': False, 'tool_call': "env['car_rental'].add_funds(amount=-50.0)"}
        ]
    },
    {
        'name': 'New Method - renew_drivers_license',
        'steps': [
            {'expect_success': True, 'tool_call': "env['car_rental'].login(username='customer_b')"},
            {'expect_success': True, 'tool_call': "env['car_rental'].renew_drivers_license(new_expiry_date='2030-01-01')"},
            {'expect_success': False, 'tool_call': "env['car_rental'].renew_drivers_license(new_expiry_date='2020-01-01')"},
            {'expect_success': False, 'tool_call': "env['car_rental'].renew_drivers_license(new_expiry_date='invalid-date')"}
        ]
    },
    {
        'name': 'New Method - get_my_bookings',
        'steps': [
            {'expect_success': False, 'tool_call': "env['car_rental'].get_my_bookings()"},
            {'expect_success': True, 'tool_call': "env['car_rental'].login(username='customer_a')"},
            {'expect_success': True, 'tool_call': "env['car_rental'].get_my_bookings()"}
        ]
    },
    {
        'name': 'New Method - get_vehicle_details',
        'steps': [
            {'expect_success': True, 'tool_call': "env['car_rental'].get_vehicle_details(vehicle_id='CAR-001')"},
            {'expect_success': False, 'tool_call': "env['car_rental'].get_vehicle_details(vehicle_id='CAR-999')"}
        ]
    },
    {
        'name': 'New Method - set_vehicle_maintenance_status',
        'steps': [
            {'expect_success': True, 'tool_call': "env['car_rental'].set_vehicle_maintenance_status(vehicle_id='CAR-001', under_maintenance=True)"},
            {'expect_success': True, 'tool_call': "env['car_rental'].set_vehicle_maintenance_status(vehicle_id='CAR-001', under_maintenance=False)"},
            {'expect_success': False, 'tool_call': "env['car_rental'].set_vehicle_maintenance_status(vehicle_id='SUV-001', under_maintenance=True)"},
            {'expect_success': False, 'tool_call': "env['car_rental'].set_vehicle_maintenance_status(vehicle_id='INVALID', under_maintenance=True)"}
        ]
    },
    {
        'name': 'New Method - modify_booking_dates',
        'steps': [
            {'expect_success': True, 'tool_call': "env['car_rental'].login(username='customer_a')"},
            {'expect_success': True, 'tool_call': "env['car_rental'].create_booking(vehicle_id='CAR-001', start_date='2026-06-01', end_date='2026-06-05')"},
            {'expect_success': True, 'tool_call': "env['car_rental'].modify_booking_dates(booking_id=10002, new_start_date='2026-06-02', new_end_date='2026-06-06')"},
            {'expect_success': False, 'tool_call': "env['car_rental'].modify_booking_dates(booking_id=10002, new_start_date='2025-06-02', new_end_date='2025-06-06')"}
        ]
    },
    {
        'name': 'New Method - get_all_bookings',
        'steps': [
            {'expect_success': True, 'tool_call': "env['car_rental'].login(username='customer_a')"},
            {'expect_success': True, 'tool_call': "env['car_rental'].get_all_bookings()"},
            {'expect_success': True, 'tool_call': "env['car_rental'].get_all_bookings(status_filter='Active')"}
        ]
    },
    {
        'name': 'New Method - update_vehicle_price',
        'steps': [
            {'expect_success': True, 'tool_call': "env['car_rental'].login(username='customer_a')"},
            {'expect_success': True, 'tool_call': "env['car_rental'].update_vehicle_price(vehicle_id='CAR-001', new_price_per_day=75.0)"},
            {'expect_success': False, 'tool_call': "env['car_rental'].update_vehicle_price(vehicle_id='CAR-001', new_price_per_day=-10.0)"}
        ]
    },
    {
        'name': 'New Method - list_all_vehicles',
        'steps': [
            {'expect_success': True, 'tool_call': "env['car_rental'].list_all_vehicles()"},
            {'expect_success': True, 'tool_call': "env['car_rental'].list_all_vehicles(sort_by='price_per_day')"},
            {'expect_success': False, 'tool_call': "env['car_rental'].list_all_vehicles(sort_by='invalid_sort')"}
        ]
    },
    {
        'name': 'New Method - pay_outstanding_debt with debt',
        'steps': [
            {'expect_success': True, 'tool_call': "env['car_rental'].login(username='customer_a')"},
            {'expect_success': True, 'tool_call': "env['car_rental'].advance_time(days=10)"},
            {'expect_success': True, 'tool_call': "env['car_rental'].return_vehicle(booking_id=10001, return_fuel_level=0, added_mileage=1000)"},
            {'expect_success': True, 'tool_call': "env['car_rental'].pay_outstanding_debt()"}
        ]
    }
]