"""Basic correlation between columns using rank-based approach."""

import numpy as np
import pandas as pd


def apply_correlations(df: pd.DataFrame, rules: list[dict]) -> pd.DataFrame:
    """Apply correlation rules between columns.

    Each rule is a dict:
        source: source column name
        target: target column name
        direction: "positive" or "negative"
        strength: 0.0 (no correlation) to 1.0 (perfect correlation)
    """
    df = df.copy()

    for rule in rules:
        source = rule.get("source")
        target = rule.get("target")
        direction = rule.get("direction", "positive")
        strength = rule.get("strength", 0.5)

        if source not in df.columns or target not in df.columns:
            continue
        if not pd.api.types.is_numeric_dtype(df[source]) or not pd.api.types.is_numeric_dtype(df[target]):
            continue

        n = len(df)
        if n < 2:
            continue

        # Get source ranks
        source_ranks = df[source].rank(method="first").values

        if direction == "negative":
            source_ranks = n + 1 - source_ranks

        # Sort target values
        target_sorted = np.sort(df[target].values)

        # Create correlated order: map source rank to target value
        rank_order = np.argsort(source_ranks)
        correlated_target = np.empty(n)
        correlated_target[rank_order] = target_sorted

        # Blend original random values with correlated values
        original_target = df[target].values
        blended = strength * correlated_target + (1 - strength) * original_target
        df[target] = blended

    return df
