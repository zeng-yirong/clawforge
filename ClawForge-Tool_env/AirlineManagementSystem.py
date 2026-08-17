import random
from copy import deepcopy
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta
import string

# 自定义初始状态
DEFAULT_STATE = {
    "generated_reservation_ids": set(),
    "generated_payment_ids": set(),
    "users": {
        "sara_doe_496": {
            "user_id": "sara_doe_496",
            "name": "Sara Doe",
            "payment_methods": {
                "credit_card_123": {"payment_id": "credit_card_123", "source": "credit_card", "amount": 1000},
                "gift_card_456": {"payment_id": "gift_card_456", "source": "gift_card", "amount": 200},
            },
            "reservations": []
        }
    },
    "flights": {
        "FL123": {
            "flight_number": "FL123",
            "origin": "JFK",
            "destination": "LAX",
            "scheduled_departure_time_est": "10:00:00",
            "scheduled_arrival_time_est": "13:00:00",
            "dates": {
                "2024-05-15": {
                    "status": "available",
                    "available_seats": {"economy": 100, "business": 20},
                    "prices": {"economy": 200, "business": 600}
                }
            }
        }
    },
    "reservations": {}
}


class AirlineAPI:
    """
    A class representing an Airline API for managing flights, users, and reservations.
    """

    def __init__(self):
        """
        Initialize the AirlineAPI with default structures.
        """
        self.generated_reservation_ids: set
        self.generated_payment_ids: set
        self.users: Dict[str, dict]
        self.flights: Dict[str, dict]
        self.reservations: Dict[str, dict]
        self._api_description = "This tool belongs to the Airline API, which is used to manage airline reservations and flights."

    def _load_scenario(self, scenario: dict, long_context: Optional[dict] = None) -> None:
        """
        Load a scenario into the AirlineAPI.

        Args:
            scenario: A dictionary containing scenario states to load.
            long_context: Optional long context (for compatibility).
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self._random = random.Random((scenario.get("random_seed", 42)))

        # 深拷贝所有可变对象，防止状态污染
        self.generated_reservation_ids = set(
            deepcopy(scenario.get("generated_reservation_ids", DEFAULT_STATE_COPY["generated_reservation_ids"])))
        self.generated_payment_ids = set(
            deepcopy(scenario.get("generated_payment_ids", DEFAULT_STATE_COPY["generated_payment_ids"])))
        self.users = deepcopy(scenario.get("users", DEFAULT_STATE_COPY["users"]))
        self.flights = deepcopy(scenario.get("flights", DEFAULT_STATE_COPY["flights"]))
        self.reservations = deepcopy(scenario.get("reservations", DEFAULT_STATE_COPY["reservations"]))

    def get_env_state(self) -> dict:
        """
        Get the current environment state.

        Returns:
            A dictionary containing the environment states.
        """
        return {
            "generated_reservation_ids": list(self.generated_reservation_ids),
            "generated_payment_ids": list(self.generated_payment_ids),
            "users": self.users,
            "flights": self.flights,
            "reservations": self.reservations
        }

    # ==========================================
    # Helper Methods
    # ==========================================

    def _get_user(self, user_id: str) -> dict:
        if user_id not in self.users:
            return {"error": f"User {user_id} not found"}
        return self.users[user_id]

    def _get_reservation(self, reservation_id: str) -> dict:
        if reservation_id not in self.reservations:
            return {"error": f"Reservation {reservation_id} not found"}
        return self.reservations[reservation_id]

    def _get_flight(self, flight_number: str) -> dict:
        if flight_number not in self.flights:
            return {"error": f"Flight {flight_number} not found"}
        return self.flights[flight_number]

    def _get_flight_instance(self, flight_number: str, date: str) -> dict:
        flight = self._get_flight(flight_number)
        if "error" in flight:
            return flight
        if date not in flight["dates"]:
            return {"error": f"Flight {flight_number} not found on date {date}"}
        return flight["dates"][date]

    def _generate_unique_reservation_id(self) -> Union[str, dict]:
        """生成唯一预订ID，并写入状态集合"""
        for _ in range(1000):  # 安全防死循环
            new_id = ''.join(self._random.choices(string.ascii_uppercase + string.digits, k=8))
            if new_id not in self.generated_reservation_ids and new_id not in self.reservations:
                self.generated_reservation_ids.add(new_id)
                return new_id
        return {"error": "Too many reservations"}

    def _generate_unique_payment_id(self) -> Union[str, dict]:
        """生成唯一支付ID，并写入状态集合"""
        for _ in range(1000):
            new_id = str(self._random.randint(1000000, 9999999))
            if new_id not in self.generated_payment_ids:
                self.generated_payment_ids.add(new_id)
                return new_id
        return {"error": "Too many payment IDs"}

    def _timestamp(self) -> str:
        return "2024-05-15T15:00:00"

    def _search_direct_flight(
            self,
            date: str,
            origin: Optional[str] = None,
            destination: Optional[str] = None,
            leave_after: Optional[str] = None,
    ) -> List[dict]:
        results = []
        for flight in self.flights.values():
            check = (
                    (origin is None or flight["origin"] == origin)
                    and (destination is None or flight["destination"] == destination)
                    and (date in flight["dates"])
                    and (flight["dates"][date]["status"] == "available")
                    and (
                            leave_after is None
                            or flight["scheduled_departure_time_est"] >= leave_after
                    )
            )
            if check:
                direct_flight = {
                    "flight_number": flight["flight_number"],
                    "origin": flight["origin"],
                    "destination": flight["destination"],
                    "status": "available",
                    "scheduled_departure_time_est": flight["scheduled_departure_time_est"],
                    "scheduled_arrival_time_est": flight["scheduled_arrival_time_est"],
                    "available_seats": flight["dates"][date]["available_seats"],
                    "prices": flight["dates"][date]["prices"],
                }
                results.append(direct_flight)
        return results

    def _process_payment(self, user: dict, payment_id: str, amount: int) -> dict:
        """
        处理扣款或退款，返回支付记录。
        amount为正：扣款；为负：退款。
        返回字典或错误字典。
        """
        if payment_id not in user["payment_methods"]:
            return {"error": "Payment method not found"}
        payment_method = user["payment_methods"][payment_id]

        # 校验支付方式余额
        if amount > 0:
            if payment_method["source"] == "certificate":
                return {"error": "Certificate cannot be used for additional payment"}
            if payment_method["amount"] < amount:
                return {"error": f"Not enough balance in payment method {payment_id}"}

        # 扣款/退款
        if payment_method["source"] == "gift_card":
            payment_method["amount"] -= amount
        elif payment_method["source"] == "credit_card":
            # 信用卡无余额概念，但允许负数记录（退款）
            payment_method["amount"] -= amount  # 记录账目变化
        elif payment_method["source"] == "certificate":
            # 证书不可以被扣款，退款时重新添加
            if amount < 0:
                # 退款：构建一个新的证书（原来已被删除）
                user["payment_methods"][payment_id] = {
                    "payment_id": payment_id,
                    "amount": -amount,
                    "source": "certificate",
                }
            else:
                return {"error": "Certificate cannot be used for payment"}

        # 返回支付记录
        if amount != 0:
            return {"payment_id": payment_id, "amount": amount}
        return None

    # ==========================================
    # Tool Methods
    # ==========================================

    def book_reservation(
            self,
            user_id: str,
            origin: str,
            destination: str,
            flight_type: str,
            cabin: str,
            flights: List[dict],
            passengers: List[dict],
            payment_methods: List[dict],
            total_baggages: int,
            nonfree_baggages: int,
            insurance: str,
    ) -> dict:
        user = self._get_user(user_id)
        if "error" in user:
            return {"success": False, "error": user["error"]}

        # 参数校验
        if cabin not in ("economy", "business"):
            return {"success": False, "error": f"Invalid cabin: {cabin}. Must be 'economy' or 'business'."}
        if insurance not in ("yes", "no"):
            return {"success": False, "error": f"Invalid insurance option: {insurance}. Must be 'yes' or 'no'."}
        for p in passengers:
            if not isinstance(p, dict) or "first_name" not in p or "last_name" not in p:
                return {"success": False, "error": "Each passenger must have 'first_name' and 'last_name' fields."}
            if not p["first_name"] or not p["last_name"]:
                return {"success": False, "error": "Passenger name fields cannot be empty."}
        if nonfree_baggages < 0 or total_baggages < nonfree_baggages:
            return {"success": False, "error": "Invalid baggage count."}

        reservation_id = self._generate_unique_reservation_id()
        if isinstance(reservation_id, dict) and "error" in reservation_id:
            return {"success": False, "error": reservation_id["error"]}

        reservation = {
            "reservation_id": reservation_id,
            "user_id": user_id,
            "origin": origin,
            "destination": destination,
            "flight_type": flight_type,
            "cabin": cabin,
            "flights": [],
            "passengers": deepcopy(passengers),
            "payment_history": deepcopy(payment_methods),
            "created_at": self._timestamp(),
            "total_baggages": total_baggages,
            "nonfree_baggages": nonfree_baggages,
            "insurance": insurance,
            "status": "active"
        }

        total_price = 0
        all_flights_date_data = []

        for flight_info in flights:
            flight_number = flight_info["flight_number"]
            flight = self._get_flight(flight_number)
            if "error" in flight:
                return {"success": False, "error": flight["error"]}

            flight_date_data = self._get_flight_instance(flight_number, flight_info["date"])
            if "error" in flight_date_data:
                return {"success": False, "error": flight_date_data["error"]}

            if flight_date_data["status"] != "available":
                return {"success": False, "error": f"Flight {flight_number} not available on date {flight_info['date']}"}
            if flight_date_data["available_seats"].get(cabin, 0) < len(passengers):
                return {"success": False, "error": f"Not enough seats on flight {flight_number}"}

            price = flight_date_data["prices"][cabin]
            reservation["flights"].append({
                "origin": flight["origin"],
                "destination": flight["destination"],
                "flight_number": flight_number,
                "date": flight_info["date"],
                "price": price,
            })
            all_flights_date_data.append(flight_date_data)
            total_price += price * len(passengers)

        if insurance == "yes":
            total_price += 30 * len(passengers)

        total_price += 50 * nonfree_baggages

        # 校验支付方式余额（包括信用卡）
        for pm in payment_methods:
            payment_id = pm["payment_id"]
            amount = pm["amount"]
            if payment_id not in user["payment_methods"]:
                return {"success": False, "error": f"Payment method {payment_id} not found"}
            user_pm = user["payment_methods"][payment_id]
            # 信用卡增加余额校验
            if user_pm["source"] in ("gift_card", "certificate"):
                if user_pm["amount"] < amount:
                    return {"success": False, "error": f"Not enough balance in payment method {payment_id}"}
            elif user_pm["source"] == "credit_card":
                if user_pm["amount"] < amount:
                    return {"success": False, "error": f"Credit card limit exceeded in {payment_id}"}
            else:
                return {"success": False, "error": f"Unknown payment source: {user_pm['source']}"}

        total_payment = sum(pm["amount"] for pm in payment_methods)
        if total_payment != total_price:
            return {"success": False, "error": f"Payment amount does not add up, total price is {total_price}, but paid {total_payment}"}

        # 扣款
        for pm in payment_methods:
            payment_id = pm["payment_id"]
            amount = pm["amount"]
            result = self._process_payment(user, payment_id, amount)
            if result is not None and "error" in result:
                return {"success": False, "error": result["error"]}

        # Update DB
        for flight_date_data in all_flights_date_data:
            flight_date_data["available_seats"][cabin] -= len(passengers)

        self.reservations[reservation_id] = reservation
        user["reservations"].append(reservation_id)

        return {"success": True, "data": reservation}

    def calculate(self, expression: str) -> dict:
        if not expression:
            return {"success": False, "error": "Empty expression"}
        if not all(char in "0123456789+-*/(). " for char in expression):
            return {"success": False, "error": "Invalid characters in expression"}
        try:
            result = str(round(float(eval(expression, {"__builtins__": None}, {})), 2))
            return {"success": True, "data": result}
        except Exception as e:
            return {"success": False, "error": f"Invalid expression: {e}"}

    def cancel_reservation(self, reservation_id: str) -> dict:
        reservation = self._get_reservation(reservation_id)
        if "error" in reservation:
            return {"success": False, "error": reservation["error"]}

        # 状态约束：只有active/checked_in可取消；已完成不可取消
        if reservation.get("status") == "cancelled":
            return {"success": False, "error": f"Reservation {reservation_id} is already cancelled."}
        if reservation.get("status") == "completed":
            return {"success": False, "error": f"Reservation {reservation_id} is completed and cannot be cancelled."}

        user = self._get_user(reservation["user_id"])
        if "error" in user:
            return {"success": False, "error": user["error"]}

        # 2. 财务层：处理退款（恢复支付方式余额/代金券）
        refunds = []
        for payment in reservation["payment_history"]:
            if payment["amount"] > 0:
                refunds.append({
                    "payment_id": payment["payment_id"],
                    "amount": -payment["amount"],
                })
        for refund in refunds:
            # 注意：payment_id可能已从用户支付方式中删除（如certificate），需要重新处理
            result = self._process_payment(user, refund["payment_id"], refund["amount"])
            if result is not None and "error" in result:
                # 如果出错（比如payment_id失效），记录但不阻断（应尽量恢复）
                pass

        reservation["payment_history"].extend(refunds)

        # 3. 物理资源层：释放座位
        num_passengers = len(reservation["passengers"])
        cabin = reservation["cabin"]
        for flight_info in reservation["flights"]:
            flight_number = flight_info["flight_number"]
            date = flight_info["date"]
            flight_date_data = self._get_flight_instance(flight_number, date)
            if "error" not in flight_date_data:
                if cabin in flight_date_data["available_seats"]:
                    flight_date_data["available_seats"][cabin] += num_passengers
                else:
                    flight_date_data["available_seats"][cabin] = num_passengers

        # 4. 状态流转
        reservation["status"] = "cancelled"

        # 同步用户列表（取消后保留在列表中，状态已更新）
        return {"success": True, "data": reservation}

    def get_reservation_details(self, reservation_id: str) -> dict:
        res = self._get_reservation(reservation_id)
        if "error" in res:
            return {"success": False, "error": res["error"]}
        return {"success": True, "data": res}

    def get_user_details(self, user_id: str) -> dict:
        user = self._get_user(user_id)
        if "error" in user:
            return {"success": False, "error": user["error"]}
        return {"success": True, "data": user}

    def list_all_airports(self) -> dict:
        airports = [
            {"iata": "SFO", "city": "San Francisco"},
            {"iata": "JFK", "city": "New York"},
            {"iata": "LAX", "city": "Los Angeles"},
            {"iata": "ORD", "city": "Chicago"},
            {"iata": "DFW", "city": "Dallas"},
            {"iata": "DEN", "city": "Denver"},
            {"iata": "SEA", "city": "Seattle"},
            {"iata": "ATL", "city": "Atlanta"},
            {"iata": "MIA", "city": "Miami"},
            {"iata": "BOS", "city": "Boston"},
            {"iata": "PHX", "city": "Phoenix"},
            {"iata": "IAH", "city": "Houston"},
            {"iata": "LAS", "city": "Las Vegas"},
            {"iata": "MCO", "city": "Orlando"},
            {"iata": "EWR", "city": "Newark"},
            {"iata": "CLT", "city": "Charlotte"},
            {"iata": "MSP", "city": "Minneapolis"},
            {"iata": "DTW", "city": "Detroit"},
            {"iata": "PHL", "city": "Philadelphia"},
            {"iata": "LGA", "city": "LaGuardia"},
        ]
        return {"success": True, "data": airports}

    def search_direct_flight(self, origin: str, destination: str, date: str) -> dict:
        if not origin or not destination or not date:
            return {"success": False, "error": "Invalid input"}
        results = self._search_direct_flight(date=date, origin=origin, destination=destination)
        return {"success": True, "data": results}

    def search_onestop_flight(self, origin: str, destination: str, date: str) -> dict:
        if not origin or not destination or not date:
            return {"success": False, "error": "Invalid input"}
        results = []
        for result1 in self._search_direct_flight(date=date, origin=origin, destination=None):
            result1["date"] = date
            # 计算第二段日期：若到达时间含"+1"则次日，否则同一天
            if "+1" in result1["scheduled_arrival_time_est"]:
                # 使用datetime正确计算次日
                try:
                    dt = datetime.strptime(date, "%Y-%m-%d")
                    next_day = dt + timedelta(days=1)
                    date2 = next_day.strftime("%Y-%m-%d")
                except ValueError:
                    return {"success": False, "error": "Invalid date format"}
            else:
                date2 = date

            for result2 in self._search_direct_flight(
                    date=date2,
                    origin=result1["destination"],
                    destination=destination,
                    leave_after=result1["scheduled_arrival_time_est"].replace("+1", ""),
            ):
                result2["date"] = date2
                results.append([result1, result2])
        return {"success": True, "data": results}

    def send_certificate(self, user_id: str, amount: int) -> dict:
        if amount <= 0:
            return {"success": False, "error": "Amount must be greater than 0"}
        user = self._get_user(user_id)
        if "error" in user:
            return {"success": False, "error": user["error"]}

        payment_id = self._generate_unique_payment_id()
        if isinstance(payment_id, dict) and "error" in payment_id:
            return {"success": False, "error": payment_id["error"]}

        cert_id = f"certificate_{payment_id}"
        user["payment_methods"][cert_id] = {
            "payment_id": cert_id,
            "amount": amount,
            "source": "certificate",
        }
        return {"success": True, "data": f"Certificate {cert_id} added to user {user_id} with amount {amount}."}

    def transfer_to_human_agents(self, summary: str) -> dict:
        return {"success": True, "data": "Transfer successful"}

    def update_reservation_baggages(
            self,
            reservation_id: str,
            total_baggages: int,
            nonfree_baggages: int,
            payment_id: str,
    ) -> dict:
        reservation = self._get_reservation(reservation_id)
        if "error" in reservation:
            return {"success": False, "error": reservation["error"]}
        if reservation["status"] == "cancelled":
            return {"success": False, "error": "Cannot update a cancelled reservation."}
        if reservation["status"] == "completed":
            return {"success": False, "error": "Cannot update a completed reservation."}

        user = self._get_user(reservation["user_id"])
        if "error" in user:
            return {"success": False, "error": user["error"]}

        # 校验
        if nonfree_baggages < 0 or total_baggages < nonfree_baggages:
            return {"success": False, "error": "Invalid baggage count."}

        # 计算差价（只计算增加的付费行李费用）
        diff_nonfree = nonfree_baggages - reservation.get("nonfree_baggages", 0)
        total_price = 50 * max(0, diff_nonfree)

        # 退款处理（若减少付费行李需退款）
        if diff_nonfree < 0:
            total_price = 50 * diff_nonfree  # 负数

        payment = self._process_payment(user, payment_id, total_price)
        if payment is not None:
            if "error" in payment:
                return {"success": False, "error": payment["error"]}
            reservation["payment_history"].append(payment)

        reservation["total_baggages"] = total_baggages
        reservation["nonfree_baggages"] = nonfree_baggages

        return {"success": True, "data": reservation}

    def update_reservation_flights(
            self,
            reservation_id: str,
            cabin: str,
            flights: List[dict],
            payment_id: str,
    ) -> dict:
        reservation = self._get_reservation(reservation_id)
        if "error" in reservation:
            return {"success": False, "error": reservation["error"]}
        if reservation["status"] == "cancelled":
            return {"success": False, "error": "Cannot update a cancelled reservation."}
        if reservation["status"] == "completed":
            return {"success": False, "error": "Cannot update a completed reservation."}

        user = self._get_user(reservation["user_id"])
        if "error" in user:
            return {"success": False, "error": user["error"]}

        if cabin not in ("economy", "business"):
            return {"success": False, "error": f"Invalid cabin: {cabin}."}

        total_price = 0
        reservation_flights = []
        for flight_info in flights:
            matching_reservation_flight = next(
                (
                    rf for rf in reservation["flights"]
                    if rf["flight_number"] == flight_info["flight_number"]
                       and rf["date"] == flight_info["date"]
                ),
                None,
            )
            if matching_reservation_flight:
                total_price += matching_reservation_flight["price"] * len(reservation["passengers"])
                reservation_flights.append(matching_reservation_flight)
                continue

            flight = self._get_flight(flight_info["flight_number"])
            if "error" in flight:
                return {"success": False, "error": flight["error"]}

            flight_date_data = self._get_flight_instance(flight_info["flight_number"], flight_info["date"])
            if "error" in flight_date_data:
                return {"success": False, "error": flight_date_data["error"]}

            if flight_date_data["status"] != "available":
                return {"success": False, "error": f"Flight {flight_info['flight_number']} not available on date {flight_info['date']}"}

            if flight_date_data["available_seats"].get(cabin, 0) < len(reservation["passengers"]):
                return {"success": False, "error": f"Not enough seats on flight {flight_info['flight_number']}"}

            reservation_flight = {
                "flight_number": flight_info["flight_number"],
                "date": flight_info["date"],
                "price": flight_date_data["prices"][cabin],
                "origin": flight["origin"],
                "destination": flight["destination"],
            }
            total_price += reservation_flight["price"] * len(reservation["passengers"])
            reservation_flights.append(reservation_flight)

        old_price = sum(flight["price"] for flight in reservation["flights"]) * len(reservation["passengers"])
        price_diff = total_price - old_price

        # 处理支付/退款
        if price_diff != 0:
            payment = self._process_payment(user, payment_id, price_diff)
            if payment is not None and "error" in payment:
                return {"success": False, "error": payment["error"]}
            if payment is not None:
                reservation["payment_history"].append(payment)

        # Restore seats for old flights not in new ones
        for rf in reservation["flights"]:
            if rf not in reservation_flights:
                old_flight_data = self._get_flight_instance(rf["flight_number"], rf["date"])
                if "error" not in old_flight_data:
                    old_flight_data["available_seats"][reservation["cabin"]] += len(reservation["passengers"])

        # Deduct seats for new flights not in old ones
        for nf in reservation_flights:
            if nf not in reservation["flights"]:
                new_flight_data = self._get_flight_instance(nf["flight_number"], nf["date"])
                if "error" not in new_flight_data:
                    new_flight_data["available_seats"][cabin] -= len(reservation["passengers"])

        reservation["flights"] = reservation_flights
        reservation["cabin"] = cabin

        return {"success": True, "data": reservation}

    def update_reservation_passengers(
            self, reservation_id: str, passengers: List[dict]
    ) -> dict:
        reservation = self._get_reservation(reservation_id)
        if "error" in reservation:
            return {"success": False, "error": reservation["error"]}
        if reservation["status"] == "cancelled":
            return {"success": False, "error": "Cannot update a cancelled reservation."}
        if reservation["status"] == "completed":
            return {"success": False, "error": "Cannot update a completed reservation."}

        # 校验乘客信息格式
        for p in passengers:
            if not isinstance(p, dict) or "first_name" not in p or "last_name" not in p:
                return {"success": False, "error": "Each passenger must have 'first_name' and 'last_name' fields."}
            if not p["first_name"] or not p["last_name"]:
                return {"success": False, "error": "Passenger name fields cannot be empty."}

        if len(passengers) != len(reservation["passengers"]):
            return {"success": False, "error": "Number of passengers does not match"}
        reservation["passengers"] = deepcopy(passengers)
        return {"success": True, "data": reservation}

    def get_flight_status(self, flight_number: str, date: str) -> dict:
        if not flight_number or not date:
            return {"success": False, "error": "Invalid input"}
        res = self._get_flight_instance(flight_number, date)
        if "error" in res:
            return {"success": False, "error": res["error"]}
        return {"success": True, "data": res["status"]}

    def add_payment_method(self, user_id: str, source: str, amount: int) -> dict:
        if amount < 0:
            return {"success": False, "error": "Amount cannot be negative"}
        valid_sources = ("credit_card", "gift_card", "certificate", "bank_transfer")
        if source not in valid_sources:
            return {"success": False, "error": f"Invalid payment source: {source}. Must be one of {valid_sources}"}

        user = self._get_user(user_id)
        if "error" in user:
            return {"success": False, "error": user["error"]}

        payment_id = self._generate_unique_payment_id()
        if isinstance(payment_id, dict) and "error" in payment_id:
            return {"success": False, "error": payment_id["error"]}

        pm_id = f"{source}_{payment_id}"
        user["payment_methods"][pm_id] = {
            "payment_id": pm_id,
            "source": source,
            "amount": amount
        }
        return {"success": True, "data": {"payment_id": pm_id, "source": source, "amount": amount}}

    def check_in_flight(self, reservation_id: str) -> dict:
        reservation = self._get_reservation(reservation_id)
        if "error" in reservation:
            return {"success": False, "error": reservation["error"]}

        if reservation.get("status") != "active":
            return {"success": False, "error": f"Reservation {reservation_id} is not active. Current status: {reservation.get('status')}"}

        reservation["status"] = "checked_in"
        return {"success": True, "data": reservation}

    def quote_reservation_change(
            self,
            reservation_id: str,
            cabin: str,
            flights: List[dict]
    ) -> dict:
        reservation = self._get_reservation(reservation_id)
        if "error" in reservation:
            return {"success": False, "error": reservation["error"]}

        user = self._get_user(reservation["user_id"])
        if "error" in user:
            return {"success": False, "error": user["error"]}

        if cabin not in ("economy", "business"):
            return {"success": False, "error": f"Invalid cabin: {cabin}."}

        total_price = 0
        for flight_info in flights:
            matching_reservation_flight = next(
                (
                    rf for rf in reservation["flights"]
                    if rf["flight_number"] == flight_info["flight_number"]
                       and rf["date"] == flight_info["date"]
                ),
                None,
            )
            if matching_reservation_flight:
                total_price += matching_reservation_flight["price"] * len(reservation["passengers"])
                continue

            flight = self._get_flight(flight_info["flight_number"])
            if "error" in flight:
                return {"success": False, "error": flight["error"]}

            flight_date_data = self._get_flight_instance(flight_info["flight_number"], flight_info["date"])
            if "error" in flight_date_data:
                return {"success": False, "error": flight_date_data["error"]}

            if flight_date_data["status"] != "available":
                return {"success": False, "error": f"Flight {flight_info['flight_number']} not available on date {flight_info['date']}"}

            if flight_date_data["available_seats"].get(cabin, 0) < len(reservation["passengers"]):
                return {"success": False, "error": f"Not enough seats on flight {flight_info['flight_number']}"}

            total_price += flight_date_data["prices"][cabin] * len(reservation["passengers"])

        old_price = sum(flight["price"] for flight in reservation["flights"]) * len(reservation["passengers"])
        price_difference = total_price - old_price

        return {"success": True, "data": {
            "reservation_id": reservation_id,
            "old_price_total": old_price,
            "new_price_total": total_price,
            "price_difference": price_difference
        }}


__TEST_CASES__ = [
    {
        'name': 'End-to-end booking workflow (Cross-method, Normal path)',
        'steps': [
            {'expect_success': True, 'tool_call': "env['airline'].search_direct_flight(origin='JFK', destination='LAX', date='2024-05-15')"},
            {'expect_success': True, 'tool_call': "env['airline'].book_reservation(user_id='sara_doe_496', origin='JFK', destination='LAX', flight_type='direct', cabin='economy', flights=[{'flight_number': 'FL123', 'date': '2024-05-15'}], passengers=[{'first_name': 'Sara', 'last_name': 'Doe'}], payment_methods=[{'payment_id': 'credit_card_123', 'amount': 200}], total_baggages=1, nonfree_baggages=0, insurance='none')"},
            {'expect_success': False, 'tool_call': "env['airline'].get_reservation_details(reservation_id='RES-0000')"},
            {'expect_success': False, 'tool_call': "env['airline'].cancel_reservation(reservation_id='RES-0000')"}
        ]
    },
    {
        'name': 'Verify user state change after sending certificate (State-change verification, Normal path)',
        'steps': [
            {'expect_success': True, 'tool_call': "env['airline'].get_user_details(user_id='sara_doe_496')"},
            {'expect_success': True, 'tool_call': "env['airline'].send_certificate(user_id='sara_doe_496', amount=150)"},
            {'expect_success': True, 'tool_call': "env['airline'].get_user_details(user_id='sara_doe_496')"}
        ]
    },
    {
        'name': 'List all airports and get flight status (Normal path)',
        'steps': [
            {'expect_success': True, 'tool_call': "env['airline'].list_all_airports()"},
            {'expect_success': True, 'tool_call': "env['airline'].get_flight_status(flight_number='FL123', date='2024-05-15')"}
        ]
    },
    {
        'name': 'Search one-stop flight and calculate price (Normal path)',
        'steps': [
            {'expect_success': True, 'tool_call': "env['airline'].search_onestop_flight(origin='JFK', destination='SFO', date='2024-05-15')"},
            {'expect_success': True, 'tool_call': "env['airline'].calculate(expression='200 + 50')"}
        ]
    },
    {
        'name': 'Transfer to human agent with long summary (Boundary values, Normal path)',
        'steps': [
            {'expect_success': True, 'tool_call': "env['airline'].transfer_to_human_agents(summary='Help needed with booking.' * 100)"}
        ]
    },
    {
        'name': 'Error path - Invalid reservation ID for updates (Error paths)',
        'steps': [
            {'expect_success': False, 'tool_call': "env['airline'].update_reservation_baggages(reservation_id='INVALID_ID', total_baggages=2, nonfree_baggages=1, payment_id='credit_card_123')"},
            {'expect_success': False, 'tool_call': "env['airline'].update_reservation_flights(reservation_id='INVALID_ID', cabin='business', flights=[], payment_id='credit_card_123')"},
            {'expect_success': False, 'tool_call': "env['airline'].update_reservation_passengers(reservation_id='INVALID_ID', passengers=[{'first_name': 'John', 'last_name': 'Doe'}])"}
        ]
    },
    {
        'name': 'Error path - Invalid user and payment in booking (Error paths)',
        'steps': [
            {'expect_success': False, 'tool_call': "env['airline'].book_reservation(user_id='non_existent_user', origin='JFK', destination='LAX', flight_type='direct', cabin='economy', flights=[{'flight_number': 'FL123', 'date': '2024-05-15'}], passengers=[{'first_name': 'Sara', 'last_name': 'Doe'}], payment_methods=[{'payment_id': 'invalid_card', 'amount': 200}], total_baggages=1, nonfree_baggages=0, insurance='none')"}
        ]
    },
    {
        'name': 'Boundary values - Empty strings and zeros in search (Boundary values)',
        'steps': [
            {'expect_success': False, 'tool_call': "env['airline'].search_direct_flight(origin='', destination='', date='')"},
            {'expect_success': False, 'tool_call': "env['airline'].search_onestop_flight(origin='', destination='', date='')"},
            {'expect_success': False, 'tool_call': "env['airline'].get_flight_status(flight_number='', date='')"}
        ]
    },
    {
        'name': 'Boundary values - Empty expression in calculate (Boundary values)',
        'steps': [
            {'expect_success': False, 'tool_call': "env['airline'].calculate(expression='')"}
        ]
    },
    {
        'name': 'Boundary values - Negative amount in send certificate (Boundary values)',
        'steps': [
            {'expect_success': False, 'tool_call': "env['airline'].send_certificate(user_id='sara_doe_496', amount=-500)"}
        ]
    },
    {
        'name': 'New functional tools workflow (add_payment_method, check_in_flight, quote_reservation_change)',
        'steps': [
            {'expect_success': True, 'tool_call': "env['airline'].add_payment_method(user_id='sara_doe_496', source='credit_card', amount=1000)"},
            {'expect_success': False, 'tool_call': "env['airline'].add_payment_method(user_id='invalid_user', source='credit_card', amount=1000)"},
            {'expect_success': True, 'tool_call': "env['airline'].book_reservation(user_id='sara_doe_496', origin='JFK', destination='LAX', flight_type='direct', cabin='economy', flights=[{'flight_number': 'FL123', 'date': '2024-05-15'}], passengers=[{'first_name': 'Sara', 'last_name': 'Doe'}], payment_methods=[{'payment_id': 'credit_card_123', 'amount': 200}], total_baggages=1, nonfree_baggages=0, insurance='none')"},
            {'expect_success': True, 'tool_call': "env['airline'].quote_reservation_change(reservation_id='HATHAT', cabin='business', flights=[{'flight_number': 'FL123', 'date': '2024-05-15'}])"},
            {'expect_success': True, 'tool_call': "env['airline'].check_in_flight(reservation_id='HATHAT')"},
            {'expect_success': False, 'tool_call': "env['airline'].check_in_flight(reservation_id='HATHAT')"}
        ]
    }
]