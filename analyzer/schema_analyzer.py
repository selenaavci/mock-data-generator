"""Schema analyzer: detects column types, distributions, and generation configs from uploaded data."""

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd

from utils.constants import FAKER_COLUMN_PATTERNS


@dataclass
class ColumnProfile:
    """Profile of a single column describing its type and generation parameters."""

    name: str
    detected_type: str  # numeric_int, numeric_float, categorical, datetime, boolean, faker, text
    nullable: bool = False
    null_ratio: float = 0.0
    stats: dict = field(default_factory=dict)
    faker_hint: str | None = None
    generation_config: dict = field(default_factory=dict)


def _detect_faker_hint(column_name: str) -> str | None:
    """Try to match column name against known Faker provider patterns."""
    for pattern, provider in FAKER_COLUMN_PATTERNS:
        if pattern.search(column_name):
            return provider
    return None


def _is_boolean(series: pd.Series) -> bool:
    """Check if a series represents boolean values."""
    unique = set(series.dropna().unique())
    if len(unique) > 2:
        return False
    bool_sets = [
        {True, False},
        {0, 1},
        {"true", "false"},
        {"yes", "no"},
        {"evet", "hayir"},
        {"evet", "hayır"},
        {1.0, 0.0},
    ]
    lower_unique = set()
    for v in unique:
        if isinstance(v, str):
            lower_unique.add(v.lower().strip())
        else:
            lower_unique.add(v)

    return any(lower_unique == bs or lower_unique.issubset(bs) for bs in bool_sets)


def _is_datetime(series: pd.Series) -> bool:
    """Check if a series can be parsed as datetime."""
    if pd.api.types.is_datetime64_any_dtype(series):
        return True
    if series.dtype == object:
        try:
            sample = series.dropna().head(50)
            if len(sample) == 0:
                return False
            pd.to_datetime(sample, format="mixed")
            return True
        except (ValueError, TypeError):
            return False
    return False


def _analyze_numeric(series: pd.Series, is_int: bool) -> dict:
    """Compute stats for numeric column."""
    clean = series.dropna()
    stats = {
        "min": float(clean.min()),
        "max": float(clean.max()),
        "mean": float(clean.mean()),
        "std": float(clean.std()) if len(clean) > 1 else 0.0,
        "median": float(clean.median()),
    }
    config = {
        "distribution": "normal",
        "min": stats["min"],
        "max": stats["max"],
        "mean": stats["mean"],
        "std": stats["std"],
        "is_int": is_int,
    }
    return stats, config


def _analyze_categorical(series: pd.Series) -> dict:
    """Compute value counts and weights for categorical column."""
    clean = series.dropna()
    value_counts = clean.value_counts()
    total = len(clean)
    values = value_counts.index.tolist()
    weights = (value_counts.values / total).tolist()
    stats = {
        "unique_count": len(values),
        "values": values[:100],  # cap at 100 for UI
        "weights": weights[:100],
    }
    config = {
        "values": values[:100],
        "weights": weights[:100],
    }
    return stats, config


def _analyze_datetime(series: pd.Series) -> dict:
    """Compute date range for datetime column."""
    clean = pd.to_datetime(series.dropna())
    stats = {
        "min": str(clean.min()),
        "max": str(clean.max()),
    }
    config = {
        "start_date": str(clean.min().date()),
        "end_date": str(clean.max().date()),
        "sequential": False,
    }
    return stats, config


def _analyze_boolean(series: pd.Series) -> dict:
    """Compute true ratio for boolean column."""
    clean = series.dropna()
    # Normalize to True/False
    true_values = {True, 1, 1.0, "true", "yes", "evet"}
    true_count = sum(
        1 for v in clean
        if (v if not isinstance(v, str) else v.lower().strip()) in true_values
    )
    true_ratio = true_count / len(clean) if len(clean) > 0 else 0.5
    stats = {"true_ratio": true_ratio}
    config = {"true_ratio": true_ratio}
    return stats, config


def analyze(df: pd.DataFrame) -> list[ColumnProfile]:
    """Analyze a DataFrame and return a ColumnProfile for each column."""
    profiles = []

    for col in df.columns:
        series = df[col]
        null_count = series.isna().sum()
        total = len(series)
        nullable = null_count > 0
        null_ratio = null_count / total if total > 0 else 0.0

        profile = ColumnProfile(
            name=col,
            detected_type="text",
            nullable=nullable,
            null_ratio=round(null_ratio, 4),
        )

        # Detection order: boolean -> datetime -> numeric -> faker -> categorical -> text

        if _is_boolean(series):
            profile.detected_type = "boolean"
            stats, config = _analyze_boolean(series)
            profile.stats = stats
            profile.generation_config = config

        elif _is_datetime(series):
            profile.detected_type = "datetime"
            stats, config = _analyze_datetime(series)
            profile.stats = stats
            profile.generation_config = config

        elif pd.api.types.is_numeric_dtype(series):
            is_int = pd.api.types.is_integer_dtype(series)
            if not is_int:
                # Check if all non-null values are whole numbers
                clean = series.dropna()
                if len(clean) > 0 and (clean == clean.astype(int)).all():
                    is_int = True
            profile.detected_type = "numeric_int" if is_int else "numeric_float"
            stats, config = _analyze_numeric(series, is_int)
            profile.stats = stats
            profile.generation_config = config

        else:
            # Text-based column: check for faker hint first
            faker_hint = _detect_faker_hint(col)
            if faker_hint:
                profile.detected_type = "faker"
                profile.faker_hint = faker_hint
                profile.stats = {"faker_provider": faker_hint}
                profile.generation_config = {"faker_provider": faker_hint}
            else:
                # Check if categorical (low unique ratio)
                clean = series.dropna()
                if len(clean) > 0:
                    unique_ratio = clean.nunique() / len(clean)
                    if unique_ratio < 0.5 or clean.nunique() <= 20:
                        profile.detected_type = "categorical"
                        stats, config = _analyze_categorical(series)
                        profile.stats = stats
                        profile.generation_config = config
                    else:
                        profile.detected_type = "text"
                        profile.stats = {
                            "unique_count": clean.nunique(),
                            "avg_length": clean.astype(str).str.len().mean(),
                        }
                        profile.generation_config = {
                            "avg_length": int(clean.astype(str).str.len().mean()),
                        }

        profiles.append(profile)

    return profiles
