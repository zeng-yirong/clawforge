import copy
from typing import Dict, List, Union, Any, Optional
from datetime import datetime

# 默认状态常量
DEFAULT_STATE: Dict[str, Any] = {
    "users": {
        "Eve": {"user_id": "U100", "password": "password123", "balance": 500.0, "vouchers": []},
        "Frank": {"user_id": "U101", "password": "password456", "balance": 300.0, "vouchers": []},
        "Grace": {"user_id": "U102", "password": "password789", "balance": 150.0, "vouchers": []},
        "Helen": {"user_id": "U103", "password": "password321", "balance": 800.0, "vouchers": []},
        "Isaac": {"user_id": "U104", "password": "password654", "balance": 400.0, "vouchers": []},
        "Jack": {"user_id": "U105", "password": "password654", "balance": 120.0, "vouchers": []},
    },
    "merchant_list": {
        "Domino's": {
            "merchant_id": "M100",
            "service_type": "Pizza",
            "menu": [
                {"product": "Margherita Pizza", "price": 68.0},
                {"product": "Super Supreme Pizza", "price": 88.0},
            ],
            "vouchers": [{"type": "100_yuan_voucher", "price": 85.0, "face_value": 100.0}]
        },
        "Rice Village Bibimbap": {
            "merchant_id": "M101",
            "service_type": "Bibimbap",
            "menu": [
                {"product": "Stone Pot Bibimbap", "price": 35.0},
                {"product": "Korean Beef Bibimbap", "price": 45.0},
            ],
            "vouchers": [{"type": "50_yuan_voucher", "price": 40.0, "face_value": 50.0}]
        },
        "Haidilao": {
            "merchant_id": "M102",
            "service_type": "Hotpot",
            "menu": [
                {"product": "Beef Rolls", "price": 68.0},
                {"product": "Seafood Platter", "price": 88.0},
            ],
            "vouchers": [{"type": "200_yuan_voucher", "price": 180.0, "face_value": 200.0}]
        },
        "Heytea": {
            "merchant_id": "M103",
            "service_type": "Milk Tea",
            "menu": [
                {"product": "Cheese Milk Tea", "price": 25.0},
                {"product": "Four Seasons Spring Milk Tea", "price": 22.0},
            ],
            "vouchers": [{"type": "20_yuan_voucher", "price": 18.0, "face_value": 20.0}]
        },
        "Hema Fresh": {
            "merchant_id": "M104",
            "service_type": "Fresh Grocery",
            "menu": [
                {"product": "Organic Vegetable Pack", "price": 15.0},
                {"product": "Fresh Gift Pack", "price": 99.0},
            ],
            "vouchers": [{"type": "100_yuan_voucher", "price": 90.0, "face_value": 100.0}]
        },
        "Jiutian BBQ": {
            "merchant_id": "M105",
            "service_type": "BBQ",
            "menu": [
                {"product": "Korean Grilled Beef", "price": 128.0},
                {"product": "Grilled Pork Belly", "price": 78.0},
            ],
            "vouchers": [{"type": "150_yuan_voucher", "price": 130.0, "face_value": 150.0}]
        },
    },
    "orders": [],
    "reviews": {},
    "wifi": True,
    "logged_in_users": []
}


