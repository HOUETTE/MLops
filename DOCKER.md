# Docker Guide - Spam Detector API

Guide complet pour la dockerisation et le déploiement de l'API de détection de spam.

## 🐳 Prérequis

- Docker Desktop installé
- Compte AWS avec accès à ECR (pour le déploiement)
- AWS CLI configuré

## 📦 Build de l'Image Docker

### Build local simple

```bash
docker build -t spam-detector-api:latest .
```

### Build avec tag ECR (pour AWS)

```bash
# Format: <account-id>.dkr.ecr.<region>.amazonaws.com/<repository-name>:<tag>
docker build -t spam-detector-api:latest \
  -t 073184925698.dkr.ecr.eu-north-1.amazonaws.com/ecr-g3-mg04-mlops:latest .
```

### Vérifier l'image créée

```bash
docker images | grep spam-detector-api
```

## 🚀 Run de l'Image Localement

### Avec Docker run

```bash
# Démarrer le conteneur
docker run -d \
  --name spam-api \
  -p 8000:8000 \
  spam-detector-api:latest

# Vérifier les logs
docker logs spam-api

# Tester l'API
curl http://localhost:8000/health

# Arrêter et supprimer
docker stop spam-api
docker rm spam-api
```

### Avec Docker Compose (recommandé)

```bash
# Démarrer
docker-compose up -d

# Voir les logs
docker-compose logs -f

# Arrêter
docker-compose down
```

## 🧪 Tests du Conteneur

### Test du health check

```bash
curl http://localhost:8000/health
```

**Réponse attendue :**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "linear_svc",
  "version": "1.0.0"
}
```

### Test de prédiction

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{"message": "WIN FREE MONEY NOW"}'
```

**Réponse attendue :**
```json
{
  "prediction": "spam",
  "is_spam": true,
  "confidence": 0.65,
  "message": "WIN FREE MONEY NOW"
}
```

## ☁️ Déploiement sur AWS ECR

### 1. Authentification à ECR

```bash
# Se connecter à ECR
aws ecr get-login-password --region eu-north-1 | \
  docker login --username AWS --password-stdin \
  073184925698.dkr.ecr.eu-north-1.amazonaws.com
```

### 2. Tag de l'image

```bash
docker tag spam-detector-api:latest \
  073184925698.dkr.ecr.eu-north-1.amazonaws.com/ecr-g3-mg04-mlops:latest
```

### 3. Push vers ECR

```bash
docker push 073184925698.dkr.ecr.eu-north-1.amazonaws.com/ecr-g3-mg04-mlops:latest
```

### 4. Vérifier le push

```bash
aws ecr describe-images \
  --repository-name ecr-g3-mg04-mlops \
  --region eu-north-1
```

## 📊 Architecture de l'Image Docker

### Multi-stage Build

L'image utilise un build multi-stage pour optimiser la taille :

1. **Stage Builder** : Installation des dépendances
2. **Stage Runtime** : Image minimale pour la production

### Avantages

- ✅ Taille d'image réduite (~200MB au lieu de ~1GB)
- ✅ Sécurité renforcée (utilisateur non-root)
- ✅ Build reproductible
- ✅ Dépendances de build non incluses dans l'image finale

### Structure de l'image

```
/app/
├── src/api/           # Code de l'API
│   ├── main.py
│   ├── model_loader.py
│   └── schemas.py
└── models/            # Modèle ML entraîné
    ├── linear_svc.joblib
    └── linear_svc_metrics.json
```

## 🔒 Sécurité

### Utilisateur non-root

L'image utilise un utilisateur `appuser` (UID 1000) pour exécuter l'application :

```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

### Health Check

Health check intégré pour vérifier l'état de l'API :

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"
```

## 📏 Taille de l'Image

```bash
# Vérifier la taille
docker images spam-detector-api:latest

# Analyser les layers
docker history spam-detector-api:latest
```

**Taille optimisée :**
- Image de base : `python:3.11-slim` (~150MB)
- Dépendances Python : ~50MB
- Code + modèle : ~10MB
- **Total : ~210MB**

## 🐛 Debugging

### Accéder au conteneur

```bash
# Shell interactif dans le conteneur
docker exec -it spam-api /bin/bash

# Voir les logs en temps réel
docker logs -f spam-api

# Inspecter le conteneur
docker inspect spam-api
```

### Variables d'environnement

```bash
# Avec des variables personnalisées
docker run -d \
  --name spam-api \
  -p 8000:8000 \
  -e LOG_LEVEL=debug \
  -e PORT=8080 \
  spam-detector-api:latest
```

## 🔄 CI/CD avec GitHub Actions

Le workflow GitHub Actions automatise :
1. Build de l'image Docker
2. Push vers ECR
3. Déploiement sur ECS/App Runner

Voir [.github/workflows/deploy.yml](.github/workflows/deploy.yml) (Phase 2C)

## 📝 Commandes Utiles

### Nettoyage

```bash
# Supprimer les conteneurs arrêtés
docker container prune

# Supprimer les images non utilisées
docker image prune

# Nettoyage complet
docker system prune -a
```

### Monitoring

```bash
# Statistiques du conteneur
docker stats spam-api

# Top des processus
docker top spam-api

# Consommation des ressources
docker inspect spam-api | grep -A 20 "HostConfig"
```

## 🚀 Déploiement sur AWS App Runner

Une fois l'image dans ECR :

```bash
# Créer un service App Runner (via console AWS ou CLI)
aws apprunner create-service \
  --service-name spam-detector-api-g3-mg04 \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "073184925698.dkr.ecr.eu-north-1.amazonaws.com/ecr-g3-mg04-mlops:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8000"
      }
    },
    "AutoDeploymentsEnabled": true
  }' \
  --instance-configuration '{
    "Cpu": "1 vCPU",
    "Memory": "2 GB"
  }' \
  --region eu-north-1
```

## 🎯 Bonnes Pratiques

1. **Toujours tagger vos images** avec des versions sémantiques
2. **Utiliser multi-stage builds** pour réduire la taille
3. **Scanner les vulnérabilités** avec `docker scan`
4. **Utiliser .dockerignore** pour exclure les fichiers inutiles
5. **Définir des health checks** pour la résilience
6. **Utiliser un utilisateur non-root** pour la sécurité

## 📚 Ressources

- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [AWS ECR Documentation](https://docs.aws.amazon.com/ecr/)
- [AWS App Runner Documentation](https://docs.aws.amazon.com/apprunner/)
