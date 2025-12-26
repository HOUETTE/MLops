"""Evaluation helpers for classifiers."""

from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
    roc_auc_score,
)


def _compute_auc(model, X_test, y_test) -> Optional[float]:
    if hasattr(model, "decision_function"):
        scores = model.decision_function(X_test)
        return float(roc_auc_score(y_test, scores))
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X_test)[:, 1]
        return float(roc_auc_score(y_test, proba))
    return None


def evaluate_model(
    model,
    X_train,
    y_train,
    X_test,
    y_test,
    model_name: str,
) -> Dict[str, Any]:
    """Fit model (if not already fitted) and compute metrics."""
    if not hasattr(model, "classes_"):
        model.fit(X_train, y_train)

    preds = model.predict(X_test)
    auc = _compute_auc(model, X_test, y_test)

    acc = accuracy_score(y_test, preds)
    prec, rec, f1, _ = precision_recall_fscore_support(
        y_test, preds, average="binary", zero_division=0
    )
    cm = confusion_matrix(y_test, preds)

    return {
        "model": model_name,
        "accuracy": float(acc),
        "precision": float(prec),
        "recall": float(rec),
        "f1": float(f1),
        "roc_auc": auc,
        "confusion_matrix": cm.tolist(),
    }
