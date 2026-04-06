"""Datetime data generator."""

import numpy as np
import pandas as pd


def generate_datetime(config: dict, num_rows: int) -> pd.Series:
    """Generate datetime data within a date range.

    Config keys:
        start_date: start date string (YYYY-MM-DD)
        end_date: end date string (YYYY-MM-DD)
        sequential: if True, generate sorted dates
    """
    start = pd.Timestamp(config.get("start_date", "2020-01-01"))
    end = pd.Timestamp(config.get("end_date", "2024-12-31"))

    if start >= end:
        end = start + pd.Timedelta(days=365)

    start_ts = start.value // 10**9
    end_ts = end.value // 10**9

    random_ts = np.random.randint(start_ts, end_ts + 1, size=num_rows)
    dates = pd.to_datetime(random_ts, unit="s")

    if config.get("sequential", False):
        dates = dates.sort_values().reset_index(drop=True)

    return pd.Series(dates)
