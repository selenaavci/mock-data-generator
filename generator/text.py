"""Text and Faker-based data generator."""

import pandas as pd
from faker import Faker


def generate_faker(config: dict, num_rows: int, locale: str = "en_US") -> pd.Series:
    """Generate realistic text data using Faker.

    Config keys:
        faker_provider: Faker method name (e.g., "name", "email", "city")
    """
    fake = Faker(locale)
    provider = config.get("faker_provider", "name")

    generator = getattr(fake, provider, None)
    if generator is None:
        generator = fake.name

    values = [generator() for _ in range(num_rows)]
    return pd.Series(values)


def generate_text(config: dict, num_rows: int, locale: str = "en_US") -> pd.Series:
    """Generate random text strings.

    Config keys:
        avg_length: target average character length
    """
    fake = Faker(locale)
    avg_len = config.get("avg_length", 20)

    if avg_len <= 10:
        values = [fake.word() for _ in range(num_rows)]
    elif avg_len <= 50:
        values = [fake.sentence(nb_words=max(1, avg_len // 5)) for _ in range(num_rows)]
    else:
        values = [fake.text(max_nb_chars=max(10, avg_len)) for _ in range(num_rows)]

    return pd.Series(values)
