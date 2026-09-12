"""
Data processing utilities for FinTrack AI.

Robust dynamic loader:
- Auto-detects separator (comma, semicolon, pipe, tab)
- Auto-detects columns: date, description, amount OR debit/credit OR amount+type
- Handles currency symbols, parentheses negatives, ISO codes, decimal commas
"""
from __future__ import annotations

import io
import re
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------
# Column-name normalization & aliases
# ---------------------------------------------------------------------
_DATE_ALIASES = {
    "date", "transactiondate", "txndate", "posteddate", "postingdate",
    "valuedate", "time", "datetime", "createdat", "created", "day",
}
_DESC_ALIASES = {
    "description", "desc", "memo", "details", "detail", "narrative",
    "transaction", "payee", "merchant", "name", "vendor", "counterparty",
    "reference", "narration", "particulars", "note", "notes", "label",
}
_AMOUNT_ALIASES = {
    "amount", "value", "total", "amt", "transactionamount", "sum",
    "net", "netamount", "gross", "grossamount", "money",
}
_DEBIT_ALIASES = {
    "debit", "withdrawal", "withdrawals", "paid", "moneyout",
    "outflow", "debitamount",
}
_CREDIT_ALIASES = {
    "credit", "deposit", "deposits", "received", "moneyin",
    "inflow", "creditamount",
}
_TYPE_ALIASES = {
    "type", "transactiontype", "txtype", "direction", "kind",
    "amounttype", "drcr",
}

REQUIRED_LOGICAL_COLUMNS = ("date", "amount")


def _normalize_colname(name: str) -> str:
    s = str(name).replace("\ufeff", "").strip().lower()
    s = re.sub(r"[\s\-_./\\()\[\]{}$#%]+", "", s)
    s = re.sub(r"[^a-z0-9]", "", s)
    return s


def _classify_column(raw_name: str) -> Optional[str]:
    norm = _normalize_colname(raw_name)
    if not norm:
        return None
    if norm in _DATE_ALIASES:
        return "date"
    if norm in _DESC_ALIASES:
        return "description"
    if norm in _AMOUNT_ALIASES:
        return "amount"
    if norm in _DEBIT_ALIASES:
        return "debit"
    if norm in _CREDIT_ALIASES:
        return "credit"
    if norm in _TYPE_ALIASES:
        return "type"
    if "date" in norm and norm not in {"updatedate", "duedate"}:
        return "date"
    if any(k in norm for k in ("desc", "memo", "payee", "merchant", "narrat", "particular")):
        return "description"
    if "amount" in norm or norm.endswith("amt"):
        return "amount"
    if norm.startswith("debit") or norm.startswith("withdraw"):
        return "debit"
    if norm.startswith("credit") or norm.startswith("deposit"):
        return "credit"
    if norm in {"dr", "drcr"}:
        return "type"
    return None


def _build_column_map(columns: List[str]) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for col in columns:
        role = _classify_column(col)
        if role and role not in result:
            result[role] = col
    amount_candidates = [c for c in columns if _normalize_colname(c) in _AMOUNT_ALIASES]
    if amount_candidates:
        result["amount"] = amount_candidates[0]
    return result


# ---------------------------------------------------------------------
# Numeric / date parsing
# ---------------------------------------------------------------------
_NUM_RE = re.compile(r"-?\d{1,3}(?:[,\s]\d{3})*(?:\.\d+)?|-?\d+(?:\.\d+)?")


def _to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float, np.integer, np.floating)) and not isinstance(value, bool):
        try:
            f = float(value)
            return None if np.isnan(f) else f
        except (TypeError, ValueError):
            return None

    s = str(value).strip()
    if not s or s.lower() in {"nan", "none", "null", "-", "--", "n/a", "na"}:
        return None

    negative = False
    if s.startswith("(") and s.endswith(")"):
        negative = True
        s = s[1:-1]

    s = re.sub(r"[A-Za-z$€£¥₹]", "", s)
    s = s.replace(" ", "")

    # European decimal: convert "1.234,56" style
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s and "." not in s:
        # If comma appears as decimal (e.g. "18400,50")
        parts = s.split(",")
        if len(parts) == 2 and len(parts[1]) <= 2:
            s = s.replace(",", ".")
        else:
            s = s.replace(",", "")

    if s.endswith("-"):
        negative = True
        s = s[:-1]

    m = _NUM_RE.search(s)
    if not m:
        return None
    num_str = m.group(0).replace(",", "").replace(" ", "")
    try:
        val = float(num_str)
    except ValueError:
        return None

    if num_str.startswith("-"):
        return val
    return -abs(val) if negative else val


def _parse_date_series(series: pd.Series) -> pd.Series:
    out = pd.to_datetime(series, errors="coerce", utc=False)
    if out.isna().mean() > 0.5:
        for fmt in (
            "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%m-%d-%Y",
            "%Y/%m/%d", "%Y.%m.%d", "%d.%m.%Y", "%b %d, %Y", "%d %b %Y",
            "%d/%m/%y", "%m/%d/%y",
        ):
            try:
                alt = pd.to_datetime(series, errors="coerce", format=fmt)
                if alt.notna().mean() > out.notna().mean():
                    out = alt
            except Exception:
                continue
    return out


