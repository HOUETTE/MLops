# Spam Detector MLOps Refactor

This project refactors the Lab02 spam classifier notebook into a modular Python package ready for future API, Docker, and CI/CD work.

## Structure
- `src/spam_detector/`: reusable package (config, data loading, preprocessing, modeling, evaluation)
- `training/`: scripts to train one model or compare all supported models
- `models/`: exported pipelines and metrics
- `data/spam.csv`: Kaggle spam dataset copy
- `notebooks/Lab02.ipynb`: original exploratory notebook (reference only)

## Quickstart
1. Install dependencies (preferably in a virtual env):
   ```bash
   pip install -r requirements.txt
   ```
2. Train the default Linear SVC + TF-IDF pipeline and export artifacts:
   ```bash
   python training/train.py --data-path data/spam.csv --model linear_svc
   ```
3. Compare all supported models (Linear SVC, Multinomial NB, Logistic Regression):
   ```bash
   python training/compare_models.py --data-path data/spam.csv
   ```

Artifacts are saved to `models/` by default (`.joblib` pipeline + `_metrics.json`).

## Notes
- Pipelines include the text cleaning step, so saved models are ready for serving.
- Defaults mirror the notebook: TF-IDF word 1–2 grams, 80/20 split, `random_state=42`.
- No NLTK downloads or notebook logic are required for training.