class FoodPlatform:
    """
    A class representing a Meituan-like platform where users need to log in, and each user has an associated balance.
    Merchants provide a menu of products, and users can place food delivery or group purchase orders.
    """

    def __init__(self):
        # 重置到初始状态
        self.reset()

    # ---------- 辅助方法 ----------
    def _success_response(self, data: Any = None) -> Dict[str, Any]:
        return {"success": True, "data": data}

    def _error_response(self, msg: str) -> Dict[str, Any]:
        return {"success": False, "error": msg}

    def _timestamp(self) -> str:
        return datetime.now().isoformat()

    # ---------- 状态管理 ----------
    def reset(self):
        """重置环境到默认状态（深拷贝）"""
        self.users = copy.deepcopy(DEFAULT_STATE["users"])
        self.merchant_list = copy.deepcopy(DEFAULT_STATE["merchant_list"])
        self.orders = copy.deepcopy(DEFAULT_STATE["orders"])
        self.reviews = copy.deepcopy(DEFAULT_STATE["reviews"])
        self.wifi = copy.deepcopy(DEFAULT_STATE["wifi"])
        self.logged_in_users = copy.deepcopy(DEFAULT_STATE["logged_in_users"])
        self._order_counter = 0
        self._voucher_id_counter = 0

    def _load_scenario(self, scenario: dict, long_context: bool = False, **kwargs) -> None:
        """加载场景配置，覆盖默认状态"""
        self.reset()  # 先重置为默认
        
        # 根据场景覆盖字段（使用深拷贝），使用 .get() 防御缺失键，缺省时保留 reset 后的默认值
        self.users = copy.deepcopy(scenario.get("users", self.users))
        self.merchant_list = copy.deepcopy(scenario.get("merchant_list", self.merchant_list))
        self.orders = copy.deepcopy(scenario.get("orders", self.orders))
        self.reviews = copy.deepcopy(scenario.get("reviews", self.reviews))
        self.wifi = copy.deepcopy(scenario.get("wifi", self.wifi))
        self.logged_in_users = copy.deepcopy(scenario.get("logged_in_users", self.logged_in_users))

        # 根据已有订单恢复计数器，使用安全的 .get() 并给一个默认整数 0
        self._order_counter = max(
            (order.get("order_id", 0) for order in self.orders if isinstance(order.get("order_id"), int)), 
            default=0
        )

    def get_env_state(self) -> Dict[str, Any]:
        """返回当前状态的深拷贝，防止外部篡改"""
        return {
            "users": copy.deepcopy(self.users),
            "merchant_list": copy.deepcopy(self.merchant_list),
            "logged_in_users": copy.deepcopy(self.logged_in_users),
            "orders": copy.deepcopy(self.orders),
            "reviews": copy.deepcopy(self.reviews),
            "wifi": copy.deepcopy(self.wifi)
        }

    # ---------- 用户登录 ----------
    def login_food_platform(self, username: str, password: str) -> Dict[str, Any]:
        if not self.wifi:
            return self._error_response("Wi-Fi is not enabled, unable to login")
        if username not in self.users:
            return self._error_response("User does not exist")
        if self.users[username]["password"] != password:
            return self._error_response("Incorrect password")
        if username in self.logged_in_users:
            return self._error_response(f"{username} is already logged in")

        self.logged_in_users.append(username)
        return self._success_response({"message": f"User {username} has successfully logged in!"})

    def view_logged_in_users(self) -> Dict[str, Any]:
        if not self.logged_in_users:
            return self._error_response("No users are currently logged in to the food platform")
        return self._success_response({"logged_in_users": self.logged_in_users})

    def logout_food_platform(self, username: str) -> Dict[str, Any]:
        if username not in self.users:
            return self._error_response(f"User {username} does not exist")
        if username not in self.logged_in_users:
            return self._error_response(f"User {username} is not currently logged in")

        self.logged_in_users.remove(username)
        return self._success_response({"message": f"User {username} has successfully logged out!"})

    # ---------- 余额 ----------
    def check_balance(self, user_name: str) -> Dict[str, Any]:
        if user_name not in self.users:
            return self._error_response(f"User {user_name} does not exist!")
        return self._success_response(self.users[user_name]["balance"])

    def recharge_balance(self, username: str, amount: float) -> Dict[str, Any]:
        if username not in self.users:
            return self._error_response(f"User {username} does not exist")
        if amount <= 0:
            return self._error_response("Recharge amount must be strictly positive")

        self.users[username]["balance"] += amount
        return self._success_response({
            "message": f"Successfully recharged {amount} yuan for user {username}. New balance: {self.users[username]['balance']} yuan"
        })

    # ---------- 商家 & 商品 ----------
    def get_all_merchants(self) -> Dict[str, Any]:
        if not self.merchant_list:
            return self._error_response("No merchants available on the platform")
        return self._success_response({"merchants": list(self.merchant_list.keys())})

    def get_products(self, merchant_name: str) -> Dict[str, Any]:
        merchant = self.merchant_list.get(merchant_name)
        if not merchant:
            return self._error_response(f"Merchant '{merchant_name}' does not exist")
        return self._success_response(merchant["menu"])

    def search_merchants_by_type(self, service_type: str) -> Dict[str, Any]:
        if not service_type:
            return self._error_response("Service type cannot be empty")
        matched = [
            name for name, det in self.merchant_list.items()
            if isinstance(det, dict) and det.get("service_type", "").lower() == service_type.lower()
        ]
        if not matched:
            return self._error_response(f"No merchants found for service type: {service_type}")
        return self._success_response({"merchants": matched})

    def search_products_globally(self, keyword: str) -> Dict[str, Any]:
        if not keyword:
            return self._error_response("Keyword cannot be empty")
        results = []
        for mname, det in self.merchant_list.items():
            if isinstance(det, dict):
                for item in det.get("menu", []):
                    if isinstance(item, dict) and keyword.lower() in str(item.get("product", "")).lower():
                        results.append({
                            "merchant_name": mname,
                            "product": item["product"],
                            "price": item["price"]
                        })
        if not results:
            return self._error_response(f"No products found matching keyword: '{keyword}'")
        return self._success_response({"products": results})

    # ---------- 订单 ----------
    def add_food_delivery_order(
        self,
        username: str,
        merchant_name: str,
        items: List[Dict[str, Union[str, int]]],
        voucher_id: Optional[int] = None
    ) -> Dict[str, Any]:
        if username not in self.logged_in_users:
            return self._error_response(f"User {username} is not logged in to the food platform")
        if merchant_name not in self.merchant_list:
            return self._error_response("Merchant does not exist")
        if not items:
            return self._error_response("Order must contain at least one item")

        total_price = 0.0
        order_items = []
        merchant = self.merchant_list[merchant_name]

        for item in items:
            if "product" not in item:
                return self._error_response("Missing product name in item")
            pname = item["product"]
            qty = item.get("quantity", 1)
            if not isinstance(qty, int) or qty <= 0:
                return self._error_response(f"Invalid quantity {qty} for product {pname}")
            found = False
            for prod in merchant["menu"]:
                if prod["product"] == pname:
                    total_price += prod["price"] * qty
                    order_items.append({
                        "product": pname,
                        "quantity": qty,
                        "price_per_unit": prod["price"]
                    })
                    found = True
                    break
            if not found:
                return self._error_response(f"Product {pname} does not exist in {merchant_name}'s menu")

        # 检查是否使用团购券抵扣
        deduction = 0.0
        used_voucher = None
        if voucher_id is not None:
            user_vouchers = self.users[username].get("vouchers", [])
            found_voucher = None
            for v in user_vouchers:
                if v.get("voucher_id") == voucher_id:
                    found_voucher = v
                    break
            if not found_voucher:
                return self._error_response(f"Voucher with id {voucher_id} not found for user {username}")
            if found_voucher.get("merchant_name") != merchant_name:
                return self._error_response("Voucher cannot be used for this merchant")
            if found_voucher.get("used", False):
                return self._error_response("Voucher has already been used")
            # 计算抵扣（不能超过订单总价）
            face_value = found_voucher.get("face_value", 0.0)
            deduction = min(face_value, total_price)
            used_voucher = found_voucher

        final_price = total_price - deduction
        if final_price < 0:
            final_price = 0.0  # 不应出现，但安全处理

        # 检查余额
        if final_price > self.users[username]["balance"]:
            return self._error_response("Insufficient balance to place the order")

        # 扣款、标记券已使用、创建订单
        self.users[username]["balance"] -= final_price
        if used_voucher is not None:
            used_voucher["used"] = True

        self._order_counter += 1
        order = {
            "order_id": self._order_counter,
            "user_name": username,
            "merchant_name": merchant_name,
            "items": order_items,
            "total_price": total_price,
            "deduction": deduction,
            "final_price": final_price,
            "used_voucher_id": voucher_id,
            "status": "completed",
            "timestamp": self._timestamp()
        }
        self.orders.append(order)
        return self._success_response({
            "message": f"Food delivery order successfully placed with {merchant_name}. Total amount: {total_price} yuan, deducted: {deduction} yuan, final paid: {final_price} yuan"
        })

    def view_orders(self, user_name: str) -> Dict[str, Any]:
        user_orders = [o for o in self.orders if o.get("user_name") == user_name]
        if not user_orders:
            return self._error_response("User has no order records")
        return self._success_response({"orders": user_orders})

    def search_orders(self, keyword: str) -> Dict[str, Any]:
        if not keyword:
            return self._error_response("Keyword cannot be empty")
        matched = [
            o for o in self.orders
            if keyword.lower() in o.get("merchant_name", "").lower()
               or any(keyword.lower() in it.get("product", "").lower() for it in o.get("items", []))
        ]
        if not matched:
            return self._error_response("No matching orders found")
        return self._success_response({"orders": matched})

    def cancel_latest_order(self, username: str) -> Dict[str, Any]:
        if username not in self.users:
            return self._error_response(f"User {username} does not exist")
        if username not in self.logged_in_users:
            return self._error_response(f"User {username} is not logged in to the food platform")

        # 找用户最新且未取消的订单
        user_orders = [o for o in self.orders if o.get("user_name") == username and o.get("status") != "cancelled"]
        if not user_orders:
            return self._error_response(f"User {username} has no orders to cancel")

        latest = user_orders[-1]
        # 退款（只退实际支付的 final_price）
        refund = latest.get("final_price", 0.0)
        self.users[username]["balance"] += refund

        # 如果使用了券，恢复券的 used 状态
        used_voucher_id = latest.get("used_voucher_id")
        if used_voucher_id is not None:
            for v in self.users[username].get("vouchers", []):
                if v.get("voucher_id") == used_voucher_id:
                    v["used"] = False
                    break

        # 标记订单为 cancelled（不物理删除）
        latest["status"] = "cancelled"
        latest["cancel_timestamp"] = self._timestamp()

        return self._success_response({
            "message": f"Successfully cancelled the latest order (order_id={latest['order_id']}) with {latest.get('merchant_name')}. Refunded {refund} yuan"
        })

    # ---------- 团购券 ----------
    def buy_group_voucher(self, username: str, merchant_name: str, voucher_type: str) -> Dict[str, Any]:
        if username not in self.logged_in_users:
            return self._error_response(f"User {username} is not logged in to the food platform")
        if merchant_name not in self.merchant_list:
            return self._error_response(f"Merchant '{merchant_name}' does not exist")

        merchant = self.merchant_list[merchant_name]
        vlist = merchant.get("vouchers", [])
        selected = next((v for v in vlist if v.get("type") == voucher_type), None)
        if not selected:
            return self._error_response(f"Voucher '{voucher_type}' does not exist for merchant '{merchant_name}'")

        price = selected.get("price", 0.0)
        face_value = selected.get("face_value", 0.0)
        if self.users[username]["balance"] < price:
            return self._error_response("Insufficient balance to buy the voucher")

        # 扣款
        self.users[username]["balance"] -= price

        # 生成券 ID 并添加
        self._voucher_id_counter += 1
        voucher = {
            "voucher_id": self._voucher_id_counter,
            "merchant_name": merchant_name,
            "voucher_type": voucher_type,
            "face_value": face_value,
            "buy_price": price,
            "used": False,
            "timestamp": self._timestamp()
        }
        # 确保用户有 vouchers 列表
        self.users[username].setdefault("vouchers", []).append(voucher)

        return self._success_response({
            "message": f"Successfully purchased {voucher_type} for {merchant_name}. Deducted {price} yuan. Voucher ID: {self._voucher_id_counter}"
        })

    def view_user_vouchers(self, username: str) -> Dict[str, Any]:
        if username not in self.users:
            return self._error_response(f"User {username} does not exist")
        vouchers = self.users[username].get("vouchers", [])
        if not vouchers:
            return self._error_response(f"User {username} has no vouchers")
        return self._success_response({"vouchers": vouchers})

    # ---------- 评价 ----------
    def add_merchant_review(self, username: str, merchant_name: str, rating: int, comment: str) -> Dict[str, Any]:
        if username not in self.users:
            return self._error_response(f"User {username} does not exist")
        if merchant_name not in self.merchant_list:
            return self._error_response(f"Merchant '{merchant_name}' does not exist")
        if not isinstance(rating, int) or not (1 <= rating <= 5):
            return self._error_response("Rating must be an integer between 1 and 5")

        has_order = any(
            o.get("user_name") == username and o.get("merchant_name") == merchant_name
            for o in self.orders
        )
        has_voucher = any(
            v.get("merchant_name") == merchant_name
            for v in self.users[username].get("vouchers", [])
        )
        if not has_order and not has_voucher:
            return self._error_response(f"User {username} cannot review merchant '{merchant_name}' without any past orders or vouchers")

        self.reviews.setdefault(merchant_name, []).append({
            "user_name": username,
            "rating": rating,
            "comment": comment,
            "timestamp": self._timestamp()
        })
        return self._success_response({"message": f"Successfully added review for {merchant_name} with rating {rating}"})

    def view_merchant_reviews(self, merchant_name: str) -> Dict[str, Any]:
        if merchant_name not in self.merchant_list:
            return self._error_response(f"Merchant '{merchant_name}' does not exist")
        reviews = self.reviews.get(merchant_name, [])
        if not reviews:
            return self._error_response(f"No reviews found for merchant '{merchant_name}'")
        avg = sum(r.get("rating", 0) for r in reviews) / len(reviews)
        return self._success_response({
            "merchant_name": merchant_name,
            "average_rating": round(avg, 2),
            "reviews": reviews
        })


