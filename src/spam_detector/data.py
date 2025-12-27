"""Data loading and splitting helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import pandas as pd
from sklearn.model_selection import train_test_split

from .config import RANDOM_STATE, TEST_SIZE


def load_dataset(csv_path: Path | str) -> pd.DataFrame:
    """Load the spam dataset and normalize column names.

    Supports two formats:
    - Format 1: columns 'text' and 'spam' (where spam is 0/1)
    - Format 2: columns 'Message' and 'Category' (where Category is 'spam'/'ham')
    """
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at {path}")

    df = pd.read_csv(path)

    # Check which format we have and normalize to Message/Category
    if "text" in df.columns and "spam" in df.columns:
        # Format 1: text, spam (0/1)
        df = df.copy()
        df = df.rename(columns={"text": "Message", "spam": "Category"})
        # Convert 0/1 to ham/spam
        df["Category"] = df["Category"].apply(lambda x: "spam" if x == 1 else "ham")
    elif "Message" in df.columns and "Category" in df.columns:
        # Format 2: already in correct format
        df = df.copy()
    else:
        raise ValueError(
            f"CSV must contain either ('text', 'spam') or ('Message', 'Category') columns. "
            f"Found: {list(df.columns)}"
        )

    df["Category"] = df["Category"].astype(str).str.strip().str.lower()
    df["Message"] = df["Message"].astype(str).str.strip()
    return df


def encode_labels(df: pd.DataFrame) -> pd.Series:
    """Convert the Category column to binary labels (1=spam, 0=ham)."""
    return (df["Category"] == "spam").astype(int)


def get_features_and_labels(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
    """Return text features and encoded labels."""
    X = df["Message"]
    y = encode_labels(df)
    return X, y


def train_test_split_data(
    X,
    y,
    test_size: float = TEST_SIZE,
    random_state: int = RANDOM_STATE,
):
    """Perform a stratified train/test split."""
    return train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )
