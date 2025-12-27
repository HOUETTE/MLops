"""Clean and transform raw spam data."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RAW_FILE = PROJECT_ROOT / "data" / "raw" / "spam_raw.csv"
DEFAULT_PROCESSED_FILE = PROJECT_ROOT / "data" / "processed" / "spam_processed.csv"


def clean_and_transform(
    input_path: Path | str,
    output_path: Path | str,
) -> pd.DataFrame:
    """Clean and transform raw spam dataset.

    Cleaning steps:
    1. Remove duplicates
    2. Handle missing values
    3. Normalize column names
    4. Validate data types
    5. Remove invalid entries
    6. Standardize text encoding

    Args:
        input_path: Path to raw data CSV
        output_path: Path to save cleaned data

    Returns:
        Cleaned DataFrame
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Loading raw data from {input_path}")
    df = pd.read_csv(input_path)
    logger.info(f"Initial dataset shape: {df.shape}")

    # Log initial statistics
    logger.info(f"Columns: {list(df.columns)}")
    initial_rows = len(df)

    # Step 1: Normalize column names
    if "text" in df.columns and "spam" in df.columns:
        df = df.rename(columns={"text": "Message", "spam": "Category"})
        # Convert 0/1 to ham/spam
        df["Category"] = df["Category"].apply(lambda x: "spam" if x == 1 else "ham")
        logger.info("Normalized column names: text->Message, spam->Category")
    elif "Message" in df.columns and "Category" in df.columns:
        logger.info("Columns already in correct format")
    else:
        raise ValueError(
            f"Unexpected columns: {list(df.columns)}. "
            "Expected 'text'/'spam' or 'Message'/'Category'"
        )

    # Step 2: Remove duplicates
    df = df.drop_duplicates(subset=["Message"], keep="first")
    logger.info(f"Removed {initial_rows - len(df)} duplicate messages")

    # Step 3: Handle missing values
    missing_before = df.isnull().sum().sum()
    df = df.dropna(subset=["Message", "Category"])
    missing_after = df.isnull().sum().sum()
    logger.info(f"Removed {missing_before - missing_after} rows with missing values")

    # Step 4: Clean text data
    df["Message"] = df["Message"].astype(str).str.strip()
    df["Category"] = df["Category"].astype(str).str.strip().str.lower()

    # Step 5: Remove empty messages
    empty_messages = df["Message"].str.len() == 0
    df = df[~empty_messages]
    logger.info(f"Removed {empty_messages.sum()} empty messages")

    # Step 6: Validate categories
    valid_categories = {"spam", "ham"}
    invalid_mask = ~df["Category"].isin(valid_categories)
    invalid_count = invalid_mask.sum()
    if invalid_count > 0:
        logger.warning(f"Found {invalid_count} invalid categories, removing them")
        df = df[~invalid_mask]

    # Step 7: Add metadata
    df["message_length"] = df["Message"].str.len()
    df["word_count"] = df["Message"].str.split().str.len()

    # Log final statistics
    logger.info(f"Final dataset shape: {df.shape}")
    logger.info(f"Category distribution:\n{df['Category'].value_counts()}")
    logger.info(f"Average message length: {df['message_length'].mean():.1f} characters")
    logger.info(f"Average word count: {df['word_count'].mean():.1f} words")

    # Save cleaned data
    df.to_csv(output_path, index=False)
    logger.info(f"Saved cleaned data to {output_path}")

    return df


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Clean and transform raw spam data"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_RAW_FILE,
        help="Input path for raw data",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_PROCESSED_FILE,
        help="Output path for cleaned data",
    )
    return parser.parse_args()


def main() -> None:
    """Main entry point for the cleaning script."""
    args = parse_args()

    try:
        df = clean_and_transform(
            input_path=args.input,
            output_path=args.output,
        )
        logger.info(f"✓ Successfully cleaned data: {len(df)} rows")
        sys.exit(0)
    except Exception as e:
        logger.error(f"✗ Failed to clean data: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