# ========== 测试用例（保持不变） ==========
__TEST_CASES__ = [
    {
        'name': 'Normal path - Login and view logged-in users',
        'steps': [
            {'expect_success': True, 'tool_call': 'login_food_platform(username="Eve", password="password123")'},
            {'expect_success': True, 'tool_call': 'view_logged_in_users()'}
        ]
    },
    {
        'name': 'Normal path - Get products and check balance',
        'steps': [
            {'expect_success': True, 'tool_call': 'get_products(merchant_name="Haidilao")'},
            {'expect_success': True, 'tool_call': 'check_balance(user_name="Eve")'}
        ]
    },
    {
        'name': 'Cross-method workflow - Complete order process',
        'steps': [
            {'expect_success': True, 'tool_call': 'login_food_platform(username="Frank", password="password456")'},
            {'expect_success': True, 'tool_call': 'get_products(merchant_name="Haidilao")'},
            {'expect_success': True, 'tool_call': 'add_food_delivery_order(username="Frank", merchant_name="Haidilao", items=[{"product": "Beef Rolls", "quantity": 2}])'},
            {'expect_success': True, 'tool_call': 'check_balance(user_name="Frank")'},
            {'expect_success': True, 'tool_call': 'view_orders(user_name="Frank")'},
            {'expect_success': True, 'tool_call': 'search_orders(keyword="Beef Rolls")'}
        ]
    },
    {
        'name': 'Error path - Invalid login credentials',
        'steps': [
            {'expect_success': False, 'tool_call': 'login_food_platform(username="nonexistent_user", password="wrong_password")'}
        ]
    },
    {
        'name': 'Error path - Order with non-existent user or not logged in',
        'steps': [
            {'expect_success': False, 'tool_call': 'add_food_delivery_order(username="Grace", merchant_name="Heytea", items=[{"product": "Cheese Milk Tea", "quantity": 1}])'}
        ]
    },
    {
        'name': 'Boundary values - Empty strings',
        'steps': [
            {'expect_success': False, 'tool_call': 'login_food_platform(username="", password="")'},
            {'expect_success': False, 'tool_call': 'get_products(merchant_name="")'},
            {'expect_success': False, 'tool_call': 'search_orders(keyword="")'}
        ]
    },
    {
        'name': 'Boundary values - Negative and zero quantities in order',
        'steps': [
            {'expect_success': True, 'tool_call': 'login_food_platform(username="Helen", password="password321")'},
            {'expect_success': False, 'tool_call': 'add_food_delivery_order(username="Helen", merchant_name="Heytea", items=[{"product": "Cheese Milk Tea", "quantity": -1}])'},
            {'expect_success': False, 'tool_call': 'add_food_delivery_order(username="Helen", merchant_name="Heytea", items=[{"product": "Cheese Milk Tea", "quantity": 0}])'}
        ]
    },
    {
        'name': 'Error path - Invalid items format',
        'steps': [
            {'expect_success': True, 'tool_call': 'login_food_platform(username="Isaac", password="password654")'},
            {'expect_success': False, 'tool_call': 'add_food_delivery_order(username="Isaac", merchant_name="Jiutian BBQ", items=[])'},
            {'expect_success': False, 'tool_call': 'add_food_delivery_order(username="Isaac", merchant_name="Jiutian BBQ", items=[{"invalid_key": "data"}])'}
        ]
    },
    {
        'name': 'State-change verification - Balance deduction and order history',
        'steps': [
            {'expect_success': True, 'tool_call': 'check_balance(user_name="Jack")'},
            {'expect_success': True, 'tool_call': 'login_food_platform(username="Jack", password="password654")'},
            {'expect_success': True, 'tool_call': 'add_food_delivery_order(username="Jack", merchant_name="Hema Fresh", items=[{"product": "Organic Vegetable Pack", "quantity": 1}])'},
            {'expect_success': True, 'tool_call': 'check_balance(user_name="Jack")'},
            {'expect_success': True, 'tool_call': 'view_orders(user_name="Jack")'}
        ]
    },
    {
        'name': 'Boundary values - Excessively long inputs',
        'steps': [
            {'expect_success': False, 'tool_call': 'login_food_platform(username="uuuu", password="pppp")'},
            {'expect_success': False, 'tool_call': 'get_products(merchant_name="m")'}
        ]
    },
    {
        'name': 'New feature - Logout workflow',
        'steps': [
            {'expect_success': True, 'tool_call': 'login_food_platform(username="Eve", password="password123")'},
            {'expect_success': True, 'tool_call': 'logout_food_platform(username="Eve")'},
            {'expect_success': False, 'tool_call': 'logout_food_platform(username="Eve")'}
        ]
    },
    {
        'name': 'New feature - Recharge balance',
        'steps': [
            {'expect_success': True, 'tool_call': 'recharge_balance(username="Grace", amount=100.0)'},
            {'expect_success': False, 'tool_call': 'recharge_balance(username="Grace", amount=-50.0)'}
        ]
    },
    {
        'name': 'New feature - Discover merchants',
        'steps': [
            {'expect_success': True, 'tool_call': 'get_all_merchants()'},
            {'expect_success': True, 'tool_call': 'search_merchants_by_type(service_type="Pizza")'},
            {'expect_success': False, 'tool_call': 'search_merchants_by_type(service_type="Aliens")'}
        ]
    },
    {
        'name': 'New feature - Cancel latest order',
        'steps': [
            {'expect_success': True, 'tool_call': 'login_food_platform(username="Frank", password="password456")'},
            {'expect_success': True, 'tool_call': 'add_food_delivery_order(username="Frank", merchant_name="Haidilao", items=[{"product": "Beef Rolls", "quantity": 1}])'},
            {'expect_success': True, 'tool_call': 'cancel_latest_order(username="Frank")'},
            {'expect_success': False, 'tool_call': 'cancel_latest_order(username="Frank")'}
        ]
    },
    {
        'name': 'New feature - Search products globally',
        'steps': [
            {'expect_success': True, 'tool_call': 'search_products_globally(keyword="Beef")'},
            {'expect_success': False, 'tool_call': 'search_products_globally(keyword="Aliens")'}
        ]
    },
    {
        'name': 'New feature - Buy and view group vouchers',
        'steps': [
            {'expect_success': True, 'tool_call': 'login_food_platform(username="Helen", password="password321")'},
            {'expect_success': True, 'tool_call': 'buy_group_voucher(username="Helen", merchant_name="Hema Fresh", voucher_type="100_yuan_voucher")'},
            {'expect_success': True, 'tool_call': 'view_user_vouchers(username="Helen")'},
            {'expect_success': False, 'tool_call': 'buy_group_voucher(username="Helen", merchant_name="Hema Fresh", voucher_type="invalid_voucher")'}
        ]
    },
    {
        'name': 'New feature - Add and view reviews',
        'steps': [
            {'expect_success': True, 'tool_call': 'login_food_platform(username="Frank", password="password456")'},
            {'expect_success': True, 'tool_call': 'add_food_delivery_order(username="Frank", merchant_name="Haidilao", items=[{"product": "Beef Rolls", "quantity": 1}])'},
            {'expect_success': True, 'tool_call': 'add_merchant_review(username="Frank", merchant_name="Haidilao", rating=5, comment="Excellent!")'},
            {'expect_success': True, 'tool_call': 'view_merchant_reviews(merchant_name="Haidilao")'},
            {'expect_success': False, 'tool_call': 'add_merchant_review(username="Eve", merchant_name="Haidilao", rating=4, comment="No order!")'}
        ]
    }
]