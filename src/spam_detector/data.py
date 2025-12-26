"""Data loading and splitting helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

import pandas as pd
from sklearn.model_selection import train_test_split

from .config import RANDOM_STATE, TEST_SIZE


def load_dataset(csv_path: Path | str) -> pd.DataFrame:
    """Load the spam dataset and normalize column names."""
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at {path}")

    df = pd.read_csv(path)
    required_columns = {"Category", "Message"}
    if not required_columns.issubset(df.columns):
        raise ValueError(f"CSV must contain columns {required_columns}")

    df = df.copy()
    df["Category"] = df["Category"].astype(str).str.strip().str.lower()
    df["Message"] = df["Message"].astype(str).str.strip()
    return df


def encode_labels(df: pd.DataFrame) -> pd.Series:
    """Convert the Category column to binary labels."""
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
