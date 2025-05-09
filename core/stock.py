import os
import yfinance as yf
import pandas as pd
from typing import Optional
from curl_cffi import requests

class Stock:
    CACHE_DIR = "cache/stock"
    INVALID_SYMBOL_FILE = "cache/stock/invalid_symbols.txt"

    @classmethod
    def get_price(cls, symbol: str, start_date: str = "2015-01-01", force_refresh: bool = False) -> Optional[pd.DataFrame]:
        """
        Fetches and caches historical price data from Yahoo Finance.

        Args:
            symbol (str): Yahoo symbol, e.g., 'RELIANCE.NS'
            start_date (str): e.g., '2015-01-01'
            force_refresh (bool): If True, forces re-download from Yahoo

        Returns:
            pd.DataFrame: Historical OHLCV data
        """
        # Placeholder for actual implementation
        os.makedirs(cls.CACHE_DIR, exist_ok=True)
        cache_file = os.path.join(cls.CACHE_DIR, f"{symbol}.csv")

        if not force_refresh and os.path.exists(cache_file):
            try:
                return pd.read_csv(cache_file, parse_dates=['Date'], index_col='Date')
            except Exception as e:
                print(f"[warning] Could not read cache for {symbol}: {e}")
                os.remove(cache_file)

        try:
            print(f"[fetching] Downloading {symbol} from Yahoo Finance...")
            session = requests.Session(impersonate="chrome")
            df = yf.download(symbol, start=start_date, progress=False, auto_adjust=False, session=session)

            if df is None or df.empty:
                print(f"[warning] No data found for {symbol}")
                cls._record_invalid_symbol(symbol)
                return None

            # ✅ Ensure index is datetime
            df.index = pd.to_datetime(df.index)

            # Handle multi-index columns (flatten if necessary)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # Save to CSV with Date as column, return with DatetimeIndex
            df_to_save = df.copy().reset_index()
            df_to_save.columns.name = None
            df_to_save.to_csv(cache_file, index=False)

            return df

        except Exception as e:
            print(f"[error] Failed to fetch {symbol}: {e}")
            cls._record_invalid_symbol(symbol)
            return None
        
    @staticmethod
    def _record_invalid_symbol(symbol: str):
        if symbol.startswith("^"):
            return  # Don't mark index symbols like ^NSEI as invalid
        
        os.makedirs("cache", exist_ok=True)
        with open(Stock.INVALID_SYMBOL_FILE, "a") as f:
            f.write(symbol + "\n")