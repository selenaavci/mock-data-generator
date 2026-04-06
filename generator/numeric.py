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
    """
    dist = config.get("distribution", "normal")
    vmin = config.get("min", 0)
    vmax = config.get("max", 100)
    is_int = config.get("is_int", False)

    if dist == "uniform":
        values = np.random.uniform(vmin, vmax, size=num_rows)
    else:  # normal
        mean = config.get("mean", (vmin + vmax) / 2)
        std = config.get("std", (vmax - vmin) / 6)
        if std <= 0:
            std = 1.0
        values = np.random.normal(mean, std, size=num_rows)
        values = np.clip(values, vmin, vmax)

    if is_int:
        values = np.round(values).astype(int)

    return pd.Series(values)
