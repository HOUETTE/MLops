# Spam Detector MLOps - Production Ready API

**Groupe G3-MG04** | Projet MLOps | Détection de Spam avec ML

Un projet MLOps complet de bout en bout : du pipeline de données au déploiement cloud AWS.

---

## 🎯 Vue d'ensemble

Ce projet implémente un système de détection de spam avec :
- 📊 **Pipeline de données ETL** complet et automatisé
- 🤖 **Modèle ML** performant (99.56% accuracy)
- 🚀 **API REST FastAPI** pour servir les prédictions
- 🐳 **Docker** pour la containerisation
- ☁️ **AWS** pour le déploiement (ECR, App Runner/ECS)
- 🔄 **CI/CD** avec GitHub Actions

---

## 📊 Performance du Modèle

| Métrique | Score |
|----------|-------|
| **Accuracy** | 99.56% |
| **Precision** | 99.63% |
| **Recall** | 98.54% |
| **F1-Score** | 99.08% |
| **ROC-AUC** | 99.99% |

**Modèle** : LinearSVC + TF-IDF (word 1-2 grams)
**Dataset** : 5,695 messages (4,327 ham / 1,368 spam)

---

## 🏗️ Architecture du Projet

```
MLops/
├── .github/workflows/       # CI/CD GitHub Actions
│   ├── test-aws.yml        # Test connexion AWS
│   └── deploy.yml          # Build + Push ECR
│
├── src/
│   ├── data/               # Pipeline ETL
│   │   ├── download_data.py
│   │   ├── clean_transform.py
│   │   ├── load_final.py
│   │   └── data_pipeline.py
│   │
│   ├── spam_detector/      # Package ML
│   │   ├── config.py
│   │   ├── data.py
│   │   ├── preprocessing.py
│   │   ├── modeling.py
│   │   └── evaluation.py
│   │
│   └── api/                # API FastAPI
│       ├── main.py
│       ├── model_loader.py
│       └── schemas.py
│
├── training/               # Scripts d'entraînement
│   ├── train.py
│   └── compare_models.py
│
├── models/                 # Modèles entraînés
│   ├── linear_svc.joblib
│   └── linear_svc_metrics.json
│
├── data/                   # Données
│   ├── spam.csv           # Dataset final
│   ├── raw/               # Données brutes
│   └── processed/         # Données nettoyées
│
├── Dockerfile              # Image Docker multi-stage
├── docker-compose.yml      # Orchestration locale
├── requirements.txt        # Dépendances Python
│
└── Documentation/
    ├── DOCKER.md          # Guide Docker
    ├── DEPLOYMENT.md      # Guide déploiement AWS
    └── README.md          # Ce fichier
```

---

## 🚀 Démarrage Rapide

### 1. Installation

```bash
# Cloner le repo
git clone <votre-repo-url>
cd MLops

# Créer environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Installer dépendances
pip install -r requirements.txt
```

### 2. Pipeline de Données

```bash
# Exécuter le pipeline ETL complet
python src/data/data_pipeline.py --source local

# Ou étape par étape
python src/data/download_data.py
python src/data/clean_transform.py
python src/data/load_final.py
```

### 3. Entraînement du Modèle

```bash
# Entraîner un modèle
python training/train.py --data-path data/spam.csv --model linear_svc

# Comparer plusieurs modèles
python training/compare_models.py --data-path data/spam.csv
```

### 4. Lancer l'API

```bash
# Option 1: Directement avec Python
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Option 2: Avec Docker
docker-compose up

# Option 3: Build et run Docker
docker build -t spam-detector-api:latest .
docker run -p 8000:8000 spam-detector-api:latest
```

Accédez à :
- **API** : http://localhost:8000
- **Docs (Swagger)** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

---

## 📡 Endpoints de l'API

### `GET /health`
Vérification de l'état du service

```bash
curl http://localhost:8000/health
```

### `POST /predict`
Prédiction pour un message

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"message": "WIN FREE MONEY NOW!!!"}'
```

**Réponse :**
```json
{
  "prediction": "spam",
  "is_spam": true,
  "confidence": 0.65,
  "message": "WIN FREE MONEY NOW!!!"
}
```

### `POST /predict/batch`
Prédictions multiples

```bash
curl -X POST "http://localhost:8000/predict/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      "Meeting at 3pm",
      "FREE MONEY!!!",
      "Project update"
    ]
  }'
