"""Generation engine: orchestrates all sub-generators."""

import pandas as pd

from analyzer.schema_analyzer import ColumnProfile
from generator.numeric import generate_numeric
from generator.categorical import generate_categorical
from generator.datetime_gen import generate_datetime
from generator.boolean_gen import generate_boolean
from generator.text import generate_faker, generate_text
from generator.id_gen import generate_id
from generator.pattern_gen import generate_pattern
from generator.correlations import apply_correlations
from generator.noise import inject_noise


def _generate_column(profile: ColumnProfile, num_rows: int, locale: str) -> pd.Series:
    config = profile.generation_config
    dtype = profile.detected_type

    if dtype in ("numeric_int", "numeric_float"):
        return generate_numeric(config, num_rows)
    elif dtype == "categorical":
        return generate_categorical(config, num_rows)
    elif dtype == "datetime":
        return generate_datetime(config, num_rows)
    elif dtype == "boolean":
        return generate_boolean(config, num_rows)
    elif dtype == "faker":
        return generate_faker(config, num_rows, locale)
    elif dtype == "id":
        return generate_id(config, num_rows)
    elif dtype == "pattern":
        return generate_pattern(config, num_rows)
    else:  # text
        return generate_text(config, num_rows, locale)


def generate(
    profiles: list[ColumnProfile],
    num_rows: int,
    locale: str = "en_US",
    noise_config: dict | None = None,
    correlation_rules: list[dict] | None = None,
    business_rules: list[str] | None = None,
) -> pd.DataFrame:
    """Generate a complete mock DataFrame."""
    generate_rows = num_rows
    if business_rules:
        generate_rows = int(num_rows * 1.5)

    data = {}
    for profile in profiles:
        data[profile.name] = _generate_column(profile, generate_rows, locale)

    df = pd.DataFrame(data)

    if correlation_rules:
        df = apply_correlations(df, correlation_rules)

    if business_rules:
        for _ in range(3):
            for rule in business_rules:
                try:
                    df = df.query(rule)
                except Exception:
                    pass

            if len(df) >= num_rows:
                break

            extra = {}
            for profile in profiles:
                extra[profile.name] = _generate_column(profile, num_rows, locale)
            extra_df = pd.DataFrame(extra)
            if correlation_rules:
                extra_df = apply_correlations(extra_df, correlation_rules)
            df = pd.concat([df, extra_df], ignore_index=True)

    df = df.head(num_rows).reset_index(drop=True)

    # Enforce per-column uniqueness where configured
    for profile in profiles:
        if profile.generation_config.get("unique"):
            df = _enforce_unique(df, profile, num_rows, locale)

    if noise_config and any(noise_config.get(k, 0) > 0 for k in (
        "null_ratio", "outlier_ratio", "duplicate_ratio",
        "typo_ratio", "whitespace_ratio", "format_inconsistency_ratio",
    )):
        df = inject_noise(df, noise_config)

    return df


def _enforce_unique(df: pd.DataFrame, profile: ColumnProfile, num_rows: int, locale: str) -> pd.DataFrame:
    """Replace duplicate values in a column by regenerating extras."""
    col = profile.name
    if col not in df.columns:
        return df
    seen_mask = df[col].duplicated(keep="first")
    tries = 0
    while seen_mask.any() and tries < 5:
        needed = int(seen_mask.sum())
        extra = _generate_column(profile, needed * 3, locale).tolist()
        existing = set(df.loc[~seen_mask, col].tolist())
        replacement = []
        for v in extra:
            if v not in existing:
                replacement.append(v)
                existing.add(v)
                if len(replacement) == needed:
                    break
        if not replacement:
            break
        idxs = df.index[seen_mask][: len(replacement)]
        df.loc[idxs, col] = replacement
        seen_mask = df[col].duplicated(keep="first")
        tries += 1
    return df
