import os
from io import StringIO

import pandas as pd
import requests

from utils.cache import is_caching_enabled, load_from_file, save_to_file


def get_universe_symbols(
    universe: str = "nifty500", cache_dir: str = "cache/universe"
) -> list[str]:
    """
    Fetch and cache stock symbols from NSE for a given universe.

    Args:
        universe (str): e.g., "nifty50", "nifty100", "nifty500"
        cache_dir (str): Directory to store the cached file

    Returns:
        Tuple[List[str], List[str]]: raw NSE symbols, Yahoo-formatted symbols
    """

    try:
        size = int(universe.replace("nifty", ""))
    except ValueError:
        raise ValueError("Universe format should be like 'nifty100', 'nifty500' etc.")

    url = f"https://archives.nseindia.com/content/indices/ind_nifty{size}list.csv"
    cache_file = os.path.join(cache_dir, f"{universe}.csv")

    # Try to load from cache
    if is_caching_enabled():
        cached_data = load_from_file(cache_file)
        if cached_data is not None:
            df = pd.DataFrame(cached_data)
        else:
            response = requests.get(url)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch data from {url}")
            df = pd.read_csv(StringIO(response.text))

            # Convert to list of dicts for storage
            records = df.to_dict("records")
            save_to_file(records, cache_file)
    else:
        # Bypass cache if disabled
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data from {url}")
        df = pd.read_csv(StringIO(response.text))

    symbols = df["Symbol"].dropna().unique().tolist()

    # Exclude symbols starting with "DUMMY" and return the rest
    return [s for s in symbols if not s.startswith("DUMMY")]
