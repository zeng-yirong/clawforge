"""
Stock Trading Platform Environment API

A simulated stock trading platform that manages real-time and historical data
for publicly traded securities, providing users access to current prices, volumes,
and other relevant market information.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime


DEFAULT_STATE: Dict[str, Any] = {
    # Stocks - real-time market data
    "stocks": {
        "AAPL": {
            "ticker_symbol": "AAPL",
            "company_name": "Apple Inc.",
            "current_price": 178.50,
            "volume": 52340000,
            "bid_price": 178.45,
            "ask_price": 178.55,
            "open_price": 177.00,
            "high_price": 179.20,
            "low_price": 176.80,
            "timestamp": "2024-01-15T10:30:00"
        },
        "TSLA": {
            "ticker_symbol": "TSLA",
            "company_name": "Tesla Inc.",
            "current_price": 245.30,
            "volume": 98760000,
            "bid_price": 245.20,
            "ask_price": 245.40,
            "open_price": 242.00,
            "high_price": 248.50,
            "low_price": 241.00,
            "timestamp": "2024-01-15T10:30:00"
        },
        "AMZN": {
            "ticker_symbol": "AMZN",
            "company_name": "Amazon.com Inc.",
            "current_price": 155.75,
            "volume": 45230000,
            "bid_price": 155.70,
            "ask_price": 155.80,
            "open_price": 154.50,
            "high_price": 156.90,
            "low_price": 154.20,
            "timestamp": "2024-01-15T10:30:00"
        },
        "GOOGL": {
            "ticker_symbol": "GOOGL",
            "company_name": "Alphabet Inc.",
            "current_price": 142.65,
            "volume": 23450000,
            "bid_price": 142.60,
            "ask_price": 142.70,
            "open_price": 141.80,
            "high_price": 143.50,
            "low_price": 141.50,
            "timestamp": "2024-01-15T10:30:00"
        }
    },
    
    # Market data feeds
    "market_feeds": {
        "NYSE_FEED": {
            "feed_id": "NYSE_FEED",
            "exchange_name": "New York Stock Exchange",
            "last_updated": "2024-01-15T10:30:00",
            "status": "active"
        },
        "NASDAQ_FEED": {
            "feed_id": "NASDAQ_FEED",
            "exchange_name": "NASDAQ",
            "last_updated": "2024-01-15T10:30:00",
            "status": "active"
        },
        "CBOE_FEED": {
            "feed_id": "CBOE_FEED",
            "exchange_name": "Chicago Board Options Exchange",
            "last_updated": "2024-01-15T10:29:00",
            "status": "active"
        }
    },
    
    # User portfolios
    "user_portfolios": {
        "user_001": {
            "user_id": "user_001",
            "stocks_held": {
                "AAPL": {"purchase_price": 165.00, "quantity": 50},
                "TSLA": {"purchase_price": 230.00, "quantity": 20}
            },
            "last_updated": "2024-01-15T09:00:00"
        },
        "user_002": {
            "user_id": "user_002",
            "stocks_held": {
                "AMZN": {"purchase_price": 148.50, "quantity": 30},
                "GOOGL": {"purchase_price": 138.00, "quantity": 25}
            },
            "last_updated": "2024-01-15T09:15:00"
        },
        "user_003": {
            "user_id": "user_003",
            "stocks_held": {
                "AAPL": {"purchase_price": 170.00, "quantity": 100}
            },
            "last_updated": "2024-01-15T08:45:00"
        }
    },
    
    # Trade transactions
    "trade_transactions": [
        {
            "transaction_id": "txn_001",
            "user_id": "user_001",
            "ticker_symbol": "AAPL",
            "quantity": 50,
            "price": 165.00,
            "trade_type": "buy",
            "timestamp": "2024-01-10T11:30:00"
        },
        {
            "transaction_id": "txn_002",
            "user_id": "user_001",
            "ticker_symbol": "TSLA",
            "quantity": 20,
            "price": 230.00,
            "trade_type": "buy",
            "timestamp": "2024-01-12T14:15:00"
        },
        {
            "transaction_id": "txn_003",
            "user_id": "user_002",
            "ticker_symbol": "AMZN",
            "quantity": 30,
            "price": 148.50,
            "trade_type": "buy",
            "timestamp": "2024-01-11T10:00:00"
        }
    ],
    
    # Market status and settings
    "market_status": {
        "is_open": True,
        "market_hours_start": "09:30",
        "market_hours_end": "16:00",
        "timezone": "America/New_York"
    },
    
    # After-hours trading setting
    "after_hours_trading_enabled": False,
    
    # User subscriptions for data access
    "user_subscriptions": {
        "user_001": {"has_realtime_access": True, "subscription_tier": "premium"},
        "user_002": {"has_realtime_access": True, "subscription_tier": "basic"},
        "user_003": {"has_realtime_access": False, "subscription_tier": "free"}
    },
    
    # Current authenticated user
    "current_user": "user_001",
    
    # Transaction counter for generating IDs
    "transaction_counter": 3
}


class StockTradingPlatform:
    """
    A stock trading platform environment that manages real-time and historical data
    for publicly traded securities, providing users access to current prices, volumes,
    and other relevant market information.
    
    The platform supports querying stock data, executing trades, managing portfolios,
    and tracking transaction histories.
    """
    
    def __init__(self) -> None:
        """
        Initialize the StockTradingPlatform environment.
        
        Declares all state attributes with type hints and sets up the API description.
        
        Returns:
            None
        """
        self.stocks: Dict[str, Dict[str, Any]] = {}
        self.market_feeds: Dict[str, Dict[str, Any]] = {}
        self.user_portfolios: Dict[str, Dict[str, Any]] = {}
        self.trade_transactions: List[Dict[str, Any]] = []
        self.market_status: Dict[str, Any] = {}
        self.after_hours_trading_enabled: bool = False
        self.user_subscriptions: Dict[str, Dict[str, Any]] = {}
        self.current_user: str = ""
        self.transaction_counter: int = 0
        
        self._api_description = (
            "A stock trading platform API for querying real-time market data, "
            "executing trades, and managing user portfolios."
        )
    
    def _timestamp(self) -> str:
        """
        Generate a consistent timestamp string for all operations.
        
        Returns:
            str: ISO format timestamp string.
        """
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: Dictionary containing initial state values.
            long_context: Flag for long context scenarios (not used currently).
        
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
        Return a dictionary containing all current environment state variables.
        
        Returns:
            Dict[str, Any]: A dictionary with all internal state variables including:
                - stocks: Current stock data keyed by ticker symbol
                - market_feeds: Market data feed information
                - user_portfolios: User portfolio holdings
                - trade_transactions: List of all trade transactions
                - market_status: Current market open/closed status
                - after_hours_trading_enabled: Whether after-hours trading is enabled
                - user_subscriptions: User subscription and access information
                - current_user: Currently authenticated user ID
                - transaction_counter: Counter for generating transaction IDs
        """
        return {
            "stocks": deepcopy(self.stocks),
            "market_feeds": deepcopy(self.market_feeds),
            "user_portfolios": deepcopy(self.user_portfolios),
            "trade_transactions": deepcopy(self.trade_transactions),
            "market_status": deepcopy(self.market_status),
            "after_hours_trading_enabled": self.after_hours_trading_enabled,
            "user_subscriptions": deepcopy(self.user_subscriptions),
            "current_user": self.current_user,
            "transaction_counter": self.transaction_counter
        }
    
    # ==================== Query Operations ====================
    
    def get_stock_by_symbol(self, ticker_symbol: str) -> Dict[str, Any]:
        """
        Retrieve full real-time information for a given ticker symbol.
        
        Args:
            ticker_symbol: The stock ticker symbol (e.g., 'AAPL').
        
        Returns:
            Dict[str, Any]: Stock data including price, volume, bid/ask, etc.,
                           or an error dict if the ticker is not found.
        """
        ticker_upper = ticker_symbol.upper()
        if ticker_upper not in self.stocks:
            return {"error": f"Stock with ticker symbol '{ticker_symbol}' not found"}
        
        return {"success": True, "stock": deepcopy(self.stocks[ticker_upper])}
    
    def get_stocks_by_symbols(self, ticker_symbols: List[str]) -> Dict[str, Any]:
        """
        Retrieve current market data for multiple ticker symbols in one request.
        
        Args:
            ticker_symbols: List of ticker symbols (e.g., ['AAPL', 'TSLA', 'AMZN']).
        
        Returns:
            Dict[str, Any]: Dictionary containing found stocks and any not found symbols.
        """
        if not ticker_symbols:
            return {"error": "No ticker symbols provided"}
        
        found_stocks = {}
        not_found = []
        
        for symbol in ticker_symbols:
            symbol_upper = symbol.upper()
            if symbol_upper in self.stocks:
                found_stocks[symbol_upper] = deepcopy(self.stocks[symbol_upper])
            else:
                not_found.append(symbol)
        
        result: Dict[str, Any] = {"success": True, "stocks": found_stocks}
        if not_found:
            result["not_found"] = not_found
        
        return result
    
    def get_current_price(self, ticker_symbol: str) -> Dict[str, Any]:
        """
        Get only the current trading price of a stock.
        
        Args:
            ticker_symbol: The stock ticker symbol.
        
        Returns:
            Dict[str, Any]: Current price or error if ticker not found.
        """
        ticker_upper = ticker_symbol.upper()
        if ticker_upper not in self.stocks:
            return {"error": f"Stock with ticker symbol '{ticker_symbol}' not found"}
        
        return {
            "success": True,
            "ticker_symbol": ticker_upper,
            "current_price": self.stocks[ticker_upper]["current_price"]
        }
    
    def get_bid_ask_spread(self, ticker_symbol: str) -> Dict[str, Any]:
        """
        Retrieve the current bid and ask prices for a stock to calculate spread.
        
        Args:
            ticker_symbol: The stock ticker symbol.
        
        Returns:
            Dict[str, Any]: Bid price, ask price, and calculated spread.
        """
        ticker_upper = ticker_symbol.upper()
        if ticker_upper not in self.stocks:
            return {"error": f"Stock with ticker symbol '{ticker_symbol}' not found"}
        
        stock = self.stocks[ticker_upper]
        spread = round(stock["ask_price"] - stock["bid_price"], 2)
        
        return {
            "success": True,
            "ticker_symbol": ticker_upper,
            "bid_price": stock["bid_price"],
            "ask_price": stock["ask_price"],
            "spread": spread
        }
    
    def get_market_status(self) -> Dict[str, Any]:
        """
        Check whether the market is currently open or closed.
        
        Returns:
            Dict[str, Any]: Market status information including open/closed state.
        """
        return {
            "success": True,
            "is_open": self.market_status.get("is_open", False),
            "market_hours_start": self.market_status.get("market_hours_start"),
            "market_hours_end": self.market_status.get("market_hours_end"),
            "timezone": self.market_status.get("timezone")
        }
    
    def check_after_hours_trading(self) -> Dict[str, Any]:
        """
        Determine if after-hours trading is enabled for price updates.
        
        Returns:
            Dict[str, Any]: After-hours trading status.
        """
        return {
            "success": True,
            "after_hours_trading_enabled": self.after_hours_trading_enabled
        }
    
    def get_user_portfolio(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve the list of stocks held by a user, including quantities and purchase prices.
        
        Args:
            user_id: The unique identifier of the user.
        
        Returns:
            Dict[str, Any]: User's portfolio data or error if user not found.
        """
        if user_id not in self.user_portfolios:
            return {"error": f"Portfolio for user '{user_id}' not found"}
        
        return {
            "success": True,
            "portfolio": deepcopy(self.user_portfolios[user_id])
        }
    
    def get_user_transaction_history(self, user_id: str, limit: int = 50) -> Dict[str, Any]:
        """
        List all past buy/sell transactions for a given user.
        
        Args:
            user_id: The unique identifier of the user.
            limit: Maximum number of transactions to return.
        
        Returns:
            Dict[str, Any]: List of user's transactions.
        """
        user_transactions = [
            deepcopy(txn) for txn in self.trade_transactions
            if txn["user_id"] == user_id
        ]
        
        # Apply limit
        limited_transactions = user_transactions[-limit:] if limit > 0 else user_transactions
        
        return {
            "success": True,
            "user_id": user_id,
            "transactions": limited_transactions,
            "total_count": len(user_transactions),
            "returned_count": len(limited_transactions)
        }
    
    def get_latest_market_feed(self) -> Dict[str, Any]:
        """
        Get the status and last update time of the primary market data feed.
        
        Returns:
            Dict[str, Any]: Market feed status information.
        """
        if not self.market_feeds:
            return {"error": "No market feeds configured"}
        
        # Return the most recently updated feed
        latest_feed = None
        latest_time = ""
        
        for feed_id, feed_data in self.market_feeds.items():
            if feed_data.get("last_updated", "") > latest_time:
                latest_time = feed_data["last_updated"]
                latest_feed = feed_data
        
        return {
            "success": True,
            "latest_feed": deepcopy(latest_feed)
        }
    
    def is_valid_ticker(self, ticker_symbol: str) -> Dict[str, Any]:
        """
        Validate whether a given ticker symbol exists and is active in the system.
        
        Args:
            ticker_symbol: The ticker symbol to validate.
        
        Returns:
            Dict[str, Any]: Validation result.
        """
        ticker_upper = ticker_symbol.upper()
        is_valid = ticker_upper in self.stocks
        
        return {
            "success": True,
            "ticker_symbol": ticker_symbol,
            "is_valid": is_valid
        }
    
    def check_data_access_permission(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Verify if the current user has subscription or authentication to access real-time data.
        
        Args:
            user_id: Optional user ID to check. If not provided, uses current_user.
        
        Returns:
            Dict[str, Any]: Access permission details.
        """
        check_user = user_id if user_id else self.current_user
        
        if not check_user:
            return {"error": "No user specified and no current user authenticated"}
        
        if check_user not in self.user_subscriptions:
            return {"error": f"User '{check_user}' not found in subscription system"}
        
        subscription = self.user_subscriptions[check_user]
        
        return {
            "success": True,
            "user_id": check_user,
            "has_realtime_access": subscription.get("has_realtime_access", False),
            "subscription_tier": subscription.get("subscription_tier", "none")
        }
    
    def search_stocks(self, query: str) -> Dict[str, Any]:
        """
        Search for stocks by company name or ticker symbol.
        
        Args:
            query: Search query string.
        
        Returns:
            Dict[str, Any]: Search results containing matching stocks.
        """
        if not query:
            return {"error": "Search query cannot be empty"}
        
        query_lower = query.lower()
        results = []
        
        for ticker, stock_data in self.stocks.items():
            if (query_lower in ticker.lower() or 
                query_lower in stock_data.get("company_name", "").lower()):
                results.append({
                    "ticker_symbol": ticker,
                    "company_name": stock_data["company_name"],
                    "current_price": stock_data["current_price"]
                })
        
        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        }
    
    def get_market_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the overall market including major indices.
        
        Returns:
            Dict[str, Any]: Market summary with indices information.
        """
        # Calculate aggregate stats from available stocks
        total_volume = sum(stock["volume"] for stock in self.stocks.values())
        avg_price = (
            sum(stock["current_price"] for stock in self.stocks.values()) / len(self.stocks)
            if self.stocks else 0
        )
        
        indices = {
            "total_stocks_tracked": len(self.stocks),
            "total_volume": total_volume,
            "average_price": round(avg_price, 2)
        }
        
        return {
            "success": True,
            "indices": indices,
            "market_status": self.market_status.get("is_open", False),
            "timestamp": self._timestamp()
        }
    
    def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get a stock quote including price and daily change information.
        
        Args:
            symbol: The stock ticker symbol.
        
        Returns:
            Dict[str, Any]: Stock quote with price, change, and change percent.
        """
        ticker_upper = symbol.upper()
        if ticker_upper not in self.stocks:
            return {"error": f"Stock with symbol '{symbol}' not found"}
        
        stock = self.stocks[ticker_upper]
        current_price = stock["current_price"]
        open_price = stock["open_price"]
        change = round(current_price - open_price, 2)
        change_percent = round((change / open_price) * 100, 2) if open_price > 0 else 0
        
        return {
            "success": True,
            "symbol": ticker_upper,
            "price": current_price,
            "change": change,
            "change_percent": change_percent,
            "volume": stock["volume"],
            "timestamp": stock["timestamp"]
        }
    
    # ==================== State Change Operations ====================
    
    def update_stock_price(
        self,
        ticker_symbol: str,
        new_price: float,
        new_bid: Optional[float] = None,
        new_ask: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Update the current_price of a stock, subject to market hours or after-hours rules.
        
        Args:
            ticker_symbol: The stock ticker symbol to update.
            new_price: The new current price.
            new_bid: Optional new bid price.
            new_ask: Optional new ask price.
        
        Returns:
            Dict[str, Any]: Update result or error if constraints violated.
        """
        ticker_upper = ticker_symbol.upper()
        
        # Validate ticker exists
        if ticker_upper not in self.stocks:
            return {"error": f"Stock with ticker symbol '{ticker_symbol}' not found"}
        
        # Check market hours constraint
        market_open = self.market_status.get("is_open", False)
        if not market_open and not self.after_hours_trading_enabled:
            return {
                "error": "Cannot update stock price: Market is closed and after-hours trading is disabled"
            }
        
        # Validate price is positive
        if new_price <= 0:
            return {"error": "Price must be a positive value"}
        
        stock = self.stocks[ticker_upper]
        stock["current_price"] = round(new_price, 2)
        
        # Update bid/ask if provided
        if new_bid is not None:
            if new_bid <= 0:
                return {"error": "Bid price must be a positive value"}
            stock["bid_price"] = round(new_bid, 2)
        
        if new_ask is not None:
            if new_ask <= 0:
                return {"error": "Ask price must be a positive value"}
            stock["ask_price"] = round(new_ask, 2)
        
        # Update high/low if needed
        if new_price > stock["high_price"]:
            stock["high_price"] = round(new_price, 2)
        if new_price < stock["low_price"]:
            stock["low_price"] = round(new_price, 2)
        
        stock["timestamp"] = self._timestamp()
        
        return {
            "success": True,
            "ticker_symbol": ticker_upper,
            "updated_price": stock["current_price"],
            "message": "Stock price updated successfully"
        }
    
    def execute_trade(
        self,
        user_id: str,
        ticker_symbol: str,
        quantity: int,
        trade_type: str,
        price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Perform a buy or sell transaction for a user, updating portfolio and recording transaction.
        
        Args:
            user_id: The user executing the trade.
            ticker_symbol: The stock ticker symbol.
            quantity: Number of shares to trade.
            trade_type: Either 'buy' or 'sell'.
            price: Optional execution price. If not provided, uses current price.
        
        Returns:
            Dict[str, Any]: Trade execution result or error.
        """
        ticker_upper = ticker_symbol.upper()
        
        # Validate ticker
        if ticker_upper not in self.stocks:
            return {"error": f"Stock with ticker symbol '{ticker_symbol}' not found"}
        
        # Validate trade type
        if trade_type not in ["buy", "sell"]:
            return {"error": "Trade type must be 'buy' or 'sell'"}
        
        # Validate quantity
        if quantity <= 0:
            return {"error": "Quantity must be a positive integer"}
        
        # Use current price if not specified
        execution_price = price if price else self.stocks[ticker_upper]["current_price"]
        
        if execution_price <= 0:
            return {"error": "Execution price must be positive"}
        
        # Initialize portfolio if user doesn't have one
        if user_id not in self.user_portfolios:
            self.user_portfolios[user_id] = {
                "user_id": user_id,
                "stocks_held": {},
                "last_updated": self._timestamp()
            }
        
        portfolio = self.user_portfolios[user_id]
        
        if trade_type == "sell":
            # Check if user has enough shares to sell
            if ticker_upper not in portfolio["stocks_held"]:
                return {"error": f"User does not hold any shares of {ticker_upper}"}
            
            held_quantity = portfolio["stocks_held"][ticker_upper]["quantity"]
            if held_quantity < quantity:
                return {
                    "error": f"Insufficient shares. User holds {held_quantity} shares of {ticker_upper}, "
                            f"attempted to sell {quantity}"
                }
            
            # Execute sell
            portfolio["stocks_held"][ticker_upper]["quantity"] -= quantity
            if portfolio["stocks_held"][ticker_upper]["quantity"] == 0:
                del portfolio["stocks_held"][ticker_upper]
        
        else:  # buy
            if ticker_upper in portfolio["stocks_held"]:
                # Average the purchase price
                existing = portfolio["stocks_held"][ticker_upper]
                total_cost = (existing["purchase_price"] * existing["quantity"]) + (execution_price * quantity)
                total_quantity = existing["quantity"] + quantity
                portfolio["stocks_held"][ticker_upper] = {
                    "purchase_price": round(total_cost / total_quantity, 2),
                    "quantity": total_quantity
                }
            else:
                portfolio["stocks_held"][ticker_upper] = {
                    "purchase_price": round(execution_price, 2),
                    "quantity": quantity
                }
        
        portfolio["last_updated"] = self._timestamp()
        
        # Record transaction
        self.transaction_counter += 1
        transaction = {
            "transaction_id": f"txn_{self.transaction_counter:03d}",
            "user_id": user_id,
            "ticker_symbol": ticker_upper,
            "quantity": quantity,
            "price": round(execution_price, 2),
            "trade_type": trade_type,
            "timestamp": self._timestamp()
        }
        self.trade_transactions.append(transaction)
        
        return {
            "success": True,
            "transaction": deepcopy(transaction),
            "message": f"Successfully executed {trade_type} order for {quantity} shares of {ticker_upper}"
        }
    
    def add_stock_to_portfolio(
        self,
        user_id: str,
        symbol: str,
        shares: int,
        purchase_price: float
    ) -> Dict[str, Any]:
        """
        Add a stock to a user's portfolio.
        
        Args:
            user_id: The user identifier.
            symbol: The stock ticker symbol.
            shares: Number of shares to add.
            purchase_price: The purchase price per share.
        
        Returns:
            Dict[str, Any]: Result of adding stock to portfolio.
        """
        if shares <= 0:
            return {"error": "Shares must be a positive integer"}
        
        if purchase_price <= 0:
            return {"error": "Purchase price must be positive"}
        
        ticker_upper = symbol.upper()
        
        # Initialize portfolio if user doesn't have one
        if user_id not in self.user_portfolios:
            self.user_portfolios[user_id] = {
                "user_id": user_id,
                "stocks_held": {},
                "last_updated": self._timestamp()
            }
        
        portfolio = self.user_portfolios[user_id]
        
        if ticker_upper in portfolio["stocks_held"]:
            # Average the purchase price
            existing = portfolio["stocks_held"][ticker_upper]
            total_cost = (existing["purchase_price"] * existing["quantity"]) + (purchase_price * shares)
            total_quantity = existing["quantity"] + shares
            portfolio["stocks_held"][ticker_upper] = {
                "purchase_price": round(total_cost / total_quantity, 2),
                "quantity": total_quantity
            }
        else:
            portfolio["stocks_held"][ticker_upper] = {
                "purchase_price": round(purchase_price, 2),
                "quantity": shares
            }
        
        portfolio["last_updated"] = self._timestamp()
        
        return {
            "success": True,
            "user_id": user_id,
            "symbol": ticker_upper,
            "shares": shares,
            "purchase_price": round(purchase_price, 2),
            "message": f"Added {shares} shares of {ticker_upper} to portfolio"
        }
    
    def remove_stock_from_portfolio(
        self,
        user_id: str,
        symbol: str,
        shares: int
    ) -> Dict[str, Any]:
        """
        Remove shares of a stock from a user's portfolio.
        
        Args:
            user_id: The user identifier.
            symbol: The stock ticker symbol.
            shares: Number of shares to remove.
        
        Returns:
            Dict[str, Any]: Result of removing stock from portfolio.
        """
        if shares <= 0:
            return {"error": "Shares must be a positive integer"}
        
        ticker_upper = symbol.upper()
        
        if user_id not in self.user_portfolios:
            return {"error": f"Portfolio for user '{user_id}' not found"}
        
        portfolio = self.user_portfolios[user_id]
        
        if ticker_upper not in portfolio["stocks_held"]:
            return {"error": f"User does not hold any shares of {ticker_upper}"}
        
        held_quantity = portfolio["stocks_held"][ticker_upper]["quantity"]
        if held_quantity < shares:
            return {
                "error": f"Insufficient shares. User holds {held_quantity} shares of {ticker_upper}, "
                        f"attempted to remove {shares}"
            }
        
        portfolio["stocks_held"][ticker_upper]["quantity"] -= shares
        shares_sold = shares
        
        if portfolio["stocks_held"][ticker_upper]["quantity"] == 0:
            del portfolio["stocks_held"][ticker_upper]
        
        portfolio["last_updated"] = self._timestamp()
        
        return {
            "success": True,
            "user_id": user_id,
            "symbol": ticker_upper,
            "shares_sold": shares_sold,
            "message": f"Removed {shares_sold} shares of {ticker_upper} from portfolio"
        }

    def get_portfolio(self, user_id: str) -> dict:
        """Get a user's portfolio."""
        if user_id not in self.portfolios:
            return {"error": f"User {user_id} not found"}
        
        portfolio = self.portfolios[user_id]
        return {
            "user_id": user_id,
            "stocks_held": portfolio["stocks_held"].copy(),
            "last_updated": portfolio["last_updated"]
        }

    def get_portfolio_value(self, user_id: str, prices: dict) -> dict:
        """Calculate the total value of a user's portfolio given current prices."""
        if user_id not in self.portfolios:
            return {"error": f"User {user_id} not found"}
        
        portfolio = self.portfolios[user_id]
        total_value = 0.0
        holdings = []
        
        for ticker, data in portfolio["stocks_held"].items():
            quantity = data["quantity"]
            if ticker in prices:
                current_price = prices[ticker]
                value = quantity * current_price
                total_value += value
                holdings.append({
                    "symbol": ticker,
                    "quantity": quantity,
                    "price": current_price,
                    "value": value
                })
            else:
                holdings.append({
                    "symbol": ticker,
                    "quantity": quantity,
                    "price": None,
                    "value": None
                })
        
        return {
            "user_id": user_id,
            "holdings": holdings,
            "total_value": total_value,
            "last_updated": portfolio["last_updated"]
        }

    def _timestamp(self) -> str:
        """Generate a timestamp string."""
        from datetime import datetime
        return datetime.now().isoformat()


__TEST_CASES__ = [
    {
        "name": "create_portfolio_success",
        "input": {"user_id": "user123"},
        "method": "create_portfolio",
        "expected": {"success": True, "user_id": "user123"}
    },
    {
        "name": "create_portfolio_duplicate",
        "setup": [{"method": "create_portfolio", "input": {"user_id": "user456"}}],
        "input": {"user_id": "user456"},
        "method": "create_portfolio",
        "expected_error": "already exists"
    },
    {
        "name": "add_stock_success",
        "setup": [{"method": "create_portfolio", "input": {"user_id": "user789"}}],
        "input": {"user_id": "user789", "ticker": "AAPL", "shares": 10},
        "method": "add_stock",
        "expected": {"success": True, "symbol": "AAPL", "shares_added": 10}
    },
    {
        "name": "add_stock_user_not_found",
        "input": {"user_id": "nonexistent", "ticker": "AAPL", "shares": 10},
        "method": "add_stock",
        "expected_error": "not found"
    },
    {
        "name": "add_stock_invalid_shares",
        "setup": [{"method": "create_portfolio", "input": {"user_id": "userA"}}],
        "input": {"user_id": "userA", "ticker": "AAPL", "shares": -5},
        "method": "add_stock",
        "expected_error": "positive"
    },
    {
        "name": "remove_stock_success",
        "setup": [
            {"method": "create_portfolio", "input": {"user_id": "userB"}},
            {"method": "add_stock", "input": {"user_id": "userB", "ticker": "GOOGL", "shares": 20}}
        ],
        "input": {"user_id": "userB", "ticker": "GOOGL", "shares": 5},
        "method": "remove_stock",
        "expected": {"success": True, "symbol": "GOOGL", "shares_sold": 5}
    },
    {
        "name": "remove_stock_insufficient",
        "setup": [
            {"method": "create_portfolio", "input": {"user_id": "userC"}},
            {"method": "add_stock", "input": {"user_id": "userC", "ticker": "MSFT", "shares": 5}}
        ],
        "input": {"user_id": "userC", "ticker": "MSFT", "shares": 10},
        "method": "remove_stock",
        "expected_error": "Insufficient"
    },
    {
        "name": "remove_stock_not_held",
        "setup": [{"method": "create_portfolio", "input": {"user_id": "userD"}}],
        "input": {"user_id": "userD", "ticker": "TSLA", "shares": 5},
        "method": "remove_stock",
        "expected_error": "does not hold"
    },
    {
        "name": "get_portfolio_success",
        "setup": [
            {"method": "create_portfolio", "input": {"user_id": "userE"}},
            {"method": "add_stock", "input": {"user_id": "userE", "ticker": "AMZN", "shares": 15}}
        ],
        "input": {"user_id": "userE"},
        "method": "get_portfolio",
        "expected": {"user_id": "userE"}
    },
    {
        "name": "get_portfolio_value",
        "setup": [
            {"method": "create_portfolio", "input": {"user_id": "userF"}},
            {"method": "add_stock", "input": {"user_id": "userF", "ticker": "AAPL", "shares": 10}},
            {"method": "add_stock", "input": {"user_id": "userF", "ticker": "GOOGL", "shares": 5}}
        ],
        "input": {"user_id": "userF", "prices": {"AAPL": 150.0, "GOOGL": 2800.0}},
        "method": "get_portfolio_value",
        "expected": {"user_id": "userF", "total_value": 15500.0}
    }
]