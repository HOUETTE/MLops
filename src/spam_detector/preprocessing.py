"""Text preprocessing utilities."""

from __future__ import annotations

import re
from typing import Iterable, List

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin


def clean_text(text: str) -> str:
    """Basic text cleaning used before vectorization."""
    text = str(text).lower()
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"\S+@\S+", " ", text)
    text = re.sub(r"\b\d{3,}\b", " ", text)
    text = re.sub(r"[^a-z\\s']", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


class TextCleaner(BaseEstimator, TransformerMixin):
    """Sklearn-compatible transformer applying `clean_text`."""

    def __init__(self, cleaner=clean_text):
        self.cleaner = cleaner

    def fit(self, X, y=None):  # noqa: N803
        return self

    def transform(self, X: Iterable[str]) -> np.ndarray:  # noqa: N803
        return np.array([self.cleaner(text) for text in X])


def clean_corpus(corpus: Iterable[str]) -> List[str]:
    """Clean an iterable of strings and return a list."""
    return [clean_text(text) for text in corpus]
