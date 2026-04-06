"""Categorical data generator."""

import numpy as np
import pandas as pd


def generate_categorical(config: dict, num_rows: int) -> pd.Series:
    """Generate categorical data based on value list and weights.

    Config keys:
        values: list of possible values
        weights: list of probabilities (same length as values)
    """
    values = config.get("values", ["A", "B", "C"])
    weights = config.get("weights", None)

    if weights:
        # Normalize weights to sum to 1
        total = sum(weights)
        if total > 0:
            weights = [w / total for w in weights]
        else:
            weights = None

    result = np.random.choice(values, size=num_rows, p=weights)
    return pd.Series(result)
