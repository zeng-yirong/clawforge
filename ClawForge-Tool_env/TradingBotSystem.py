import random
from copy import deepcopy
from datetime import datetime, time, timedelta
from typing import Dict, List, Optional, Union, Any

# === Trimmed long context extension data (5-10 samples each) ===
WATCH_LIST_EXTENSION = ['JHGUN', 'LMAT', 'YNK', 'W', 'XSW', 'XZEHV', 'R', 'UIENW', 'H', 'P']

TRANSACTION_HISTORY_EXTENSION = [{'amount': 9933.53, 'timestamp': '2024-05-01 22:14:05.858817', 'type': 'deposit'},
 {'amount': 9084.83, 'timestamp': '2023-10-25 20:12:10.858830', 'type': 'deposit'},
 {'amount': 671.32, 'timestamp': '2023-10-04 06:33:21.858835', 'type': 'deposit'},
 {'amount': 9665.3, 'timestamp': '2024-04-13 15:29:14.858840', 'type': 'withdrawal'},
 {'amount': 3921.42, 'timestamp': '2024-03-16 06:18:24.858844', 'type': 'deposit'},
 {'amount': 9675.67, 'timestamp': '2024-07-26 21:53:21.858849', 'type': 'withdrawal'},
 {'amount': 853.72, 'timestamp': '2023-10-28 18:01:23.858853', 'type': 'deposit'},
 {'amount': 932.42, 'timestamp': '2024-04-19 10:06:26.858858', 'type': 'deposit'},
 {'amount': 6048.05, 'timestamp': '2024-01-03 22:01:08.858862', 'type': 'withdrawal'},
 {'amount': 6235.57, 'timestamp': '2023-10-04 22:40:59.858867', 'type': 'withdrawal'}]

MA_5_EXTENSION = [234.34, 212.46, 228.56, 209.19, 223.68, 242.5, 225.93, 219.47, 241.34, 208.85]

MA_20_EXTENSION = [225.08, 209.54, 242.23, 200.66, 205.5, 236.61, 235.66, 244.32, 207.04, 236.46]

AUTOMOBILE_EXTENSION = ['TSLA', 'F', 'GM', 'UNUGJ', 'BVO', 'OG', 'QMQQH', 'CP', 'NPIGW', 'V']

