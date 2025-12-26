"""Train a spam detector model and export artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.spam_detector import (  # noqa: E402
    AVAILABLE_MODELS,
    DEFAULT_DATA_PATH,
    DEFAULT_MODELS_DIR,
    RANDOM_STATE,
    TEST_SIZE,
    evaluate_model,
    get_model_pipeline,
    load_dataset,
    train_test_split_data,
)
from src.spam_detector.data import get_features_and_labels  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a spam detector model.")
    parser.add_argument(
        "--data-path",
        type=Path,
        default=DEFAULT_DATA_PATH,
        help="Path to spam.csv dataset",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="linear_svc",
        choices=AVAILABLE_MODELS,
        help="Model to train",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_MODELS_DIR,
        help="Directory to store trained model and metrics",
    )
    parser.add_argument(
        "--test-size",
        type=float,
        default=TEST_SIZE,
        help="Fraction of data used for testing",
    )
    parser.add_argument(
        "--random-state",
        type=int,
        default=RANDOM_STATE,
        help="Random seed for splits",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = load_dataset(args.data_path)
    X, y = get_features_and_labels(df)

    X_train, X_test, y_train, y_test = train_test_split_data(
        X, y, test_size=args.test_size, random_state=args.random_state
    )

    model = get_model_pipeline(args.model)
    model.fit(X_train, y_train)
    metrics = evaluate_model(model, X_train, y_train, X_test, y_test, args.model)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    model_path = args.output_dir / f"{args.model}.joblib"
    metrics_path = args.output_dir / f"{args.model}_metrics.json"

    joblib.dump(model, model_path)
    with metrics_path.open("w") as f:
        json.dump(metrics, f, indent=2)

    print(f"Saved model to {model_path}")
    print(f"Saved metrics to {metrics_path}")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
