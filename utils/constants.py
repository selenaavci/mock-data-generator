"""Constants for Mock Data Generator."""

import re

# Internal type identifiers used by the engine
TYPE_OPTIONS = [
    "numeric_int",
    "numeric_float",
    "categorical",
    "datetime",
    "boolean",
    "text",
    "faker",
    "id",
    "pattern",
]

# User-facing types for the "Design from Scratch" wizard.
# Each entry maps a friendly label -> (internal_type, optional faker_provider).
USER_TYPES = {
    "Tam Sayı (Integer)": ("numeric_int", None),
    "Ondalık (Decimal)": ("numeric_float", None),
    "Metin (Text)": ("text", None),
    "Kategorik": ("categorical", None),
    "Doğru / Yanlış (Boolean)": ("boolean", None),
    "Tarih / Saat": ("datetime", None),
    "ID": ("id", None),
    "E-posta": ("faker", "email"),
    "Telefon": ("faker", "phone_number"),
    "İsim": ("faker", "name"),
    "Ad": ("faker", "first_name"),
    "Soyad": ("faker", "last_name"),
    "Şirket": ("faker", "company"),
    "Ülke": ("faker", "country"),
    "Şehir": ("faker", "city"),
    "Adres": ("faker", "address"),
    "Özel Desen (Pattern)": ("pattern", None),
}

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

DEFAULT_LOCALE = "en_US"

LOCALE_OPTIONS = {
    "İngilizce": "en_US",
    "Türkçe": "tr_TR",
    "Almanca": "de_DE",
    "Fransızca": "fr_FR",
    "İspanyolca": "es_ES",
}

# Date output format presets
DATE_FORMAT_OPTIONS = {
    "YYYY-MM-DD": "%Y-%m-%d",
    "DD/MM/YYYY": "%d/%m/%Y",
    "MM/DD/YYYY": "%m/%d/%Y",
    "DD.MM.YYYY": "%d.%m.%Y",
    "YYYY-MM-DD HH:MM:SS": "%Y-%m-%d %H:%M:%S",
    "Ham (datetime)": None,
}

# Boolean output formats
BOOLEAN_FORMAT_OPTIONS = {
    "True / False": "true_false",
    "Yes / No": "yes_no",
    "Evet / Hayır": "evet_hayir",
    "1 / 0": "1_0",
}

MAX_ROWS = 1_000_000
WARN_ROWS = 500_000
