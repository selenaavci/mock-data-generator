"""I/O helper functions for reading uploads and exporting data."""

from io import BytesIO

import pandas as pd


def read_upload(uploaded_file) -> pd.DataFrame:
    """Read an uploaded file (CSV or Excel) into a DataFrame."""
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    elif name.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file, engine="openpyxl")
    else:
        raise ValueError(f"Unsupported file format: {name}")


def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="MockData")
    return buffer.getvalue()


def df_to_json_bytes(df: pd.DataFrame) -> bytes:
    """Export DataFrame to pretty-printed JSON records."""
    return df.to_json(orient="records", force_ascii=False, indent=2, date_format="iso").encode("utf-8")