ORDER_DETAIL_EXTENSION = {'company_overview': '\n'
                     '    {symbol} is one of the most influential companies in its sector. With a global reach, '
                     '{symbol} has been instrumental\n'
                     '    in shaping its industry. From groundbreaking products to innovative services, the company '
                     'has consistently delivered\n'
                     '    high-quality offerings that resonate with both consumers and investors. Founded several '
                     'decades ago, {symbol} has grown\n'
                     '    exponentially, establishing itself as a market leader. Its extensive portfolio includes '
                     'diverse products and services,\n'
                     '    each contributing to the company’s robust financial health.\n'
                     '\n'
                     '    The company has consistently demonstrated a commitment to innovation, regularly introducing '
                     'new technologies that redefine\n'
                     '    how consumers and businesses interact with its products. In recent years, {symbol} has '
                     'placed significant emphasis on \n'
                     '    sustainability, investing in environmentally friendly initiatives and aiming for carbon '
                     'neutrality by the year 2030. This\n'
                     '    focus has garnered support from eco-conscious consumers and institutional investors alike, '
                     "further enhancing the company's\n"
                     '    reputation and stock value.\n'
                     '    ',
 'financial_highlights': '\n'
                         '    In terms of financials, {symbol} boasts impressive metrics. The company has reported '
                         'consistent revenue growth over the past\n'
                         '    five years, with a compound annual growth rate (CAGR) of over 15%. The company’s net '
                         'profit margins have remained high,\n'
                         '    exceeding 20% for the past three fiscal years. This strong financial performance has '
                         'allowed {symbol} to maintain a robust\n'
                         '    balance sheet, with significant cash reserves and minimal debt.\n'
                         '\n'
                         '    {symbol} has also been returning value to shareholders through dividends and share '
                         'buybacks. Over the past two years,\n'
                         '    the company has repurchased over $20 billion worth of its own stock, boosting earnings '
                         'per share (EPS) and increasing\n'
                         '    shareholder value. Analysts predict that {symbol} will continue its strong financial '
                         'performance, driven by new product\n'
                         '    launches and expansion into new markets.\n'
                         '    ',
 'future_outlook': '\n'
                   '    Looking ahead, {symbol} is poised for continued growth. The company has several new products '
                   'in the pipeline, including \n'
                   '    expansions into new markets such as artificial intelligence (AI), augmented reality (AR), and '
                   'the Internet of Things (IoT). \n'
                   "    These technologies are expected to drive demand for {symbol}'s products, particularly in the "
                   'business and enterprise sectors.\n'
                   '\n'
                   '    {symbol} has also announced plans to expand its services division, which includes '
                   'subscription-based offerings such as \n'
                   '    cloud services, digital media, and financial technology (FinTech) solutions. These high-margin '
                   'services are expected to \n'
                   "    contribute significantly to the company's revenue in the coming years. Investors and analysts "
                   'alike are optimistic about \n'
                   '    the company’s future prospects, particularly in light of its continued commitment to '
                   'innovation and sustainability.\n'
                   '    ',
 'historical_performance': '\n'
                           '    Over the past decade, {symbol} has been a standout performer in its sector, delivering '
                           'consistently high returns to \n'
                           '    shareholders. The stock has outperformed the broader market, with an annualized return '
                           'of over 18% in the past 10 years. \n'
                           '    The company’s ability to navigate both market downturns and economic crises, such as '
                           'the 2008 financial crisis and the \n'
                           '    2020 COVID-19 pandemic, has made it a favorite among institutional investors.\n'
                           '\n'
                           '    In 2022, {symbol} saw a record-breaking year, with revenue exceeding $500 billion for '
                           'the first time in its history. \n'
                           '    This growth was driven by strong demand for the company’s flagship products, as well '
                           'as the rapid expansion of its services \n'
                           '    division. Analysts expect the company to continue its strong performance, with '
                           'projected revenue growth of 10% in the \n'
                           '    next fiscal year.\n'
                           '    ',
 'market_analysis': '\n'
                    '    {symbol} has maintained a strong presence in the market, consistently outperforming many of '
                    'its competitors. Analysts\n'
                    "    regard the stock as a strong buy, citing the company's steady growth trajectory, high "
                    'margins, and diverse revenue streams.\n'
                    '    Despite global economic challenges, {symbol} has continued to expand, particularly in '
                    'emerging markets where it has seen\n'
                    '    significant demand for its products. \n'
                    '\n'
                    "    The company operates in a highly competitive sector, with key rivals like {symbol}'s closest "
                    'competitors vying for market\n'
                    '    share. However, due to its strong brand loyalty and continuous innovation, {symbol} has '
                    'remained a top choice for both \n'
                    '    consumers and businesses. Recent quarterly reports have highlighted the company’s ability to '
                    'navigate challenges such as \n'
                    '    supply chain disruptions, inflationary pressures, and shifts in consumer behavior.\n'
                    '    ',
 'risks': '\n'
          '    Despite its strong performance, {symbol} faces several risks that could impact its future growth. One '
          'of the primary risks \n'
          '    is increased competition, particularly from smaller, more agile companies that are quickly gaining '
          'market share in niche \n'
          '    areas. Additionally, {symbol} operates in a sector that is highly sensitive to technological change, '
          'and the company \n'
          '    must continuously innovate to stay ahead.\n'
          '\n'
          '    Regulatory scrutiny is another concern for {symbol}, particularly in markets like the European Union, '
          'where new regulations \n'
          '    could affect the company’s ability to operate freely. There are also concerns about potential '
          'disruptions in the global supply \n'
          "    chain, which could impact the company's manufacturing and distribution capabilities, leading to delays "
          'in product launches.\n'
          '    ',
 'sustainability_initiatives': '\n'
                               '    {symbol} has been at the forefront of sustainability initiatives within its '
                               'industry. The company has made significant \n'
                               '    investments in renewable energy, with plans to power all of its global operations '
                               'with 100% renewable energy by 2025. \n'
                               '    {symbol} has also committed to reducing its carbon footprint, aiming to achieve '
                               'carbon neutrality across its entire \n'
                               '    supply chain by 2030.\n'
                               '\n'
                               '    In addition to its environmental efforts, {symbol} has implemented several '
                               'initiatives to promote diversity and inclusion \n'
                               '    within the company. These efforts have been well-received by both employees and '
                               'the wider public, enhancing the company’s \n'
                               '    reputation as a socially responsible corporate entity.\n'
                               '    ',
 'technical_analysis': '\n'
                       '    From a technical analysis perspective, {symbol} is currently trading within a key range '
                       'that has attracted significant\n'
                       '    attention from traders. The stock’s 50-day moving average (MA50) and 200-day moving '
                       'average (MA200) are converging, \n'
                       '    signaling a potential breakout. Additionally, the stock’s current price of $210.65 '
                       'reflects a period of consolidation, \n'
                       '    where it has been trading in a tight range between $200 and $220. \n'
                       '\n'
                       '    Indicators such as the Relative Strength Index (RSI) suggest that {symbol} is in neutral '
                       'territory, neither overbought \n'
                       '    nor oversold. Many traders are watching the Bollinger Bands, which have tightened in '
                       'recent weeks, indicating that the \n'
                       '    stock could experience higher volatility soon. Historical trends show that {symbol} tends '
                       'to rally after earnings \n'
                       "    announcements, especially when the company beats analysts' expectations.\n"
                       '    '}

