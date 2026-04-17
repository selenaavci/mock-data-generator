"""Numeric data generator (int and float)."""

import numpy as np
import pandas as pd


def generate_numeric(config: dict, num_rows: int) -> pd.Series:
    """Generate numeric data based on configuration.

    Config keys:
        distribution: "normal" or "uniform"
        min, max: value range
        mean, std: for normal distribution
        is_int: whether to round to integers
        decimals: decimal precision for float
        allow_negative: if False, clamp at 0
        sequential: if True, produce a sequence starting at min with step
        step: increment for sequential mode
    """
    dist = config.get("distribution", "normal")
    vmin = config.get("min", 0)
    vmax = config.get("max", 100)
    is_int = config.get("is_int", False)
    decimals = config.get("decimals", 2)
    allow_negative = config.get("allow_negative", True)
    sequential = config.get("sequential", False)
    step = config.get("step", 1)

    if sequential:
        start = vmin
        values = start + np.arange(num_rows) * step
        if is_int:
            values = values.astype(int)
    elif dist == "uniform":
        values = np.random.uniform(vmin, vmax, size=num_rows)
    else:  # normal
        mean = config.get("mean", (vmin + vmax) / 2)
        std = config.get("std", (vmax - vmin) / 6)
        if std <= 0:
            std = 1.0
        values = np.random.normal(mean, std, size=num_rows)
        values = np.clip(values, vmin, vmax)

    if not allow_negative:
        values = np.clip(values, 0, None)

    if is_int:
        values = np.round(values).astype(int)
    else:
        values = np.round(values, decimals)

    return pd.Series(values)
