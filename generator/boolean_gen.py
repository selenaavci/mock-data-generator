"""Boolean data generator."""

import numpy as np
import pandas as pd


def generate_boolean(config: dict, num_rows: int) -> pd.Series:
    """Generate boolean data with configurable true ratio.

    Config keys:
        true_ratio: probability of True (0.0 to 1.0)
    """
    true_ratio = config.get("true_ratio", 0.5)
    values = np.random.random(num_rows) < true_ratio
    return pd.Series(values)
