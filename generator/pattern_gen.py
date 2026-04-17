"""Custom pattern-based string generator.

Pattern tokens:
    #   digit 0-9
    @   uppercase letter A-Z
    &   lowercase letter a-z
    ?   any letter (mixed case)
    *   alphanumeric
    \\x literal next character

Example: "ABC-####-@@" -> "ABC-4821-QK"
"""

import random
import string

import pandas as pd


def _generate_one(pattern: str) -> str:
    out = []
    i = 0
    while i < len(pattern):
        c = pattern[i]
        if c == "\\" and i + 1 < len(pattern):
            out.append(pattern[i + 1])
            i += 2
            continue
        if c == "#":
            out.append(random.choice(string.digits))
        elif c == "@":
            out.append(random.choice(string.ascii_uppercase))
        elif c == "&":
            out.append(random.choice(string.ascii_lowercase))
        elif c == "?":
            out.append(random.choice(string.ascii_letters))
        elif c == "*":
            out.append(random.choice(string.ascii_letters + string.digits))
        else:
            out.append(c)
        i += 1
    return "".join(out)


def generate_pattern(config: dict, num_rows: int) -> pd.Series:
    """Generate strings from a token pattern.

    Config keys:
        pattern: token string (see module docstring)
    """
    pattern = config.get("pattern", "####-@@@@")
    values = [_generate_one(pattern) for _ in range(num_rows)]
    return pd.Series(values)