# ---------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------
def load_csv(source: Any, filename: str = "") -> pd.DataFrame:
    """
    Load CSV / TSV / TXT / XLSX.
    Auto-detects separator when possible.
    """
    name = (filename or "").lower()

    is_xlsx_ext = name.endswith((".xlsx", ".xls"))
    is_xlsx_bytes = (
        isinstance(source, (bytes, bytearray))
        and len(source) >= 2
        and source[:2] == b"PK"
    )
    if is_xlsx_ext or is_xlsx_bytes:
        try:
            if isinstance(source, (bytes, bytearray)):
                return pd.read_excel(io.BytesIO(source))
            return pd.read_excel(source)
        except Exception as exc:
            raise ValueError(f"Could not read Excel file: {exc}") from exc

    def _try_read(**kwargs) -> Optional[pd.DataFrame]:
        try:
            if isinstance(source, (bytes, bytearray)):
                return pd.read_csv(io.BytesIO(source), **kwargs)
            return pd.read_csv(source, **kwargs)
        except Exception:
            return None

    candidates: List[pd.DataFrame] = []

    auto = _try_read(sep=None, engine="python")
    if auto is not None and auto.shape[1] > 1:
        candidates.append(auto)

    for sep in (",", ";", "\t", "|"):
        df = _try_read(sep=sep)
        if df is not None and df.shape[1] > 1:
            candidates.append(df)

    if not candidates:
        df = _try_read()
        if df is not None:
            candidates.append(df)

    if not candidates:
        raise ValueError(
            "Could not read file — no valid CSV/TSV structure detected."
        )

    best = max(candidates, key=lambda d: d.shape[1])

    if best.empty:
        raise ValueError("File is empty.")
    return best


def process_transactions(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Data Agent core routine. Adapts to many column layouts.
    """
    errors: List[str] = []
    original_rows = len(df)
    original_cols = list(df.columns)

    df = df.rename(columns={c: str(c).replace("\ufeff", "").strip() for c in df.columns})

    col_map = _build_column_map(list(df.columns))

    if "date" not in col_map:
        raise ValueError(
            f"Could not find a date column. "
            f"Detected columns: {original_cols}. "
            f"Expected something like 'date', 'transaction_date', 'txn_date'."
        )

    has_amount = "amount" in col_map
    has_debit_credit = "debit" in col_map or "credit" in col_map

    if not has_amount and not has_debit_credit:
        raise ValueError(
            f"Could not find an amount column (or debit/credit columns). "
            f"Detected columns: {original_cols}. "
            f"Expected something like 'amount', 'value', 'total', or 'debit'/'credit'."
        )

    work = pd.DataFrame()
    work["date_raw"] = df[col_map["date"]]

    if "description" in col_map:
        work["description"] = df[col_map["description"]].astype(str).str.strip()
    else:
        work["description"] = ""
        errors.append("No description column found — defaulted to empty strings.")

    if has_amount:
        work["amount"] = df[col_map["amount"]].apply(_to_float)
        if "type" in col_map:
            t = df[col_map["type"]].astype(str).str.lower()
            debit_like = t.str.contains("debit|dr|expense|withdraw|payment|out", regex=True, na=False)
            credit_like = t.str.contains("credit|cr|income|deposit|received|in", regex=True, na=False)
            work.loc[debit_like, "amount"] = -work.loc[debit_like, "amount"].abs()
            work.loc[credit_like, "amount"] = work.loc[credit_like, "amount"].abs()
    else:
        debit = (
            df[col_map["debit"]].apply(_to_float).fillna(0.0).abs()
            if "debit" in col_map else pd.Series([0.0] * len(df))
        )
        credit = (
            df[col_map["credit"]].apply(_to_float).fillna(0.0).abs()
            if "credit" in col_map else pd.Series([0.0] * len(df))
        )
        work["amount"] = credit - debit
        errors.append(
            f"Used debit/credit columns: '{col_map.get('debit','—')}' / "
            f"'{col_map.get('credit','—')}'."
        )

    parsed_dates = _parse_date_series(work["date_raw"])
    bad_dates = int(parsed_dates.isna().sum())
    if bad_dates:
        errors.append(f"Dropped {bad_dates} row(s) with unparseable dates.")
    work["date"] = parsed_dates

    bad_amounts = int(work["amount"].isna().sum())
    if bad_amounts:
        errors.append(f"Dropped {bad_amounts} row(s) with invalid amounts.")

    empty_desc = int((work["description"] == "").sum())

    clean = work.dropna(subset=["date", "amount"]).reset_index(drop=True)
    clean["description"] = clean["description"].fillna("").astype(str)
    clean["type"] = np.where(clean["amount"] >= 0, "income", "expense")
    clean["abs_amount"] = clean["amount"].abs()

    clean = clean.sort_values("date").reset_index(drop=True)
    clean["transaction_id"] = [f"TX{i+1:05d}" for i in range(len(clean))]

    clean = clean[[
        "transaction_id", "date", "description", "amount", "abs_amount", "type"
    ]]

    dropped = original_rows - len(clean)

    detected = {
        "date": col_map.get("date"),
        "description": col_map.get("description"),
        "amount": col_map.get("amount"),
        "debit": col_map.get("debit"),
        "credit": col_map.get("credit"),
        "type": col_map.get("type"),
    }

    quality = {
        "original_rows": int(original_rows),
        "clean_rows": int(len(clean)),
        "dropped_rows": int(dropped),
        "missing_descriptions": int(empty_desc),
        "date_range": (
            f"{clean['date'].min().date()} → {clean['date'].max().date()}"
            if not clean.empty else "n/a"
        ),
        "income_rows": int((clean["type"] == "income").sum()),
        "expense_rows": int((clean["type"] == "expense").sum()),
        "original_columns": original_cols,
        "detected_columns": {k: v for k, v in detected.items() if v},
        "valid": not clean.empty,
    }

    return {"df": clean, "quality": quality, "errors": errors}


def summarize_quality(quality: Dict[str, Any]) -> str:
    parts = [
        f"{quality['clean_rows']} clean transactions",
        f"{quality['income_rows']} income / {quality['expense_rows']} expense",
    ]
    if quality["dropped_rows"]:
        parts.append(f"{quality['dropped_rows']} dropped")
    return " • ".join(parts)