TECHNOLOGY_EXTENSION = []


CURRENT_TIME = datetime(2024, 9, 1, 10, 30)

DEFAULT_STATE = {
    "orders": {
        12345: {
            "id": 12345,
            "order_type": "Buy",
            "symbol": "AAPL",
            "price": 210.65,
            "amount": 10,
            "status": "Completed",
        },
        12446: {
            "id": 12446,
            "order_type": "Sell",
            "symbol": "GOOG",
            "price": 2840.56,
            "amount": 5,
            "status": "Pending",
        },
    },
    "account_info": {
        "account_id": 12345,
        "balance": 10000.0,
        "binding_card": 1974202140965533,
    },
    "authenticated": False,
    "market_status": "Closed",
    "order_counter": 12446,
    "stocks": {
        "AAPL": {
            "price": 227.16,
            "percent_change": 0.17,
            "volume": 2.552,
            "MA(5)": 227.11,
            "MA(20)": 227.09,
        },
        "GOOG": {
            "price": 2840.34,
            "percent_change": 0.24,
            "volume": 1.123,
            "MA(5)": 2835.67,
            "MA(20)": 2842.15,
        },
        "TSLA": {
            "price": 667.92,
            "percent_change": -0.12,
            "volume": 1.654,
            "MA(5)": 671.15,
            "MA(20)": 668.20,
        },
        "MSFT": {
            "price": 310.23,
            "percent_change": 0.09,
            "volume": 3.234,
            "MA(5)": 309.88,
            "MA(20)": 310.11,
        },
        "NVDA": {
            "price": 220.34,
            "percent_change": 0.34,
            "volume": 1.234,
            "MA(5)": 220.45,
            "MA(20)": 220.67,
        },
        "ALPH": {
            "price": 1320.45,
            "percent_change": -0.08,
            "volume": 1.567,
            "MA(5)": 1321.12,
            "MA(20)": 1325.78,
        },
        "OMEG": {
            "price": 457.23,
            "percent_change": 0.12,
            "volume": 2.345,
            "MA(5)": 456.78,
            "MA(20)": 458.12,
        },
        "QUAS": {
            "price": 725.89,
            "percent_change": -0.03,
            "volume": 1.789,
            "MA(5)": 726.45,
            "MA(20)": 728.00,
        },
        "NEPT": {
            "price": 88.34,
            "percent_change": 0.19,
            "volume": 0.654,
            "MA(5)": 88.21,
            "MA(20)": 88.67,
        },
        "SYNX": {
            "price": 345.67,
            "percent_change": 0.11,
            "volume": 2.112,
            "MA(5)": 345.34,
            "MA(20)": 346.12,
        },
        "ZETA": {
            "price": 22.09,
            "percent_change": -0.05,
            "volume": 0.789,
            "MA(5)": 22.12,
            "MA(20)": 22.34,
        },
    },
    "watch_list": ["NVDA"],
    "transaction_history": [],
    "random_seed": 1053520,
}

