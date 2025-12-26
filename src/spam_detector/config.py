"""Default configuration values for the spam detector project."""

from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent.parent

DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "spam.csv"
DEFAULT_MODELS_DIR = PROJECT_ROOT / "models"

TEST_SIZE = 0.2
RANDOM_STATE = 42

TFIDF_PARAMS = {
    "ngram_range": (1, 2),
    "min_df": 1,
}

MODEL_PARAMS = {
    "linear_svc": {"C": 1.0},
    "multinomial_nb": {"alpha": 0.5},
    "log_reg": {"C": 1.0, "max_iter": 200, "solver": "liblinear"},
}
