"""
Data processing utilities for FinTrack AI.

Responsible for loading CSVs, normalizing columns, parsing dates/amounts,
and producing the Data Agent's structured output.
"""
from __future__ import annotations

import io
import re
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd


# Column synonyms for robust CSV ingestion
_DATE_ALIASES = {"date", "transaction_date", "txn_date", "posted_date", "posting_date", "time"}
_DESC_ALIASES = {
    "description", "desc", "memo", "details", "narrative",
    "transaction", "payee", "merchant", "name",
}
_AMOUNT_ALIASES = {
    "amount", "value", "total", "amt", "transaction_amount", "sum",
}

REQUIRED_LOGICAL_COLUMNS = ("date", "description", "amount")


def _normalize_colname(name: str) -> str:
    return re.sub(r"[\s\-]+", "_", str(name).strip().lower())


def _map_columns(df: pd.DataFrame) -> Dict[str, str]:
    """Return a mapping of original column -> logical name."""
    mapping: Dict[str, str] = {}
    for col in df.columns:
        norm = _normalize_colname(col)
        if norm in _DATE_ALIASES:
            mapping[col] = "date"
        elif norm in _DESC_ALIASES:
            mapping[col] = "description"
        elif norm in _AMOUNT_ALIASES:
            mapping[col] = "amount"
    return mapping


def _to_float(value: Any) -> Optional[float]:
    """Parse a messy amount string into a float (or None)."""
    if value is None:
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if pd.isna(value):
            return None
        return float(value)
    s = str(value).strip()
    if not s:
        return None
    negative = False
    if s.startswith("(") and s.endswith(")"):
        negative = True
        s = s[1:-1]
    s = s.replace("$", "").replace(",", "").replace(" ", "")
    if s.startswith("-"):
        negative = True
        s = s[1:]
    elif s.startswith("+"):
        s = s[1:]
    # strip trailing currency codes
    s = re.sub(r"[A-Za-z]+$", "", s)
    try:
        val = float(s)
    except ValueError:
        return None
    return -val if negative else val


def load_csv(source: Any) -> pd.DataFrame:
    """
    Load CSV from a path, file-like, or bytes. Raises ValueError on failure.
    """
    try:
        if isinstance(source, bytes):
            df = pd.read_csv(io.BytesIO(source))
        else:
            df = pd.read_csv(source)
    except Exception as exc:  # pragma: no cover - surface to UI
        raise ValueError(f"Could not read CSV: {exc}") from exc

    if df.empty:
        raise ValueError("CSV file is empty.")

    return df


def process_transactions(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Data Agent core routine.

    Returns a dict with:
      - df: cleaned DataFrame
      - quality: data-quality report
      - errors: list of issues encountered
    """
    errors: List[str] = []
    original_rows = len(df)

    col_map = _map_columns(df)
    df = df.rename(columns=col_map)

    missing = [c for c in REQUIRED_LOGICAL_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing required columns: {missing}. "
            f"Expected columns: date, description, amount."
        )

    df = df[list(REQUIRED_LOGICAL_COLUMNS)].copy()

    # --- Parse dates -----------------------------------------------------
    parsed_dates = pd.to_datetime(df["date"], errors="coerce", utc=False)
    bad_dates = parsed_dates.isna().sum()
    if bad_dates:
        errors.append(f"Dropped {bad_dates} row(s) with unparseable dates.")
    df["date"] = parsed_dates

    # --- Parse amounts ---------------------------------------------------
    df["amount"] = df["amount"].apply(_to_float)
    bad_amounts = df["amount"].isna().sum()
    if bad_amounts:
        errors.append(f"Dropped {bad_amounts} row(s) with invalid amounts.")

    # --- Clean descriptions ---------------------------------------------
    df["description"] = (
        df["description"].astype(str).str.strip().replace({"nan": ""})
    )
    empty_desc = (df["description"] == "").sum()

    # --- Drop invalid rows ----------------------------------------------
    df = df.dropna(subset=["date", "amount"]).reset_index(drop=True)

    # --- Income vs expense ---------------------------------------------
    df["type"] = np.where(df["amount"] >= 0, "income", "expense")
    df["abs_amount"] = df["amount"].abs()

    # --- Sort ------------------------------------------------------------
    df = df.sort_values("date").reset_index(drop=True)
    df["transaction_id"] = [f"TX{i+1:05d}" for i in range(len(df))]

    # --- Quality report --------------------------------------------------
    dropped = original_rows - len(df)
    quality = {
        "original_rows": int(original_rows),
        "clean_rows": int(len(df)),
        "dropped_rows": int(dropped),
        "missing_descriptions": int(empty_desc),
        "date_range": (
            f"{df['date'].min().date()} → {df['date'].max().date()}"
            if not df.empty else "n/a"
        ),
        "income_rows": int((df["type"] == "income").sum()),
        "expense_rows": int((df["type"] == "expense").sum()),
        "valid": not df.empty,
    }

    return {"df": df, "quality": quality, "errors": errors}


def summarize_quality(quality: Dict[str, Any]) -> str:
    parts = [
        f"{quality['clean_rows']} clean transactions",
        f"{quality['income_rows']} income / {quality['expense_rows']} expense",
    ]
    if quality["dropped_rows"]:
        parts.append(f"{quality['dropped_rows']} dropped")
    return " • ".join(parts)
