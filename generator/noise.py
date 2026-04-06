"""Noise injection: null values and outliers."""

import numpy as np
import pandas as pd


def inject_noise(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Inject noise into generated DataFrame.

    Config keys:
        null_ratio: fraction of cells to set as NaN (0.0 to 0.3)
        outlier_ratio: fraction of numeric values to replace with outliers (0.0 to 0.1)
        outlier_scale: multiplier for outlier distance from mean (default 3.0)
    """
    df = df.copy()
    null_ratio = config.get("null_ratio", 0.0)
    outlier_ratio = config.get("outlier_ratio", 0.0)
    outlier_scale = config.get("outlier_scale", 3.0)

    n_rows, n_cols = df.shape

    # Inject nulls
    if null_ratio > 0:
        null_mask = np.random.random((n_rows, n_cols)) < null_ratio
        for i, col in enumerate(df.columns):
            df.loc[null_mask[:, i], col] = np.nan

    # Inject outliers in numeric columns
    if outlier_ratio > 0:
        for col in df.select_dtypes(include=[np.number]).columns:
            n_outliers = int(n_rows * outlier_ratio)
            if n_outliers == 0:
                continue
            indices = np.random.choice(n_rows, size=n_outliers, replace=False)
            mean = df[col].mean()
            std = df[col].std()
            if pd.isna(std) or std == 0:
                std = 1.0
            # Random sign for outliers
            signs = np.random.choice([-1, 1], size=n_outliers)
            outlier_values = mean + signs * outlier_scale * std
            df.loc[indices, col] = outlier_values

    return df
