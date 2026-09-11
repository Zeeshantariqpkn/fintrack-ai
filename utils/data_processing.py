"""Data processing utilities for FinTrack AI."""

import pandas as pd


def load_and_clean(file) -> pd.DataFrame:
    """
    Load a financial CSV and clean the core fields.

    Required columns:
    - date
    - description
    - amount
    """

    df = pd.read_csv(file)

    # Normalize column names
    df.columns = [
        str(column).strip().lower()
        for column in df.columns
    ]

    required_columns = {
        "date",
        "description",
        "amount",
    }

    missing_columns = (
        required_columns - set(df.columns)
    )

    if missing_columns:

        raise ValueError(
            "Missing required columns: "
            + ", ".join(
                sorted(missing_columns)
            )
        )

    # Clean dates
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce",
    )

    # Clean amounts
    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce",
    )

    # Clean descriptions
    df["description"] = (
        df["description"]
        .astype(str)
        .str.strip()
    )

    # Remove invalid rows
    df = df.dropna(
        subset=[
            "date",
            "amount",
            "description",
        ]
    ).copy()

    # Remove empty descriptions
    df = df[
        df["description"].ne("")
    ].copy()

    # Create month field
    df["month"] = (
        df["date"]
        .dt.to_period("M")
        .astype(str)
    )

    # Determine transaction type
    df["type"] = df["amount"].apply(
        lambda amount:
        "income"
        if amount > 0
        else "expense"
    )

    # Sort chronologically
    df = (
        df.sort_values("date")
        .reset_index(drop=True)
    )

    return df


def compute_stats(
    df: pd.DataFrame,
) -> dict:
    """
    Calculate financial analytics from
    processed transactions.
    """

    # ---------------------------------------
    # Expenses
    # ---------------------------------------

    expenses = df[
        df["type"] == "expense"
    ].copy()

    # Convert negative expenses to positive
    # values for reporting
    expenses["abs_amount"] = (
        expenses["amount"].abs()
    )

    # ---------------------------------------
    # Spending by category
    # ---------------------------------------

    if "category" in expenses.columns:

        by_category = (
            expenses
            .groupby("category")[
                "abs_amount"
            ]
            .sum()
            .sort_values(
                ascending=False
            )
        )

    else:

        by_category = None

    # ---------------------------------------
    # Monthly income and expenses
    # ---------------------------------------

    monthly = (
        df
        .groupby(
            ["month", "type"]
        )["amount"]
        .sum()
        .unstack(
            fill_value=0
        )
    )

    # Expenses are stored as negative
    # amounts, so make them positive
    # for chart/reporting purposes.
    if "expense" in monthly.columns:

        monthly["expense"] = (
            monthly["expense"].abs()
        )

    # ---------------------------------------
    # Top vendors/descriptions
    # ---------------------------------------

    top_vendors = (
        expenses
        .groupby("description")[
            "abs_amount"
        ]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(10)
    )

    # ---------------------------------------
    # Recurring expenses
    # ---------------------------------------

    recurring = (
        expenses
        .groupby("description")[
            "month"
        ]
        .nunique()
        .sort_values(
            ascending=False
        )
    )

    # A transaction appearing in at least
    # two different months is considered
    # potentially recurring.
    recurring = recurring[
        recurring >= 2
    ]

    # ---------------------------------------
    # Total income
    # ---------------------------------------

    total_income = float(
        df[
            df["type"] == "income"
        ]["amount"].sum()
    )

    # ---------------------------------------
    # Total expenses
    # ---------------------------------------

    total_expense = float(
        expenses["abs_amount"].sum()
    )

    return {
        "by_category": by_category,
        "monthly": monthly,
        "top_vendors": top_vendors,
        "recurring": recurring,
        "total_income": total_income,
        "total_expense": total_expense,
    }