```

### `GET /metrics`
Métriques du modèle et de l'API

```bash
curl http://localhost:8000/metrics
```

---

## 🐳 Docker

### Build

```bash
docker build -t spam-detector-api:latest .
```

### Run

```bash
docker run -d --name spam-api -p 8000:8000 spam-detector-api:latest
```

### Docker Compose

```bash
# Démarrer
docker-compose up -d

# Arrêter
docker-compose down
```

Voir [DOCKER.md](DOCKER.md) pour plus de détails.

---

## ☁️ Déploiement AWS

### Ressources AWS (Groupe G3-MG04)

| Ressource | Nom | Région |
|-----------|-----|--------|
| **S3 Data** | `s3-g3-mg04-data` | eu-north-1 |
| **S3 Terraform** | `tfstate-g3-mg04-mlops` | eu-north-1 |
| **ECR** | `ecr-g3-mg04-mlops` | eu-north-1 |
| **IAM User** | `iam-g3-mg04-github-actions` | - |

### Push vers ECR

```bash
# 1. Login ECR
aws ecr get-login-password --region eu-north-1 | \
  docker login --username AWS --password-stdin \
  073184925698.dkr.ecr.eu-north-1.amazonaws.com

# 2. Tag l'image
docker tag spam-detector-api:latest \
  073184925698.dkr.ecr.eu-north-1.amazonaws.com/ecr-g3-mg04-mlops:latest

# 3. Push
docker push 073184925698.dkr.ecr.eu-north-1.amazonaws.com/ecr-g3-mg04-mlops:latest
```

### Déploiement App Runner

Voir le guide complet : [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 🔄 CI/CD avec GitHub Actions

### Workflows disponibles

1. **test-aws.yml** : Test de la connexion AWS
2. **deploy.yml** : Build + Push ECR automatique

### Configuration requise

Ajouter ces secrets dans GitHub :
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION` = `eu-north-1`

---

## 📚 Documentation

| Fichier | Description |
|---------|-------------|
| [src/data/README.md](src/data/README.md) | Documentation du pipeline de données |
| [src/api/README.md](src/api/README.md) | Documentation de l'API |
| [DOCKER.md](DOCKER.md) | Guide Docker complet |
| [DEPLOYMENT.md](DEPLOYMENT.md) | Guide de déploiement AWS |

---

## 🧪 Tests

### Test de l'API locale

```bash
# Health check
curl http://localhost:8000/health

# Prédiction spam
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"message": "WIN FREE MONEY"}'

# Prédiction ham
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"message": "Meeting tomorrow at 3pm"}'
```

---

## 📦 Stack Technique

### Machine Learning
- **scikit-learn** : ML pipeline (TF-IDF + LinearSVC)
- **pandas** : Manipulation de données
- **numpy** : Calculs numériques

### API
- **FastAPI** : Framework web moderne
- **Pydantic** : Validation des données
- **Uvicorn** : Serveur ASGI

### DevOps
- **Docker** : Containerisation
- **AWS ECR** : Registry Docker
- **AWS App Runner/ECS** : Déploiement cloud
- **GitHub Actions** : CI/CD

---

## 🎓 Phases du Projet

### ✅ Phase 1 : Data & Model Pipeline
- Pipeline ETL complet (download, clean, load)
- Entraînement de 3 modèles (LinearSVC, MultinomialNB, LogReg)
- Sélection du meilleur modèle (LinearSVC : 99.56% accuracy)
- Configuration GitHub ↔ AWS

### ✅ Phase 2A : API
- API REST FastAPI avec 5 endpoints
- Validation Pydantic
- Documentation Swagger auto-générée
- Métriques en temps réel

### ✅ Phase 2B : Dockerisation
- Multi-stage Dockerfile optimisé (~210MB)
- Docker Compose pour développement
- Health checks intégrés
- Utilisateur non-root pour sécurité

### ✅ Phase 2C : CI/CD & Déploiement
- Workflow GitHub Actions (build + push ECR)
- Image Docker sur ECR
- Guide de déploiement App Runner/ECS
- Tests automatisés

---

## 👥 Équipe

**Groupe G3-MG04**

- Membres du groupe (à compléter)

---

## 📝 Licence

Ce projet est réalisé dans le cadre d'un projet académique MLOps.

---

## 🔗 Liens Utiles

- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [AWS App Runner](https://docs.aws.amazon.com/apprunner/)
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [GitHub Actions](https://docs.github.com/en/actions)

---

**Projet généré avec [Claude Code](https://claude.com/claude-code)**
