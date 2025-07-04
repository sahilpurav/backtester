from typing import Dict, List, Optional

import pandas as pd


class BacktestBroker:
    """
    Simulates a broker for bac            if existing_holding:
                # Update average price
                total_quantity = existing_holding["quantity"] + quantity
                total_value = (
                    existing_holding["quantity"] * existing_holding["buy_price"]
                ) + transaction_value
                existing_holding["buy_price"] = total_value / total_quantity
                existing_holding["quantity"] = total_quantity
            else:
                # Create new holding
                self.holdings.append(
                    {"symbol": symbol, "quantity": quantity, "buy_price": price}
                )oses.
    Mimics the interface of ZerodhaBroker but operates on historical data.
    """

    def __init__(self, initial_capital: float, transaction_cost_pct: float = 0.001190):
        """
        Initialize the backtest broker.

        Args:
            initial_capital: Starting cash amount
            transaction_cost_pct: Transaction cost as percentage (default: 0.1190%)
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.transaction_cost_pct = transaction_cost_pct
        self.holdings = (
            []
        )  # List of dict: {"symbol": str, "quantity": int, "buy_price": float}
        self.transactions = []  # Track all transactions for analysis
        self.current_date = None

    def cash(self) -> float:
        """Get current cash balance (matches live broker interface)."""
        return self.cash

    def get_holdings(self) -> List[Dict]:
        """
        Get current holdings in the same format as ZerodhaBroker.

        Returns:
            List of holdings: [{"symbol": str, "quantity": int, "buy_price": float}]
        """
        return self.holdings.copy()

    def get_cash_balance(self) -> float:
        """Get current cash balance."""
        return self.cash



    def get_portfolio_value(
        self, price_data: Dict[str, pd.DataFrame], date: pd.Timestamp
    ) -> float:
        """
        Calculate total portfolio value (cash + holdings market value).

        Args:
            price_data: Dict mapping symbols to price DataFrames
            date: Date for which to calculate portfolio value

        Returns:
            Total portfolio value
        """
        holdings_value = 0

        for holding in self.holdings:
            symbol = holding["symbol"]
            quantity = holding["quantity"]

            # Get price for equity symbols (add .NS suffix if needed)
            symbol_key = f"{symbol}.NS" if symbol not in price_data else symbol

            if symbol_key in price_data and date in price_data[symbol_key].index:
                price = price_data[symbol_key].loc[date, "Close"]
                holdings_value += quantity * price
            else:
                # If price not available, use last known buy price (conservative approach)
                holdings_value += quantity * holding["buy_price"]

        return self.cash + holdings_value

    def place_market_order(
        self,
        symbol: str,
        quantity: int,
        transaction_type: str,
        price: float,
        date: pd.Timestamp,
    ) -> Optional[str]:
        """
        Simulate placing a market order.

        Args:
            symbol: Stock symbol (without .NS suffix)
            quantity: Number of shares
            transaction_type: "BUY" or "SELL"
            price: Execution price
            date: Date of execution

        Returns:
            Mock order ID or None if order fails
        """
        if quantity <= 0:
            return None

        transaction_value = quantity * price
        transaction_cost = transaction_value * self.transaction_cost_pct

        if transaction_type == "BUY":
            total_cost = transaction_value + transaction_cost

            # Check if we have enough cash
            if total_cost > self.cash:
                print(
                    f"❌ Insufficient funds for {symbol}: Need ₹{total_cost:,.2f}, Have ₹{self.cash:,.2f}"
                )
                return None

            # Deduct cash
            self.cash -= total_cost

            # Add to holdings or update existing position
            existing_holding = next(
                (h for h in self.holdings if h["symbol"] == symbol), None
            )

            if existing_holding:
                # Update average price
                total_quantity = existing_holding["quantity"] + quantity
                total_value = (
                    existing_holding["quantity"] * existing_holding["buy_price"]
                ) + transaction_value
                existing_holding["buy_price"] = total_value / total_quantity
                existing_holding["quantity"] = total_quantity
            else:
                # Add new holding
                self.holdings.append(
                    {"symbol": symbol, "quantity": quantity, "buy_price": price}
                )

            # Record transaction
            self.transactions.append(
                {
                    "date": date,
                    "symbol": symbol,
                    "action": "BUY",
                    "quantity": quantity,
                    "price": price,
                    "transaction_cost": transaction_cost,
                    "cash_after": self.cash,
                }
            )

        elif transaction_type == "SELL":
            # Find holding to sell
            holding = next((h for h in self.holdings if h["symbol"] == symbol), None)

            if not holding or holding["quantity"] < quantity:
                print(
                    f"❌ Insufficient shares to sell {symbol}: Need {quantity}, Have {holding['quantity'] if holding else 0}"
                )
                return None

            # Update holding
            holding["quantity"] -= quantity

            # Remove holding if quantity becomes 0
            if holding["quantity"] == 0:
                self.holdings.remove(holding)

            # Add cash (minus transaction cost)
            net_proceeds = transaction_value - transaction_cost
            self.cash += net_proceeds

            # Record transaction
            self.transactions.append(
                {
                    "date": date,
                    "symbol": symbol,
                    "action": "SELL",
                    "quantity": quantity,
                    "price": price,
                    "transaction_cost": transaction_cost,
                    "cash_after": self.cash,
                }
            )

        return f"MOCK_ORDER_{symbol}_{date.strftime('%Y%m%d')}_{transaction_type}"

    def get_transactions(self) -> pd.DataFrame:
        """
        Get all transactions as a DataFrame for analysis.

        Returns:
            DataFrame with transaction history
        """
        if not self.transactions:
            return pd.DataFrame()

        return pd.DataFrame(self.transactions)

    def get_current_positions(self) -> List[Dict]:
        """
        Get current positions (alias for get_holdings for compatibility).
        """
        return self.get_holdings()

    def reset(self, initial_capital: float = None):
        """
        Reset the broker to initial state.

        Args:
            initial_capital: New initial capital (optional)
        """
        if initial_capital is not None:
            self.initial_capital = initial_capital

        self.cash = self.initial_capital
        self.holdings = []
        self.transactions = []
        self.current_date = None

        print(f"🔄 Broker reset with ₹{self.initial_capital:,.2f} initial capital")
