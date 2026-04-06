"""Constants for Mock Data Generator."""

import re

# Column type options
TYPE_OPTIONS = [
    "numeric_int",
    "numeric_float",
    "categorical",
    "datetime",
    "boolean",
    "text",
    "faker",
]

# Faker provider options available in UI
FAKER_PROVIDERS = [
    None,
    "name",
    "first_name",
    "last_name",
    "email",
    "phone_number",
    "city",
    "address",
    "country",
    "company",
    "job",
    "text",
    "sentence",
    "word",
    "iban",
    "credit_card_number",
    "ssn",
    "license_plate",
    "url",
    "user_name",
    "zipcode",
]

# Regex patterns to auto-detect Faker providers from column names
FAKER_COLUMN_PATTERNS = [
    (re.compile(r"(?i)^(e[-_]?mail|eposta)"), "email"),
    (re.compile(r"(?i)(first[-_]?name|ad[iı]|isim)"), "first_name"),
    (re.compile(r"(?i)(last[-_]?name|soyad|soyisim)"), "last_name"),
    (re.compile(r"(?i)(full[-_]?name|name|isim|ad[-_]?soyad)"), "name"),
    (re.compile(r"(?i)(phone|tel|telefon|gsm|mobile|cep)"), "phone_number"),
    (re.compile(r"(?i)(city|sehir|[sş]ehir|il\b)"), "city"),
    (re.compile(r"(?i)(address|adres)"), "address"),
    (re.compile(r"(?i)(country|[uü]lke|ulke)"), "country"),
    (re.compile(r"(?i)(company|firma|[sş]irket|sirket)"), "company"),
    (re.compile(r"(?i)(job|title|meslek|[gG][oö]rev|pozisyon|unvan)"), "job"),
    (re.compile(r"(?i)(iban)"), "iban"),
    (re.compile(r"(?i)(credit[-_]?card|kredi[-_]?kart)"), "credit_card_number"),
    (re.compile(r"(?i)(ssn|tc[-_]?kimlik|kimlik[-_]?no)"), "ssn"),
    (re.compile(r"(?i)(plate|plaka)"), "license_plate"),
    (re.compile(r"(?i)(url|website|web[-_]?site)"), "url"),
    (re.compile(r"(?i)(user[-_]?name|kullan[iı]c[iı])"), "user_name"),
    (re.compile(r"(?i)(zip|posta[-_]?kodu|zipcode|postal)"), "zipcode"),
]

# Default locale
DEFAULT_LOCALE = "en_US"

# Supported locales
LOCALE_OPTIONS = {
    "English": "en_US",
    "Turkish": "tr_TR",
    "German": "de_DE",
    "French": "fr_FR",
    "Spanish": "es_ES",
}

# Max rows
MAX_ROWS = 1_000_000
WARN_ROWS = 500_000
