"""Boolean data generator."""

import numpy as np
import pandas as pd


BOOL_FORMATS = {
    "true_false": (True, False),
    "yes_no": ("Yes", "No"),
    "evet_hayir": ("Evet", "Hayır"),
    "1_0": (1, 0),
}


def generate_boolean(config: dict, num_rows: int) -> pd.Series:
    """Generate boolean data with configurable true ratio and output format.

    Config keys:
        true_ratio: probability of True (0.0 to 1.0)
        value_format: one of "true_false", "yes_no", "evet_hayir", "1_0"
    """
    true_ratio = config.get("true_ratio", 0.5)
    value_format = config.get("value_format", "true_false")
    true_val, false_val = BOOL_FORMATS.get(value_format, BOOL_FORMATS["true_false"])

    mask = np.random.random(num_rows) < true_ratio
    values = np.where(mask, true_val, false_val)
    return pd.Series(values)
