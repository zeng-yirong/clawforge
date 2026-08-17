from copy import deepcopy
from typing import Dict, List, Optional, Tuple, Union, Any
from datetime import datetime

DEFAULT_STATE = {
    "current_user": None,
    "user_roles": {},  # 用户角色映射，key: username, value: role
    "reimbursement_requests": [],  # 所有报销申请
    "receipts": [],  # 所有票据信息
    "bank_transactions": [],  # 银行卡交易流水
    "request_counter": 1,  # 报销申请ID计数器
    "receipt_counter": 1,  # 票据ID计数器
    "system_config": {  # 系统配置
        "auto_match_threshold": 0.99,  # 自动匹配阈值
        "vat_rate": 0.13,  # 增值税率
        "max_amount_per_request": 10000.0,  # 单次报销最大金额
        "allowed_categories": ["交通费", "餐饮费", "住宿费", "办公用品", "差旅费", "其他"]
    }
}


class ReimbursementAPI:
    """
    自动化报销对账系统API类，用于OCR识别票据信息、比对银行卡流水、
    在财务系统中填充报销单并核对差额。

    该系统支持：
    1. 用户认证和角色管理
    2. 票据OCR识别和管理
    3. 银行流水导入和匹配
    4. 自动化报销申请创建和审批
    5. 金额核对和差额处理
    """

    def __init__(self):
        """
        初始化报销对账系统实例。
        """
        self.current_user: Optional[str]
        self.user_roles: Dict[str, str]
        self.reimbursement_requests: List[Dict[str, Any]]
        self.receipts: List[Dict[str, Any]]
        self.bank_transactions: List[Dict[str, Any]]
        self.request_counter: int
        self.receipt_counter: int
        self.system_config: Dict[str, Any]
        self._api_description = "该工具属于自动化报销对账系统，支持票据OCR识别、银行流水比对、自动填充报销单及金额核对功能。"

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        """
        从场景字典加载初始状态到环境中。

        Args:
            scenario (dict): 包含环境初始状态的字典
            long_context (bool): 是否加载长上下文，默认False
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.current_user = scenario.get("current_user", DEFAULT_STATE_COPY["current_user"])
        self.user_roles = scenario.get("user_roles", DEFAULT_STATE_COPY["user_roles"])
        self.reimbursement_requests = scenario.get(
            "reimbursement_requests", DEFAULT_STATE_COPY["reimbursement_requests"]
        )
        self.receipts = scenario.get("receipts", DEFAULT_STATE_COPY["receipts"])
        self.bank_transactions = scenario.get(
            "bank_transactions", DEFAULT_STATE_COPY["bank_transactions"]
        )
        self.request_counter = scenario.get(
            "request_counter", DEFAULT_STATE_COPY["request_counter"]
        )
        self.receipt_counter = scenario.get(
            "receipt_counter", DEFAULT_STATE_COPY["receipt_counter"]
        )
        self.system_config = scenario.get(
            "system_config", DEFAULT_STATE_COPY["system_config"]
        )

    def get_env_state(self) -> dict:
        """
        返回环境的完整内部状态。

        Returns:
            dict: 包含以下键值对的环境状态字典：
                - current_user (str): 当前登录用户
                - user_roles (dict): 用户角色映射
                - reimbursement_requests (list): 所有报销申请
                - receipts (list): 所有票据信息
                - bank_transactions (list): 银行卡交易流水
                - request_counter (int): 报销申请ID计数器
                - receipt_counter (int): 票据ID计数器
                - system_config (dict): 系统配置参数
        """
        return {
            "current_user": self.current_user,
            "user_roles": self.user_roles,
            "reimbursement_requests": self.reimbursement_requests,
            "receipts": self.receipts,
            "bank_transactions": self.bank_transactions,
            "request_counter": self.request_counter,
            "receipt_counter": self.receipt_counter,
            "system_config": self.system_config,
        }

    def login(self, username: str, password: str) -> Dict[str, bool]:
        """
        用户登录系统。

        Args:
            username (str): 用户名
            password (str): 密码

        Returns:
            dict: 包含登录结果的字典，成功返回 {"success": True}，失败返回 {"success": False}
        """
        # 简化认证：需要用户名和密码，且用户必须在user_roles中注册
        if username and password and username in self.user_roles:
            self.current_user = username
            return {"success": True}
        return {"success": False}

    def logout(self) -> Dict[str, bool]:
        """
        用户登出系统。

        Returns:
            dict: 包含登出结果的字典
        """
        if self.current_user:
            self.current_user = None
            return {"success": True}
        return {"success": False}

    def get_login_status(self) -> Dict[str, Optional[str]]:
        """
        获取当前登录状态。

        Returns:
            dict: 包含当前用户信息的字典，未登录时username为None
        """
        return {"username": self.current_user}

    def add_user(self, username: str, role: str) -> Dict[str, Union[bool, str]]:
        """
        添加用户到系统（仅管理员可用）。

        Args:
            username (str): 用户名
            role (str): 用户角色，可选值为 "employee", "manager", "admin"

        Returns:
            dict: 操作结果
        """
        if not self.current_user or self.user_roles.get(self.current_user) != "admin":
            return {"error": "需要管理员权限才能添加用户"}

        if role not in ["employee", "manager", "admin"]:
            return {"error": "无效的角色，可选值为: employee, manager, admin"}

        if username in self.user_roles:
            return {"error": f"用户 '{username}' 已存在"}

        self.user_roles[username] = role
        return {"success": True, "message": f"用户 '{username}' 已成功添加为 {role}"}

    def ocr_process_receipt(
        self,
        image_data: str,
        receipt_date: str,
        amount: float,
        category: str,
        merchant: str = "",
        tax_amount: float = 0.0,
        description: str = ""
    ) -> Dict[str, Union[int, str, float]]:
        """
        OCR处理票据并添加到系统。

        Args:
            image_data (str): 票据图像数据（base64编码或其他标识）
            receipt_date (str): 票据日期，格式 "YYYY-MM-DD"
            amount (float): 票据金额
            category (str): 费用类别
            merchant (str): 商户名称，默认为空
            tax_amount (float): 税额，默认为0.0
            description (str): 票据描述，默认为空

        Returns:
            dict: 处理后的票据信息或错误信息
        """
        if not self.current_user:
            return {"error": "用户未登录，请先登录"}

        if category not in self.system_config["allowed_categories"]:
            return {"error": f"无效的费用类别，可选值为: {', '.join(self.system_config['allowed_categories'])}"}

        if amount <= 0:
            return {"error": "票据金额必须大于0"}

        try:
            datetime.strptime(receipt_date, "%Y-%m-%d")
        except ValueError:
            return {"error": "日期格式无效，请使用 YYYY-MM-DD 格式"}

        receipt_id = self.receipt_counter
        receipt = {
            "id": receipt_id,
            "user": self.current_user,
            "image_data": image_data,
            "receipt_date": receipt_date,
            "amount": amount,
            "category": category,
            "merchant": merchant,
            "tax_amount": tax_amount,
            "description": description,
            "ocr_status": "success",
            "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "matched": False,
            "matched_transaction_id": None
        }

        self.receipts.append(receipt)
        self.receipt_counter += 1

        return receipt

    def import_bank_transaction(
        self,
        transaction_date: str,
        amount: float,
        description: str,
        counterparty: str = ""
    ) -> Dict[str, Union[int, str, float]]:
        """
        导入银行交易流水。

        Args:
            transaction_date (str): 交易日期，格式 "YYYY-MM-DD"
            amount (float): 交易金额（正数为收入，负数为支出）
            description (str): 交易描述
            counterparty (str): 交易对手方，默认为空

        Returns:
            dict: 导入的交易信息或错误信息
        """
        if not self.current_user:
            return {"error": "用户未登录，请先登录"}

        try:
            datetime.strptime(transaction_date, "%Y-%m-%d")
        except ValueError:
            return {"error": "日期格式无效，请使用 YYYY-MM-DD 格式"}

        transaction = {
            "id": len(self.bank_transactions) + 1,
            "user": self.current_user,
            "transaction_date": transaction_date,
            "amount": amount,
            "description": description,
            "counterparty": counterparty,
            "imported_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "matched": False,
            "matched_receipt_id": None
        }

        self.bank_transactions.append(transaction)
        return transaction

    def auto_match_receipts(self) -> Dict[str, Union[int, List[Dict]]]:
        """
        自动匹配票据和银行交易流水。

        Returns:
            dict: 匹配结果统计和详情
        """
        if not self.current_user:
            return {"error": "用户未登录，请先登录"}

        user_receipts = [r for r in self.receipts if r["user"] == self.current_user and not r["matched"]]
        user_transactions = [t for t in self.bank_transactions if t["user"] == self.current_user and not t["matched"]]

        matched_pairs = []
        for receipt in user_receipts:
            for transaction in user_transactions:
                # 简化匹配逻辑：金额相近且日期接近
                amount_diff = abs(abs(transaction["amount"]) - receipt["amount"])
                if amount_diff < 0.01:  # 金额差异小于0.01元
                    receipt["matched"] = True
                    receipt["matched_transaction_id"] = transaction["id"]
                    transaction["matched"] = True
                    transaction["matched_receipt_id"] = receipt["id"]
                    matched_pairs.append({
                        "receipt_id": receipt["id"],
                        "transaction_id": transaction["id"],
                        "amount": receipt["amount"],
                        "receipt_date": receipt["receipt_date"],
                        "transaction_date": transaction["transaction_date"]
                    })
                    break

        return {
            "matched_count": len(matched_pairs),
            "matched_pairs": matched_pairs,
            "total_receipts": len(user_receipts),
            "total_transactions": len(user_transactions)
        }

    def create_reimbursement_request(
        self,
        receipt_ids: List[int],
        description: str = "",
        is_urgent: bool = False
    ) -> Dict[str, Union[int, str, float, List]]:
        """
        创建报销申请。

        Args:
            receipt_ids (List[int]): 票据ID列表
            description (str): 报销申请描述，默认为空
            is_urgent (bool): 是否为紧急报销，默认为False

        Returns:
            dict: 创建的报销申请信息或错误信息
        """
        if not self.current_user:
            return {"error": "用户未登录，请先登录"}

        if not receipt_ids:
            return {"error": "至少需要一张票据才能创建报销申请"}

        # 验证所有票据是否属于当前用户且已匹配
        total_amount = 0.0
        included_receipts = []
        unmatched_receipts = []

        for receipt_id in receipt_ids:
            receipt = self._find_receipt(receipt_id)
            if not receipt:
                return {"error": f"票据ID {receipt_id} 不存在"}

            if receipt["user"] != self.current_user:
                return {"error": f"票据ID {receipt_id} 不属于当前用户"}

            if not receipt.get("matched", False):
                unmatched_receipts.append(receipt_id)
                continue

            total_amount += receipt["amount"]
            included_receipts.append(receipt)

        if unmatched_receipts:
            return {"error": f"以下票据未匹配银行流水: {unmatched_receipts}"}

        if total_amount > self.system_config["max_amount_per_request"]:
            return {"error": f"累计金额超过单次报销最大限额 {self.system_config['max_amount_per_request']}"}

        request_id = self.request_counter
        reimbursement_request = {
            "id": request_id,
            "user": self.current_user,
            "description": description,
            "total_amount": total_amount,
            "urgent": is_urgent,
            "status": "pending",  # pending, approved, rejected, paid
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "receipts": included_receipts,
            "approver": None,
            "approval_notes": "",
            "payment_date": None,
            "discrepancy_amount": 0.0,
            "discrepancy_notes": ""
        }

        self.reimbursement_requests.append(reimbursement_request)
        self.request_counter += 1

        return reimbursement_request

    def get_reimbursement_request(self, request_id: int) -> Dict[str, Any]:
        """
        获取报销申请详情。

        Args:
            request_id (int): 报销申请ID

        Returns:
            dict: 报销申请详情或错误信息
        """
        request = self._find_reimbursement_request(request_id)
        if not request:
            return {"error": f"报销申请ID {request_id} 不存在"}

        # 权限检查：用户只能查看自己的申请，管理员/经理可查看所有
        if self.current_user != request["user"] and self.user_roles.get(self.current_user) not in ["manager", "admin"]:
            return {"error": "无权查看此报销申请"}

        return request

    def update_reimbursement_request(
        self,
        request_id: int,
        updates: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        更新报销申请信息。

        Args:
            request_id (int): 报销申请ID
            updates (dict): 更新字段字典，支持更新 description, urgent

        Returns:
            dict: 更新结果
        """
        request = self._find_reimbursement_request(request_id)
        if not request:
            return {"error": f"报销申请ID {request_id} 不存在"}

        if self.current_user != request["user"]:
            return {"error": "只能修改自己的报销申请"}

        if request["status"] != "pending":
            return {"error": "只能修改状态为pending的报销申请"}

        valid_fields = {"description", "urgent"}
        invalid_fields = set(updates.keys()) - valid_fields
        if invalid_fields:
            return {"error": f"无效的更新字段: {', '.join(invalid_fields)}"}

        for key, value in updates.items():
            if value is not None:
                request[key] = value

        request["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {"status": f"报销申请 {request_id} 已成功更新"}

    def approve_reimbursement_request(
        self,
        request_id: int,
        notes: str = "",
        discrepancy_amount: float = 0.0,
        discrepancy_notes: str = ""
    ) -> Dict[str, str]:
        """
        审批报销申请（仅经理/管理员可用）。

        Args:
            request_id (int): 报销申请ID
            notes (str): 审批意见，默认为空
            discrepancy_amount (float): 差额金额，默认为0.0
            discrepancy_notes (str): 差额说明，默认为空

        Returns:
            dict: 审批结果
        """
        user_role = self.user_roles.get(self.current_user)
        if user_role not in ["manager", "admin"]:
            return {"error": "需要经理或管理员权限才能审批报销申请"}

        request = self._find_reimbursement_request(request_id)
        if not request:
            return {"error": f"报销申请ID {request_id} 不存在"}

        if request["status"] != "pending":
            return {"error": f"报销申请状态为 {request['status']}，无法审批"}

        request["status"] = "approved"
        request["approver"] = self.current_user
        request["approval_notes"] = notes
        request["discrepancy_amount"] = discrepancy_amount
        request["discrepancy_notes"] = discrepancy_notes
        request["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {"status": f"报销申请 {request_id} 已批准"}

    def reject_reimbursement_request(
        self,
        request_id: int,
        reason: str
    ) -> Dict[str, str]:
        """
        拒绝报销申请（仅经理/管理员可用）。

        Args:
            request_id (int): 报销申请ID
            reason (str): 拒绝原因

        Returns:
            dict: 拒绝结果
        """
        user_role = self.user_roles.get(self.current_user)
        if user_role not in ["manager", "admin"]:
            return {"error": "需要经理或管理员权限才能拒绝报销申请"}

        request = self._find_reimbursement_request(request_id)
        if not request:
            return {"error": f"报销申请ID {request_id} 不存在"}

        if request["status"] != "pending":
            return {"error": f"报销申请状态为 {request['status']}，无法拒绝"}

        request["status"] = "rejected"
        request["approver"] = self.current_user
        request["approval_notes"] = reason
        request["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {"status": f"报销申请 {request_id} 已拒绝"}

    def process_payment(
        self,
        request_id: int,
        payment_date: str,
        payment_method: str = "bank_transfer"
    ) -> Dict[str, str]:
        """
        处理报销申请付款（仅财务/管理员可用）。

        Args:
            request_id (int): 报销申请ID
            payment_date (str): 付款日期，格式 "YYYY-MM-DD"
            payment_method (str): 付款方式，默认为 "bank_transfer"

        Returns:
            dict: 付款处理结果
        """
        user_role = self.user_roles.get(self.current_user)
        if user_role not in ["admin"]:  # 仅管理员可处理付款
            return {"error": "需要管理员权限才能处理付款"}

        request = self._find_reimbursement_request(request_id)
        if not request:
            return {"error": f"报销申请ID {request_id} 不存在"}

        if request["status"] != "approved":
            return {"error": f"只有已批准的报销申请才能付款，当前状态: {request['status']}"}

        try:
            datetime.strptime(payment_date, "%Y-%m-%d")
        except ValueError:
            return {"error": "付款日期格式无效，请使用 YYYY-MM-DD 格式"}

        if payment_method not in ["bank_transfer", "cash", "check"]:
            return {"error": "无效的付款方式，可选值为: bank_transfer, cash, check"}

        request["status"] = "paid"
        request["payment_date"] = payment_date
        request["payment_method"] = payment_method
        request["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {"status": f"报销申请 {request_id} 已标记为已付款"}

    def get_user_receipts(
        self,
        matched: Optional[bool] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取当前用户的票据列表。

        Args:
            matched (bool): 筛选是否已匹配，默认为None（不过滤）
            category (str): 筛选费用类别，默认为None（不过滤）

        Returns:
            list: 票据列表
        """
        if not self.current_user:
            return [{"error": "用户未登录，请先登录"}]

        user_receipts = [r for r in self.receipts if r["user"] == self.current_user]

        if matched is not None:
            user_receipts = [r for r in user_receipts if r["matched"] == matched]

        if category:
            user_receipts = [r for r in user_receipts if r["category"] == category]

        return user_receipts

    def get_user_requests(
        self,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        获取当前用户的报销申请列表。

        Args:
            status (str): 筛选状态，默认为None（不过滤）

        Returns:
            list: 报销申请列表
        """
        if not self.current_user:
            return [{"error": "用户未登录，请先登录"}]

        user_requests = [r for r in self.reimbursement_requests if r["user"] == self.current_user]

        if status:
            user_requests = [r for r in user_requests if r["status"] == status]

        return user_requests

    def calculate_statistics(self) -> Dict[str, Any]:
        """
        计算当前用户的报销统计信息。

        Returns:
            dict: 统计信息
        """
        if not self.current_user:
            return {"error": "用户未登录，请先登录"}

        user_receipts = [r for r in self.receipts if r["user"] == self.current_user]
        user_requests = [r for r in self.reimbursement_requests if r["user"] == self.current_user]

        total_receipts = len(user_receipts)
        matched_receipts = sum(1 for r in user_receipts if r["matched"])
        total_amount = sum(r["amount"] for r in user_receipts)
        matched_amount = sum(r["amount"] for r in user_receipts if r["matched"])

        pending_amount = sum(r["total_amount"] for r in user_requests if r["status"] == "pending")
        approved_amount = sum(r["total_amount"] for r in user_requests if r["status"] == "approved")
        paid_amount = sum(r["total_amount"] for r in user_requests if r["status"] == "paid")

        return {
            "user": self.current_user,
            "total_receipts": total_receipts,
            "matched_receipts": matched_receipts,
            "matching_rate": matched_receipts / total_receipts if total_receipts > 0 else 0,
            "total_amount": total_amount,
            "matched_amount": matched_amount,
            "pending_amount": pending_amount,
            "approved_amount": approved_amount,
            "paid_amount": paid_amount,
            "total_requests": len(user_requests)
        }

    def update_system_config(
        self,
        key: str,
        value: Union[str, float, int, List[str]]
    ) -> Dict[str, str]:
        """
        更新系统配置（仅管理员可用）。

        Args:
            key (str): 配置键
            value (Union[str, float, int, List[str]]): 配置值

        Returns:
            dict: 更新结果
        """
        if not self.current_user or self.user_roles.get(self.current_user) != "admin":
            return {"error": "需要管理员权限才能更新系统配置"}

        if key not in self.system_config:
            return {"error": f"无效的配置键: {key}"}

        # 验证值类型
        current_value = self.system_config[key]
        if not isinstance(value, type(current_value)):
            return {"error": f"配置值类型错误，期望类型: {type(current_value).__name__}"}

        # 验证特定配置的合法范围
        error_message = None
        if key == "auto_match_threshold":
            if not 0 <= value <= 1:
                error_message = "auto_match_threshold 必须在0到1之间"
        elif key == "vat_rate":
            if not 0 <= value <= 1:
                error_message = "vat_rate 必须在0到1之间"
        elif key == "max_amount_per_request":
            if value <= 0:
                error_message = "max_amount_per_request 必须大于0"
        elif key == "allowed_categories":
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                error_message = "allowed_categories 必须是字符串列表"

        if error_message:
            return {"error": error_message}

        self.system_config[key] = value
        return {"status": f"系统配置 {key} 已更新为 {value}"}

    def _find_receipt(self, receipt_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID查找票据。

        Args:
            receipt_id (int): 票据ID

        Returns:
            dict: 票据信息，如果未找到返回None
        """
        for receipt in self.receipts:
            if receipt["id"] == receipt_id:
                return receipt
        return None

    def _find_reimbursement_request(self, request_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID查找报销申请。

        Args:
            request_id (int): 报销申请ID

        Returns:
            dict: 报销申请信息，如果未找到返回None
        """
        for request in self.reimbursement_requests:
            if request["id"] == request_id:
                return request
        return None

    def _find_bank_transaction(self, transaction_id: int) -> Optional[Dict[str, Any]]:
        """
        根据ID查找银行交易流水。

        Args:
            transaction_id (int): 交易ID

        Returns:
            dict: 交易信息，如果未找到返回None
        """
        for transaction in self.bank_transactions:
            if transaction["id"] == transaction_id:
                return transaction
        return None

    def _log(self, event: str, detail: Dict) -> None:
        """Log environment events."""
        if not hasattr(self, '_event_log'):
            self._event_log: List[Dict[str, Any]] = []
        self._event_log.append({
            "event": event,
            "detail": detail,
            "timestamp": datetime.now().isoformat()
        })