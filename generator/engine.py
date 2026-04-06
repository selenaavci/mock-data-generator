"""Generation engine: orchestrates all sub-generators."""

import pandas as pd

from analyzer.schema_analyzer import ColumnProfile
from generator.numeric import generate_numeric
from generator.categorical import generate_categorical
from generator.datetime_gen import generate_datetime
from generator.boolean_gen import generate_boolean
from generator.text import generate_faker, generate_text
from generator.correlations import apply_correlations
from generator.noise import inject_noise


def _generate_column(profile: ColumnProfile, num_rows: int, locale: str) -> pd.Series:
    """Generate a single column based on its profile."""
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
    """Generate a complete mock DataFrame.

    Args:
        profiles: List of ColumnProfile objects describing each column.
        num_rows: Number of rows to generate.
        locale: Faker locale string.
        noise_config: Optional noise injection config.
        correlation_rules: Optional list of correlation rule dicts.
        business_rules: Optional list of pandas query strings.

    Returns:
        Generated DataFrame.
    """
    # If business rules exist, over-generate to allow filtering
    generate_rows = num_rows
    if business_rules:
        generate_rows = int(num_rows * 1.5)

    # Generate each column
    data = {}
    for profile in profiles:
        data[profile.name] = _generate_column(profile, generate_rows, locale)

    df = pd.DataFrame(data)

    # Apply correlations
    if correlation_rules:
        df = apply_correlations(df, correlation_rules)

    # Apply business rules (filter)
    if business_rules:
        for _ in range(3):  # max 3 retry iterations
            for rule in business_rules:
                try:
                    df = df.query(rule)
                except Exception:
                    pass  # skip invalid rules

            if len(df) >= num_rows:
                break

            # Need more rows - generate additional batch
            extra = {}
            for profile in profiles:
                extra[profile.name] = _generate_column(profile, num_rows, locale)
            extra_df = pd.DataFrame(extra)
            if correlation_rules:
                extra_df = apply_correlations(extra_df, correlation_rules)
            df = pd.concat([df, extra_df], ignore_index=True)

    # Truncate to exact row count
    df = df.head(num_rows).reset_index(drop=True)

    # Apply noise (after rules, so noise doesn't break constraints)
    if noise_config and (noise_config.get("null_ratio", 0) > 0 or noise_config.get("outlier_ratio", 0) > 0):
        df = inject_noise(df, noise_config)

    return df
