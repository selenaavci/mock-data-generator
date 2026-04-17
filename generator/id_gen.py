"""ID column generator."""

import random
import string

import numpy as np
import pandas as pd


def generate_id(config: dict, num_rows: int) -> pd.Series:
    """Generate ID values with prefix, fixed length, sequential or random mode.

    Config keys:
        prefix: string prefix (default "")
        start: starting number for sequential mode (default 1)
        length: total digit length for the numeric part (zero-padded)
        sequential: if True, generate a sequence; else random unique IDs
        unique: enforce uniqueness for random mode (default True)
    """
    prefix = str(config.get("prefix", ""))
    start = int(config.get("start", 1))
    length = int(config.get("length", 6))
    sequential = bool(config.get("sequential", True))
    unique = bool(config.get("unique", True))

    if sequential:
        numbers = np.arange(start, start + num_rows)
    else:
        upper = 10 ** length - 1
        if unique and num_rows <= upper:
            numbers = np.random.choice(upper + 1, size=num_rows, replace=False)
        else:
            numbers = np.random.randint(0, upper + 1, size=num_rows)

    formatted = [f"{prefix}{int(n):0{length}d}" for n in numbers]
    return pd.Series(formatted)