class TradingBot:
    """
    A class representing a trading bot for executing stock trades and managing a trading account.

    Attributes:
        orders (Dict[int, Dict[str, Union[str, float, int]]]): A dictionary of orders for purchasing and selling of stock, keyed by order ID.
        account_info (Dict[str, Union[int, float]]): Information about the trading account.
        authenticated (bool): Whether the user is currently authenticated.
        market_status (str): The current status of the market ('Open' or 'Closed').
        order_counter (int): A counter for generating unique order IDs.
        stocks (Dict[str, Dict[str, Union[float, int]]]): Information about various stocks.
        watch_list (List[str]): A list of stock symbols being watched.
        transaction_history (List[Dict[str, Union[str, float, int]]]): A history of trading account related transactions.
    """

    def __init__(self):
        """
        Initialize the TradingBot instance.
        """
        self.orders: Dict[int, Dict[str, Union[str, float, int]]]
        self.account_info: Dict[str, Union[int, float]]
        self.authenticated: bool
        self.market_status: str
        self.order_counter: int
        self.stocks: Dict[str, Dict[str, Union[float, int]]]
        self.watch_list: List[str]
        self.transaction_history: List[Dict[str, Union[str, float, int]]]
        self._api_description = "This tool belongs to the trading system, which allows users to trade stocks, manage their account, and view stock information."

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        """
        Load a scenario into the TradingBot.

        Args:
            scenario (dict): A scenario dictionary containing data to load.
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.orders = scenario.get("orders", DEFAULT_STATE_COPY["orders"])
        # Convert all string keys that can be interpreted as integers to integer keys
        self.orders = {
            int(k) if isinstance(k, str) and k.isdigit() else k: v
            for k, v in self.orders.items()
        }
        self.account_info = scenario.get("account_info", DEFAULT_STATE_COPY["account_info"])
        self.authenticated = scenario.get(
            "authenticated", DEFAULT_STATE_COPY["authenticated"]
        )
        self.market_status = scenario.get(
            "market_status", DEFAULT_STATE_COPY["market_status"]
        )
        self.order_counter = scenario.get(
            "order_counter", DEFAULT_STATE_COPY["order_counter"]
        )  # Start counter from the next order ID
        self.stocks = scenario.get("stocks", DEFAULT_STATE_COPY["stocks"])
        self.watch_list = scenario.get("watch_list", DEFAULT_STATE_COPY["watch_list"])
        self.transaction_history = scenario.get(
            "transaction_history", DEFAULT_STATE_COPY["transaction_history"]
        )
        self.long_context = long_context
        self.random_seed = scenario.get("random_seed", DEFAULT_STATE_COPY["random_seed"])
        self._random = random.Random(
            (scenario.get("random_seed", DEFAULT_STATE_COPY["random_seed"]))
        )

    def _generate_transaction_timestamp(self) -> str:
        """
        Generate a timestamp for a transaction.

        Returns:
            timestamp (str): A formatted timestamp string.
        """
        # Define the start and end dates for the range
        start_date = CURRENT_TIME
        end_date = CURRENT_TIME + timedelta(days=1)

        start_timestamp = int(start_date.timestamp())
        end_timestamp = int(end_date.timestamp())

        # Generate a random timestamp within the range
        random_timestamp = self._random.randint(start_timestamp, end_timestamp)

        # Convert the random timestamp to a datetime object
        random_date = datetime.fromtimestamp(random_timestamp)

        return random_date.strftime("%Y-%m-%d %H:%M:%S")

    def get_env_state(self):
        return {
            "orders": self.orders,
            "account_info": self.account_info,
            "authenticated": self.authenticated,
            "market_status": self.market_status,
            "order_counter": self.order_counter,
            "stocks": self.stocks,
            "watch_list": self.watch_list,
            "transaction_history": self.transaction_history,
            "random_seed": self.random_seed,
        }

    def get_current_time(self) -> Dict[str, str]:
        """
        Get the current time.

        Returns:
            current_time (str): Current time in HH:MM AM/PM format.
        """
        return {"current_time": CURRENT_TIME.strftime("%I:%M %p")}

    def update_market_status(self, current_time_str: str) -> Dict[str, str]:
        """
        Update the market status based on the current time.

        Args:
            current_time_str (str): Current time in HH:MM AM/PM format.

        Returns:
            status (str): Status of the market. [Enum]: ["Open", "Closed"]
        """
        market_open_time = time(9, 30)  # Market opens at 9:30 AM
        market_close_time = time(16, 0)  # Market closes at 4:00 PM

        try:
            current_time = datetime.strptime(current_time_str, "%I:%M %p").time()
        except ValueError as e:
            return {"error": f"Invalid time format: {str(e)}"}

        if market_open_time <= current_time <= market_close_time:
            self.market_status = "Open"
            return {"status": "Open"}
        else:
            self.market_status = "Closed"
            return {"status": "Closed"}

    def get_symbol_by_name(self, name: str) -> Dict[str, str]:
        """
        Get the symbol of a stock by company name.

        Args:
            name (str): Name of the company.

        Returns:
            symbol (str): Symbol of the stock or an error dictionary if not available.
        """
        symbol_map = {
            "Apple": "AAPL",
            "Google": "GOOG",
            "Tesla": "TSLA",
            "Microsoft": "MSFT",
            "Nvidia": "NVDA",
            "Zeta Corp": "ZETA",
            "Alpha Tech": "ALPH",
            "Omega Industries": "OMEG",
            "Quasar Ltd.": "QUAS",
            "Neptune Systems": "NEPT",
            "Synex Solutions": "SYNX",
            "Amazon": "AMZN",
            "Gorilla": "GORI",
        }

        symbol = symbol_map.get(name)
        if not symbol:
            return {"error": "Stock not found"}
        
        return {"symbol": symbol}

    def get_stock_info(self, symbol: str) -> Dict[str, Union[float, int, str, list]]:
        """
        Get the details of a stock.

        Args:
            symbol (str): Symbol that uniquely identifies the stock.

        Returns:
            price (float): Current price of the stock.
            percent_change (float): Percentage change in stock price.
            volume (float): Trading volume of the stock.
            MA(5) (float): 5-day Moving Average of the stock.
            MA(20) (float): 20-day Moving Average of the stock.
        """
        if symbol not in self.stocks:
            return {"error": f"Stock with symbol '{symbol}' not found."}
        if self.long_context:
            stock = self.stocks[symbol].copy()
            stock["MA(5)"] = MA_5_EXTENSION
            stock["MA(20)"] = MA_20_EXTENSION
            return stock
        return self.stocks[symbol]

    def get_order_details(self, order_id: int) -> Dict[str, Union[str, float, int, dict]]:
        """
        Get the details of an order.

        Args:
            order_id (int): ID of the order.

        Returns:
            id (int): ID of the order.
            order_type (str): Type of the order.
            symbol (str): Symbol of the stock in the order.
            price (float): Price at which the order was placed.
            amount (int): Number of shares in the order.
            status (str): Current status of the order. [Enum]: ["Open", "Pending", "Completed", "Cancelled"]
        """
        if not self.authenticated:
            return {"error": "User not authenticated. Please log in to view order details."}
        if order_id not in self.orders:
            return {
                "error": f"Order with ID {order_id} not found."
                + "Here is the list of orders_id: "
                + str(list(self.orders.keys()))
            }

        if self.long_context:
            order = self.orders[order_id].copy()
            symbol = order["symbol"]

            formatted_extension = {}
            for key, value in ORDER_DETAIL_EXTENSION.items():
                try:
                    formatted_extension[key] = value.format(symbol=symbol)
                except KeyError as e:
                    return {"error": f"KeyError during formatting: {str(e)}"}

            # Add formatted extension to the order metadata
            order["metadata"] = formatted_extension
            return order

        return self.orders[order_id]

    def cancel_order(self, order_id: int) -> Dict[str, Union[int, str]]:
        """
        Cancel an order.

        Args:
            order_id (int): ID of the order to cancel.

        Returns:
            order_id (int): ID of the cancelled order.
            status (str): New status of the order after cancellation attempt.
        """
        if not self.authenticated:
            return {"error": "User not authenticated. Please log in to cancel an order."}
        if order_id not in self.orders:
            return {"error": f"Order with ID {order_id} not found."}
        if self.orders[order_id]["status"] == "Completed":
            return {"error": f"Can't cancel order {order_id}. Order is already completed."}
        self.orders[order_id]["status"] = "Cancelled"
        return {"order_id": order_id, "status": "Cancelled"}

    def place_order(
        self, order_type: str, symbol: str, price: float, amount: int
    ) -> Dict[str, Union[int, str, float]]:
        """
        Place an order.

        Args:
            order_type (str): Type of the order (Buy/Sell).
            symbol (str): Symbol of the stock to trade.
            price (float): Price at which to place the order.
            amount (int): Number of shares to trade.

        Returns:
            order_id (int): ID of the newly placed order.
            order_type (str): Type of the order (Buy/Sell).
            status (str): Initial status of the order.
            price (float): Price at which the order was placed.
            amount (int): Number of shares in the order.
        """
        if not self.authenticated:
            return {"error": "User not authenticated. Please log in to place an order."}
        if order_type not in ["Buy", "Sell"]:
            return {"error": f"Invalid order type: {order_type}"}
        if symbol not in self.stocks:
            return {"error": f"Invalid stock symbol: {symbol}"}
        
        try:
            price = float(price)
            amount = int(amount)
        except (ValueError, TypeError):
            return {"error": "Price and amount must be numeric values."}

        if price <= 0 or amount <= 0:
            return {"error": "Price and amount must be positive values."}
            
        order_id = self.order_counter
        self.orders[order_id] = {
            "id": order_id,
            "order_type": order_type,
            "symbol": symbol,
            "price": price,
            "amount": amount,
            "status": "Open",
        }
        self.order_counter += 1
        # We return the status as "Pending" to indicate that the order has been placed but not yet executed
        # When polled later, the status will show as 'Open'
        # This is to simulate the delay between placing an order and it being executed
        return {
            "order_id": order_id,
            "order_type": order_type,
            "status": "Pending",
            "price": price,
            "amount": amount,
        }

    def make_transaction(
        self, account_id: int, xact_type: str, amount: float
    ) -> Dict[str, Union[str, float]]:
        """
        Make a deposit or withdrawal based on specified amount.

        Args:
            account_id (int): ID of the account.
            xact_type (str): Transaction type (deposit or withdrawal).
            amount (float): Amount to deposit or withdraw.

        Returns:
            status (str): Status of the transaction.
            new_balance (float): Updated account balance after the transaction.
        """
        if not self.authenticated:
            return {"error": "User not authenticated. Please log in to make a transaction."}
        if self.market_status != "Open":
            return {"error": "Market is closed. Transactions are not allowed."}
        if account_id != self.account_info["account_id"]:
            return {"error": f"Account with ID {account_id} not found."}
            
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            return {"error": "Amount must be a numeric value."}

        if amount <= 0:
            return {"error": "Transaction amount must be positive."}

        if xact_type == "deposit":
            self.account_info["balance"] += amount
            self.transaction_history.append(
                {
                    "type": "deposit",
                    "amount": amount,
                    "timestamp": self._generate_transaction_timestamp(),
                }
            )
            return {
                "status": "Deposit successful",
                "new_balance": self.account_info["balance"],
            }
        elif xact_type == "withdrawal":
            if amount > self.account_info["balance"]:
                return {"error": "Insufficient funds for withdrawal."}
            self.account_info["balance"] -= amount
            self.transaction_history.append(
                {
                    "type": "withdrawal",
                    "amount": amount,
                    "timestamp": self._generate_transaction_timestamp(),
                }
            )
            return {
                "status": "Withdrawal successful",
                "new_balance": self.account_info["balance"],
            }
        return {"error": "Invalid transaction type. Use 'deposit' or 'withdrawal'."}

    def get_account_info(self) -> Dict[str, Union[int, float, str]]:
        """
        Get account information.

        Returns:
            account_id (int): ID of the account.
            balance (float): Current balance of the account.
            binding_card (int): Card number associated with the account.
        """
        if not self.authenticated:
            return {
                "error": "User not authenticated. Please log in to view account information."
            }
        return self.account_info

    def trading_login(self, username: str, password: str) -> Dict[str, str]:
        """
        Handle user login.

        Args:
            username (str): Username for authentication.
            password (str): Password for authentication.

        Returns:
            status (str): Login status message.
        """
        if not username or not password:
            return {"error": "Invalid credentials"}
            
        if self.authenticated:
            return {"status": "Already logged in"}
        # In a real system, we would validate the username and password here
        self.authenticated = True
        return {"status": "Logged in successfully"}

    def trading_get_login_status(self) -> Dict[str, bool]:
        """
        Get the login status.

        Returns:
            status (bool): Login status.
        """

        return {"status": bool(self.authenticated)}

    def trading_logout(self) -> Dict[str, str]:
        """
        Handle user logout for trading system.

        Returns:
            status (str): Logout status message.
        """
        if not self.authenticated:
            return {"status": "No user is currently logged in"}
        self.authenticated = False
        return {"status": "Logged out successfully"}

    def fund_account(self, amount: float) -> Dict[str, Union[str, float]]:
        """
        Fund the account with the specified amount.

        Args:
            amount (float): Amount to fund the account with.

        Returns:
            status (str): Status of the funding operation.
            new_balance (float): Updated account balance after funding.
        """
        if not self.authenticated:
            return {"error": "User not authenticated. Please log in to fund the account."}
            
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            return {"error": "Amount must be a numeric value."}

        if amount <= 0:
            return {"error": "Funding amount must be positive."}
            
        self.account_info["balance"] += amount
        self.transaction_history.append(
            {"type": "deposit", "amount": amount, "timestamp": self._generate_transaction_timestamp()}
        )
        return {
            "status": "Account funded successfully",
            "new_balance": self.account_info["balance"],
        }

    def remove_stock_from_watchlist(self, symbol: str) -> Dict[str, str]:
        """
        Remove a stock from the watchlist.

        Args:
            symbol (str): Symbol of the stock to remove.

        Returns:
            status (str): Status of the removal operation.
        """
        if not self.authenticated:
            return {
                "error": "User not authenticated. Please log in to modify the watchlist."
            }
        if symbol not in self.watch_list:
            return {"error": f"Stock {symbol} not found in watchlist."}
        self.watch_list.remove(symbol)
        return {"status": f"Stock {symbol} removed from watchlist successfully."}

    def get_watchlist(self) -> Dict[str, Any]:
        """
        Get the watchlist.

        Returns:
            watchlist (List[str]): List of stock symbols in the watchlist.
        """
        if not self.authenticated:
            return {"error": "User not authenticated. Please log in to view the watchlist."}

        if self.long_context:
            watch_list = self.watch_list.copy()
            watch_list.extend(WATCH_LIST_EXTENSION)
            return {"watchlist": watch_list}
        return {"watchlist": self.watch_list}

    def get_order_history(self) -> Dict[str, Any]:
        """
        Get the stock order ID history.

        Returns:
            history (List[int]): List of orders ID in the order history.
        """
        if not self.authenticated:
            return {"error": "User not authenticated. Please log in to view order history."}

        return {"history": list(self.orders.keys())}

    def get_transaction_history(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get the transaction history within a specified date range.

        Args:
            start_date (str): [Optional] Start date for the history (format: 'YYYY-MM-DD').
            end_date (str): [Optional] End date for the history (format: 'YYYY-MM-DD').

        Returns:
            transaction_history (List[Dict]): List of transactions within the specified date range.
                - type (str): Type of transaction. [Enum]: ["deposit", "withdrawal"]
                - amount (float): Amount involved in the transaction.
                - timestamp (str): Timestamp of the transaction, formatted as 'YYYY-MM-DD HH:MM:SS'.
        """
        if not self.authenticated:
            return {"error": "User not authenticated. Please log in to view transaction history."}

        if start_date:
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError as e:
                return {"error": f"Invalid start_date format: {str(e)}"}
        else:
            start = datetime.min

        if end_date:
            try:
                end = datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError as e:
                return {"error": f"Invalid end_date format: {str(e)}"}
        else:
            end = datetime.max

        filtered_history = [
            transaction
            for transaction in self.transaction_history
            if start
            <= datetime.strptime(transaction["timestamp"], "%Y-%m-%d %H:%M:%S")
            <= end
        ]

        if self.long_context:
            filtered_history.extend(TRANSACTION_HISTORY_EXTENSION)

        return {"transaction_history": filtered_history}

    def update_stock_price(
        self, symbol: str, new_price: float
    ) -> Dict[str, Union[str, float]]:
        """
        Update the price of a stock.

        Args:
            symbol (str): Symbol of the stock to update.
            new_price (float): New price of the stock.

        Returns:
            symbol (str): Symbol of the updated stock.
            old_price (float): Previous price of the stock.
            new_price (float): Updated price of the stock.
        """
        if symbol not in self.stocks:
            return {"error": f"Stock with symbol '{symbol}' not found."}
        if new_price <= 0:
            return {"error": "New price must be a positive value."}

        old_price = self.stocks[symbol]["price"]
        self.stocks[symbol]["price"] = new_price
        self.stocks[symbol]["percent_change"] = ((new_price - old_price) / old_price) * 100

        return {"symbol": symbol, "old_price": old_price, "new_price": new_price}

    # below contains a list of functions to be nested
    def get_available_stocks(self, sector: str) -> Dict[str, List[str]]:
        """
        Get a list of stock symbols in the given sector.

        Args:
            sector (str): The sector to retrieve stocks from (e.g., 'Technology').

        Returns:
            stock_list (List[str]): List of stock symbols in the specified sector.
        """
        sector_map = {
            "Technology": ["AAPL", "GOOG", "MSFT", "NVDA"],
            "Automobile": ["TSLA", "F", "GM"],
        }

        if self.long_context:
            sector_map["Technology"].extend(TECHNOLOGY_EXTENSION)
            sector_map["Automobile"].extend(AUTOMOBILE_EXTENSION)
        return {"stock_list": sector_map.get(sector, [])}

    def filter_stocks_by_price(
        self, stocks: List[str], min_price: float, max_price: float
    ) -> Dict[str, List[str]]:
        """
        Filter stocks based on a price range.

        Args:
            stocks (List[str]): List of stock symbols to filter.
            min_price (float): Minimum stock price.
            max_price (float): Maximum stock price.

        Returns:
            filtered_stocks (List[str]): Filtered list of stock symbols within the price range.
        """
        filtered_stocks = [
            symbol
            for symbol in stocks
            if self.stocks.get(symbol, {}).get("price", 0) >= min_price
            and self.stocks.get(symbol, {}).get("price", 0) <= max_price
        ]
        return {"filtered_stocks": filtered_stocks}

    def add_to_watchlist(self, stock: str) -> Dict[str, Any]:
        """
        Add a stock to the watchlist.

        Args:
            stock (str): the stock symbol to add to the watchlist.

        Returns:
            watchlist (List[str]): the watchlist that successfully added the stock.
        """
        if not self.authenticated:
            return {"error": "User not authenticated. Please log in."}
        if stock not in self.stocks:
            return {"error": "Invalid stock symbol"}
            
        if stock not in self.watch_list:
            self.watch_list.append(stock)
        return {"watchlist": self.watch_list}

    def notify_price_change(self, stocks: List[str], threshold: float) -> Dict[str, str]:
        """
        Notify if there is a significant price change in the stocks.

        Args:
            stocks (List[str]): List of stock symbols to check.
            threshold (float): Percentage change threshold to trigger a notification.

        Returns:
            notification (str): Notification message about the price changes.
        """
        changed_stocks = [
            symbol
            for symbol in stocks
            if symbol in self.stocks
            and abs(self.stocks[symbol]["percent_change"]) >= threshold
        ]

        if changed_stocks:
            return {"notification": f"Stocks {', '.join(changed_stocks)} have significant price changes."}
        else:
            return {"notification": "No significant price changes in the selected stocks."}

