# Guide de Déploiement - Spam Detector API

## 📋 Architecture

1. **Interface Streamlit** : Streamlit Cloud
2. **API FastAPI** : AWS EC2 via Docker  
3. **Images Docker** : AWS ECR
4. **CI/CD** : GitHub Actions

## 🚀 Déploiement Streamlit Cloud

1. Aller sur https://share.streamlit.io/
2. New app → Repository: MLops, Branch: main, File: app.py
3. Requirements file: requirements-streamlit.txt
4. Deploy !

## 🐳 GitHub Actions

Secrets à configurer (Settings → Secrets):
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY

Le workflow build automatiquement l'image AMD64 et la push vers ECR.

## ☁️ Déploiement EC2  

Instance: 54.75.77.83

Connexion via EC2 Instance Connect puis:

```bash
# Configure AWS
aws configure

# Login ECR
aws ecr get-login-password --region eu-west-1 | docker login --username AWS --password-stdin 073184925698.dkr.ecr.eu-west-1.amazonaws.com

# Pull image
docker pull 073184925698.dkr.ecr.eu-west-1.amazonaws.com/ecr-g3-mg04-mlops-ireland:latest

# Run
docker run -d --name spam-detector-api -p 8000:8000 --restart unless-stopped 073184925698.dkr.ecr.eu-west-1.amazonaws.com/ecr-g3-mg04-mlops-ireland:latest
```

## 🧪 Tests

```bash
curl http://54.75.77.83:8000/health
curl -X POST http://54.75.77.83:8000/predict -H "Content-Type: application/json" -d '{"message": "WIN FREE MONEY"}'
```

🤖 Generated with Claude Code
