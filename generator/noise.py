"""Noise injection: nulls, outliers, duplicates, typos, whitespace, format inconsistencies."""

import random
import string

import numpy as np
import pandas as pd


def _inject_typos(value: str) -> str:
    if not isinstance(value, str) or len(value) == 0:
        return value
    op = random.choice(["swap", "replace", "drop", "insert"])
    i = random.randrange(len(value))
    if op == "swap" and len(value) > 1:
        j = min(i + 1, len(value) - 1)
        chars = list(value)
        chars[i], chars[j] = chars[j], chars[i]
        return "".join(chars)
    if op == "replace":
        return value[:i] + random.choice(string.ascii_letters) + value[i + 1:]
    if op == "drop":
        return value[:i] + value[i + 1:]
    # insert
    return value[:i] + random.choice(string.ascii_letters) + value[i:]


def _inject_whitespace(value: str) -> str:
    if not isinstance(value, str):
        return value
    op = random.choice(["lead", "trail", "double", "lead_trail"])
    if op == "lead":
        return " " + value
    if op == "trail":
        return value + " "
    if op == "double" and " " in value:
        i = value.find(" ")
        return value[: i + 1] + " " + value[i + 1:]
    return " " + value + " "


def _inject_format_inconsistency(value):
    if isinstance(value, str):
        choice = random.choice(["upper", "lower", "title"])
        if choice == "upper":
            return value.upper()
        if choice == "lower":
            return value.lower()
        return value.title()
    return value


def inject_noise(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """Inject noise into generated DataFrame.

    Config keys (all 0.0 disables the effect):
        null_ratio: fraction of cells to NaN
        outlier_ratio: fraction of numeric cells replaced with outliers
        outlier_scale: multiplier for outlier distance (default 3.0)
        duplicate_ratio: fraction of rows duplicated
        typo_ratio: fraction of string cells with typographical noise
        whitespace_ratio: fraction of string cells with whitespace noise
        format_inconsistency_ratio: fraction of string cells with case inconsistency
    """
    df = df.copy()
    null_ratio = config.get("null_ratio", 0.0)
    outlier_ratio = config.get("outlier_ratio", 0.0)
    outlier_scale = config.get("outlier_scale", 3.0)
    duplicate_ratio = config.get("duplicate_ratio", 0.0)
    typo_ratio = config.get("typo_ratio", 0.0)
    whitespace_ratio = config.get("whitespace_ratio", 0.0)
    format_ratio = config.get("format_inconsistency_ratio", 0.0)

    n_rows, n_cols = df.shape

    if null_ratio > 0:
        null_mask = np.random.random((n_rows, n_cols)) < null_ratio
        for i, col in enumerate(df.columns):
            df.loc[null_mask[:, i], col] = np.nan

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
            signs = np.random.choice([-1, 1], size=n_outliers)
            outlier_values = mean + signs * outlier_scale * std
            df.loc[indices, col] = outlier_values

    string_cols = [c for c in df.columns if df[c].dtype == object]

    def _apply(col: str, ratio: float, fn):
        n = int(n_rows * ratio)
        if n == 0:
            return
        indices = np.random.choice(n_rows, size=n, replace=False)
        df.loc[indices, col] = df.loc[indices, col].apply(fn)

    for col in string_cols:
        if typo_ratio > 0:
            _apply(col, typo_ratio, _inject_typos)
        if whitespace_ratio > 0:
            _apply(col, whitespace_ratio, _inject_whitespace)
        if format_ratio > 0:
            _apply(col, format_ratio, _inject_format_inconsistency)

    if duplicate_ratio > 0:
        n_dup = int(n_rows * duplicate_ratio)
        if n_dup > 0:
            src_indices = np.random.choice(n_rows, size=n_dup, replace=True)
            dup_rows = df.iloc[src_indices].copy()
            df = pd.concat([df, dup_rows], ignore_index=True).sample(frac=1).reset_index(drop=True)

    return df