__TEST_CASES__ = [
    {
        'name': 'Authentication workflow covering login, status check, and logout',
        'steps': [
            {'expect_success': True, 'tool_call': "env['trading_bot'].trading_login(username='user1', password='password123')"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].trading_get_login_status()"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].trading_logout()"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].trading_get_login_status()"}
        ]
    },
    {
        'name': 'Market status update with normal and boundary time values',
        'steps': [
            {'expect_success': True, 'tool_call': "env['trading_bot'].get_current_time()"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].update_market_status(current_time_str='09:30 AM')"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].update_market_status(current_time_str='04:00 PM')"},
            {'expect_success': False, 'tool_call': "env['trading_bot'].update_market_status(current_time_str='25:00 PM')"}
        ]
    },
    {
        'name': 'Account funding and transactions with state-change verification',
        'steps': [
            {'expect_success': True, 'tool_call': "env['trading_bot'].trading_login(username='user1', password='password123')"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].update_market_status(current_time_str='10:00 AM')"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].get_account_info()"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].fund_account(amount=500.0)"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].make_transaction(account_id=12345, xact_type='withdrawal', amount=200.0)"},
            {'expect_success': False, 'tool_call': "env['trading_bot'].make_transaction(account_id=12345, xact_type='withdrawal', amount=-50.0)"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].get_transaction_history(start_date='2020-01-01', end_date='2030-01-01')"}
        ]
    },
    {
        'name': 'Watchlist management and stock info retrieval',
        'steps': [
            {'expect_success': True, 'tool_call': "env['trading_bot'].trading_login(username='user1', password='password123')"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].get_symbol_by_name(name='Apple')"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].get_stock_info(symbol='AAPL')"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].add_to_watchlist(stock='AAPL')"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].get_watchlist()"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].remove_stock_from_watchlist(symbol='NVDA')"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].get_watchlist()"}
        ]
    },
    {
        'name': 'Order placement, history retrieval, and cancellation workflow',
        'steps': [
            {'expect_success': True, 'tool_call': "env['trading_bot'].trading_login(username='user1', password='password123')"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].place_order(order_type='Buy', symbol='AAPL', price=220.0, amount=10)"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].get_order_history()"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].get_order_details(order_id=12446)"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].cancel_order(order_id=12446)"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].get_order_details(order_id=12446)"}
        ]
    },
    {
        'name': 'Error paths for authentication and account operations with invalid inputs',
        'steps': [
            {'expect_success': False, 'tool_call': "env['trading_bot'].trading_login(username='', password='')"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].trading_login(username='user1', password='password123')"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].update_market_status(current_time_str='10:00 AM')"},
            {'expect_success': False, 'tool_call': "env['trading_bot'].make_transaction(account_id=99999, xact_type='deposit', amount=100.0)"},
            {'expect_success': False, 'tool_call': "env['trading_bot'].fund_account(amount=0.0)"},
            {'expect_success': False, 'tool_call': "env['trading_bot'].fund_account(amount=-100.5)"}
        ]
    },
    {
        'name': 'Error paths for order placement and stock info with invalid parameters',
        'steps': [
            {'expect_success': True, 'tool_call': "env['trading_bot'].trading_login(username='user1', password='password123')"},
            {'expect_success': False, 'tool_call': "env['trading_bot'].place_order(order_type='Invalid', symbol='AAPL', price=100.0, amount=10)"},
            {'expect_success': False, 'tool_call': "env['trading_bot'].place_order(order_type='Buy', symbol='INVALID', price=100.0, amount=10)"},
            {'expect_success': False, 'tool_call': "env['trading_bot'].get_order_details(order_id=99999)"},
            {'expect_success': False, 'tool_call': "env['trading_bot'].cancel_order(order_id=99999)"},
            {'expect_success': False, 'tool_call': "env['trading_bot'].get_stock_info(symbol='INVALID')"}
        ]
    },
    {
        'name': 'Stock filtering, price update, and notification workflow',
        'steps': [
            {'expect_success': True, 'tool_call': "env['trading_bot'].get_available_stocks(sector='Technology')"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].filter_stocks_by_price(stocks=['AAPL', 'GOOG', 'TSLA'], min_price=200.0, max_price=1000.0)"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].update_stock_price(symbol='AAPL', new_price=250.0)"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].get_stock_info(symbol='AAPL')"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].notify_price_change(stocks=['AAPL', 'GOOG'], threshold=5.0)"}
        ]
    },
    {
        'name': 'Boundary testing with empty strings and excessively long inputs',
        'steps': [
            {'expect_success': True, 'tool_call': "env['trading_bot'].trading_login(username='user1', password='password123')"},
            {'expect_success': False, 'tool_call': "env['trading_bot'].get_symbol_by_name(name='')"},
            {'expect_success': False, 'tool_call': "env['trading_bot'].get_symbol_by_name(name='A very long company name that probably does not exist in the database at all')"},
            {'expect_success': False, 'tool_call': "env['trading_bot'].add_to_watchlist(stock='')"},
            {'expect_success': False, 'tool_call': "env['trading_bot'].remove_stock_from_watchlist(symbol='NONEXISTENT')"}
        ]
    },
    {
        'name': 'End-to-end trading workflow chaining multiple methods',
        'steps': [
            {'expect_success': True, 'tool_call': "env['trading_bot'].trading_login(username='testuser', password='password123')"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].fund_account(amount=1000.0)"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].get_stock_info(symbol='MSFT')"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].place_order(order_type='Buy', symbol='MSFT', price=310.0, amount=2)"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].get_order_history()"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].update_market_status(current_time_str='10:00 AM')"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].make_transaction(account_id=12345, xact_type='withdrawal', amount=100.0)"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].trading_logout()"},
            {'expect_success': True, 'tool_call': "env['trading_bot'].get_env_state()"}
        ]
    }
]