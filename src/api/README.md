# Spam Detector API

API REST FastAPI pour servir le modèle de détection de spam.

## 🚀 Démarrage Rapide

### Installation des dépendances

```bash
pip install -r requirements.txt
```

### Lancer l'API

```bash
# Option 1 : Depuis la racine du projet
python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Option 2 : Depuis src/api/
cd src/api
python main.py
```

L'API sera accessible sur : `http://localhost:8000`

Documentation interactive :
- Swagger UI : `http://localhost:8000/docs`
- ReDoc : `http://localhost:8000/redoc`

## 📋 Endpoints Disponibles

### `GET /`
Point d'entrée racine avec informations sur l'API.

**Exemple :**
```bash
curl http://localhost:8000/
```

**Réponse :**
```json
{
  "name": "Spam Detector API",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs",
  "health": "/health"
}
```

---

### `GET /health`
Vérification de l'état de l'API et du modèle.

**Exemple :**
```bash
curl http://localhost:8000/health
```

**Réponse :**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "linear_svc",
  "version": "1.0.0"
}
```

---

### `POST /predict`
Prédiction pour un seul message.

**Exemple :**
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
  "confidence": 0.98,
  "message": "WIN FREE MONEY NOW!!!"
}
```

---

### `POST /predict/batch`
Prédictions pour plusieurs messages simultanément.

**Exemple :**
```bash
curl -X POST "http://localhost:8000/predict/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      "Meeting at 3pm tomorrow",
      "WIN FREE MONEY NOW!!!",
      "Can you send me the report?"
    ]
  }'
```

**Réponse :**
```json
{
  "predictions": [
    {
      "message": "Meeting at 3pm tomorrow",
      "prediction": "ham",
      "is_spam": false,
      "confidence": 0.33
    },
    {
      "message": "WIN FREE MONEY NOW!!!",
      "prediction": "spam",
      "is_spam": true,
      "confidence": 0.98
    },
    {
      "message": "Can you send me the report?",
      "prediction": "ham",
      "is_spam": false,
      "confidence": 0.35
    }
  ],
  "total": 3,
  "spam_count": 1,
  "ham_count": 2
}
```

---

### `GET /metrics`
Métriques du modèle ML et statistiques de l'API.

**Exemple :**
```bash
curl http://localhost:8000/metrics
```

**Réponse :**
```json
{
  "model_metrics": {
    "model": "linear_svc",
    "accuracy": 0.9956,
    "precision": 0.9963,
    "recall": 0.9854,
    "f1": 0.9908,
    "roc_auc": 0.9999
  },
  "system_metrics": {
    "uptime_seconds": 3600.0,
    "total_requests": 150,
    "total_predictions": 120,
    "spam_detected": 45,
    "ham_detected": 75,
    "model_loaded": true
  }
}
```

## 🏗️ Architecture

```
src/api/
├── __init__.py          # Exports du module
├── main.py             # Application FastAPI principale
├── model_loader.py     # Chargement et cache du modèle ML
├── schemas.py          # Schémas Pydantic (validation)
└── README.md           # Cette documentation
```

### Flux de Prédiction

```
Client → POST /predict → FastAPI
                           ↓
                    Validation (Pydantic)
                           ↓
                    Model Loader (cache)
                           ↓
                    Scikit-learn Pipeline
                           ↓
                    Text Cleaning → TF-IDF → LinearSVC
                           ↓
                    Response (JSON)
```

## 🧪 Tests

### Test manuel avec curl

```bash
# Test spam
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"message": "Congratulations! You won $1,000,000. Click here!"}'

# Test ham
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"message": "Meeting scheduled for tomorrow at 2pm"}'

# Test batch
curl -X POST "http://localhost:8000/predict/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      "Normal email about work",
      "FREE MONEY CLICK NOW!!!",
      "Project update for next week"
    ]
  }'
```

### Test avec Python

```python
import requests

# Single prediction
response = requests.post(
    "http://localhost:8000/predict",
    json={"message": "WIN FREE MONEY NOW!!!"}
)
print(response.json())

# Batch prediction
response = requests.post(
    "http://localhost:8000/predict/batch",
    json={
        "messages": [
            "Meeting at 3pm",
            "FREE PRIZE!!!",
            "Project report attached"
        ]
    }
)
print(response.json())
```

## 📊 Performance du Modèle

- **Accuracy** : 99.56%
- **Precision** : 99.63%
- **Recall** : 98.54%
- **F1-Score** : 99.08%
- **ROC-AUC** : 99.99%

Le modèle est un **LinearSVC** avec vectorisation TF-IDF.

## 🔧 Configuration

### Variables d'environnement (optionnel)

```bash
# Port de l'API
export API_PORT=8000

# Niveau de log
export LOG_LEVEL=info

# Path du modèle (par défaut: models/linear_svc.joblib)
export MODEL_PATH=/path/to/model.joblib
```

### CORS

Par défaut, CORS est activé pour toutes les origines (`allow_origins=["*"]`).

En production, configurez les origines autorisées dans [main.py](main.py:71) :

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Spécifiez vos domaines
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🚀 Déploiement

### Docker (voir Phase 2B)

```bash
# Build
docker build -t spam-detector-api .

# Run
docker run -p 8000:8000 spam-detector-api
```

### AWS (voir Phase 2C)

- **ECR** : Push de l'image Docker
- **App Runner / ECS Fargate** : Déploiement du conteneur
- **URL publique** : API accessible via HTTPS

## 🐛 Troubleshooting

### Erreur : "Model not loaded"

**Cause :** Le fichier modèle n'existe pas.

**Solution :**
```bash
# Entraîner un modèle d'abord
python training/train.py --data-path data/spam.csv --model linear_svc
```

### Erreur : "Module not found"

**Cause :** Dépendances manquantes.

**Solution :**
```bash
pip install -r requirements.txt
```

### Port 8000 déjà utilisé

**Solution :**
```bash
# Utiliser un autre port
uvicorn src.api.main:app --port 8080
```

## 📝 Prochaines Améliorations

- [ ] Authentification API (JWT tokens)
- [ ] Rate limiting (limitation du nombre de requêtes)
- [ ] Monitoring avec Prometheus
- [ ] Logging structuré (JSON)
- [ ] Tests unitaires et d'intégration
- [ ] Cache Redis pour les prédictions fréquentes
- [ ] Support de plusieurs modèles (A/B testing)

## 📚 Ressources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
