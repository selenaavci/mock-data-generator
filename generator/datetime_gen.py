"""Datetime data generator."""

import numpy as np
import pandas as pd


def generate_datetime(config: dict, num_rows: int) -> pd.Series:
    """Generate datetime data within a date range.

    Config keys:
        start_date: start date string (YYYY-MM-DD)
        end_date: end date string (YYYY-MM-DD)
        sequential: if True, generate sorted dates
        output_format: strftime format, e.g. "%Y-%m-%d" (None = keep as datetime)
        include_time: include time component in format
        business_days_only: exclude weekends
    """
    start = pd.Timestamp(config.get("start_date", "2020-01-01"))
    end = pd.Timestamp(config.get("end_date", "2024-12-31"))

    if start >= end:
        end = start + pd.Timedelta(days=365)

    start_ts = start.value // 10**9
    end_ts = end.value // 10**9

    business_days = config.get("business_days_only", False)
    include_time = config.get("include_time", False)

    # Over-generate to account for business-day filtering
    oversample = 2 if business_days else 1
    random_ts = np.random.randint(start_ts, end_ts + 1, size=num_rows * oversample)
    dates = pd.to_datetime(random_ts, unit="s")

    if business_days:
        mask = dates.dayofweek < 5
        dates = dates[mask][:num_rows]
        # If we got unlucky, refill with weekdays
        while len(dates) < num_rows:
            extra_ts = np.random.randint(start_ts, end_ts + 1, size=num_rows)
            extra = pd.to_datetime(extra_ts, unit="s")
            extra = extra[extra.dayofweek < 5]
            dates = dates.append(extra) if hasattr(dates, "append") else pd.DatetimeIndex(list(dates) + list(extra))
        dates = dates[:num_rows]

    if not include_time:
        dates = dates.normalize()

    if config.get("sequential", False):
        dates = dates.sort_values()

    series = pd.Series(dates).reset_index(drop=True)

    output_format = config.get("output_format")
    if output_format:
        series = series.dt.strftime(output_format)

    return series
