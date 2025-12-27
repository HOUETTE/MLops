# Data Pipeline

Ce module contient le pipeline ETL (Extract, Transform, Load) complet pour le projet Spam Detector.

## Architecture du Pipeline

```
┌─────────────────────┐
│  1. Download Data   │  ← Télécharge les données brutes
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│ 2. Clean Transform  │  ← Nettoie et transforme les données
└──────────┬──────────┘
           │
           v
┌─────────────────────┐
│  3. Load Final      │  ← Charge les données finales (+ S3 optionnel)
└─────────────────────┘
```

## Structure des Fichiers

```
src/data/
├── __init__.py           # Exports des fonctions principales
├── download_data.py      # Téléchargement des données brutes
├── clean_transform.py    # Nettoyage et transformation
├── load_final.py         # Chargement final (+ upload S3)
├── data_pipeline.py      # Orchestration complète du pipeline
└── README.md            # Cette documentation
```

## Utilisation

### Option 1 : Pipeline Complet (Recommandé)

Exécuter tout le pipeline en une seule commande :

```bash
# Pipeline local uniquement
python src/data/data_pipeline.py --source local

# Pipeline avec upload S3
python src/data/data_pipeline.py --source local --upload-to-s3 --s3-bucket groupeX-data --s3-key data/spam.csv
```

### Option 2 : Étapes Individuelles

Exécuter chaque étape séparément :

```bash
# Étape 1 : Téléchargement
python src/data/download_data.py --source local --output data/raw/spam_raw.csv

# Étape 2 : Nettoyage et transformation
python src/data/clean_transform.py --input data/raw/spam_raw.csv --output data/processed/spam_processed.csv

# Étape 3 : Chargement final
python src/data/load_final.py --input data/processed/spam_processed.csv --output data/spam.csv
```

## Flux de Données

### 1. Download Data (`download_data.py`)

**Sources supportées :**
- `local` : Copie depuis `data/spam.csv` existant
- `s3` : Télécharge depuis un bucket S3 (à implémenter)
- `url` : Télécharge depuis une URL publique (à implémenter)

**Output :** `data/raw/spam_raw.csv`

### 2. Clean & Transform (`clean_transform.py`)

**Opérations de nettoyage :**
1. Normalisation des noms de colonnes
2. Suppression des doublons
3. Gestion des valeurs manquantes
4. Nettoyage du texte
5. Suppression des messages vides
6. Validation des catégories
7. Ajout de métadonnées (longueur, nombre de mots)

**Input :** `data/raw/spam_raw.csv`
**Output :** `data/processed/spam_processed.csv`

### 3. Load Final (`load_final.py`)

**Opérations :**
1. Chargement des données processées
2. Validation finale
3. Sélection des colonnes nécessaires
4. Sauvegarde locale
5. Upload S3 optionnel

**Input :** `data/processed/spam_processed.csv`
**Output :** `data/spam.csv` (+ S3 optionnel)

## Formats de Données Supportés

Le pipeline supporte deux formats CSV :

### Format 1 : `text`, `spam`
```csv
text,spam
"Message content...",1
"Another message...",0
```

### Format 2 : `Message`, `Category`
```csv
Message,Category
"Message content...","spam"
"Another message...","ham"
```

Les deux formats sont automatiquement normalisés vers le format 2.

## Configuration AWS (pour S3)

Pour utiliser les fonctionnalités S3, installez boto3 :

```bash
pip install boto3
```

Et configurez vos credentials AWS :
```bash
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
```

Ou utilisez les secrets GitHub Actions (voir `.github/workflows/`).

## Logs et Monitoring

Tous les scripts génèrent des logs détaillés :
- Niveau INFO pour les opérations normales
- Niveau WARNING pour les anomalies non-bloquantes
- Niveau ERROR pour les erreurs fatales

Exemple de sortie :
```
2025-12-27 17:54:33 - INFO - Loading raw data from data/raw/spam_raw.csv
2025-12-27 17:54:33 - INFO - Initial dataset shape: (5728, 2)
2025-12-27 17:54:33 - INFO - Removed 33 duplicate messages
2025-12-27 17:54:33 - INFO - Final dataset shape: (5695, 2)
```

## Statistiques du Pipeline

Après chaque exécution, le pipeline affiche :
- Nombre de lignes initiales
- Nombre de lignes après nettoyage
- Distribution des catégories (spam/ham)
- Longueur moyenne des messages
- Temps d'exécution

## Prochaines Étapes

Pour intégrer ce pipeline dans votre workflow MLOps :

1. **CI/CD** : Ajoutez une GitHub Action pour exécuter le pipeline automatiquement
2. **Monitoring** : Ajoutez des métriques (CloudWatch, Prometheus)
3. **Versioning** : Versionnez vos datasets avec DVC ou MLflow
4. **Automation** : Planifiez l'exécution périodique (cron, Airflow)

## Troubleshooting

### Erreur : "Dataset not found"
- Vérifiez que `data/spam.csv` existe
- Ou spécifiez une autre source avec `--source`

### Erreur : "boto3 not installed"
- Installez boto3 : `pip install boto3`

### Erreur : "Invalid columns"
- Vérifiez que votre CSV a les colonnes `text/spam` ou `Message/Category`
