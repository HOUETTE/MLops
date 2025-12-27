# Guide de Déploiement AWS - Spam Detector API

Guide complet pour déployer l'API sur AWS App Runner ou ECS Fargate.

## 📋 Prérequis

- ✅ Image Docker pushée sur ECR : `073184925698.dkr.ecr.eu-north-1.amazonaws.com/ecr-g3-mg04-mlops:latest`
- ✅ Secrets GitHub configurés (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION)
- ✅ Repository ECR créé : `ecr-g3-mg04-mlops`
- ✅ Accès à la console AWS

---

## 🚀 Option 1 : Déploiement sur AWS App Runner (Recommandé - Plus Simple)

### Pourquoi App Runner ?
- ✅ Déploiement en 1 clic
- ✅ URL HTTPS automatique
- ✅ Auto-scaling automatique
- ✅ Pas de configuration d'infrastructure
- ✅ Tarification à l'utilisation

### Étapes de déploiement

#### 1. Via la Console AWS (Interface graphique)

**a) Accéder à App Runner**
1. Connectez-vous à la console AWS
2. Recherchez "App Runner" dans la barre de recherche
3. Cliquez sur "Create service"

**b) Configuration de la source**
1. **Repository type** : Container registry
2. **Provider** : Amazon ECR
3. **Container image URI** : `073184925698.dkr.ecr.eu-north-1.amazonaws.com/ecr-g3-mg04-mlops:latest`
4. **Deployment trigger** : Manual (ou Automatic pour auto-deploy)
5. **ECR access role** : Créer un nouveau rôle ou utiliser un existant
6. Cliquez sur "Next"

**c) Configuration du service**
1. **Service name** : `spam-detector-api-g3-mg04`
2. **Port** : `8000`
3. **CPU** : 1 vCPU
4. **Memory** : 2 GB
5. **Environment variables** : (optionnel)
   - `PYTHONUNBUFFERED=1`
   - `LOG_LEVEL=info`

**d) Configuration du réseau (optionnel)**
1. Laissez les paramètres par défaut (Public endpoint)

**e) Health check**
1. **Health check protocol** : HTTP
2. **Health check path** : `/health`
3. **Interval** : 30 seconds
4. **Timeout** : 10 seconds
5. **Healthy threshold** : 1
6. **Unhealthy threshold** : 3

**f) Review and create**
1. Vérifiez la configuration
2. Cliquez sur "Create & deploy"
3. Attendez 5-10 minutes (déploiement en cours)

**g) Récupérer l'URL**
Une fois déployé, vous obtiendrez une URL comme :
```
https://xxxxxxxxx.eu-north-1.awsapprunner.com
```

#### 2. Via AWS CLI

```bash
# Créer le service App Runner
aws apprunner create-service \
  --service-name spam-detector-api-g3-mg04 \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "073184925698.dkr.ecr.eu-north-1.amazonaws.com/ecr-g3-mg04-mlops:latest",
      "ImageRepositoryType": "ECR",
      "ImageConfiguration": {
        "Port": "8000",
        "RuntimeEnvironmentVariables": {
          "PYTHONUNBUFFERED": "1"
        }
      }
    },
    "AutoDeploymentsEnabled": false
  }' \
  --instance-configuration '{
    "Cpu": "1 vCPU",
    "Memory": "2 GB"
  }' \
  --health-check-configuration '{
    "Protocol": "HTTP",
    "Path": "/health",
    "Interval": 30,
    "Timeout": 10,
    "HealthyThreshold": 1,
    "UnhealthyThreshold": 3
  }' \
  --region eu-north-1

# Récupérer le statut et l'URL
aws apprunner describe-service \
  --service-arn <ARN_du_service> \
  --region eu-north-1 \
  --query 'Service.ServiceUrl' \
  --output text
```

---

## 🏗️ Option 2 : Déploiement sur ECS Fargate (Plus avancé)

### Pourquoi ECS Fargate ?
- ✅ Plus de contrôle sur l'infrastructure
- ✅ Support VPC personnalisé
- ✅ Integration avec ALB (Load Balancer)
- ✅ Support multi-conteneurs

### Étapes de déploiement

#### 1. Créer un cluster ECS

```bash
aws ecs create-cluster \
  --cluster-name g3-mg04-cluster \
  --region eu-north-1
```

#### 2. Créer une Task Definition

Créez un fichier `task-definition.json` :

```json
{
  "family": "spam-detector-task-g3-mg04",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::073184925698:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "spam-detector-api",
      "image": "073184925698.dkr.ecr.eu-north-1.amazonaws.com/ecr-g3-mg04-mlops:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "essential": true,
      "environment": [
        {
          "name": "PYTHONUNBUFFERED",
          "value": "1"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/spam-detector-g3-mg04",
          "awslogs-region": "eu-north-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 10,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

Enregistrez la task :

```bash
aws ecs register-task-definition \
  --cli-input-json file://task-definition.json \
  --region eu-north-1
```

#### 3. Créer un service ECS

```bash
aws ecs create-service \
  --cluster g3-mg04-cluster \
  --service-name spam-detector-api-g3-mg04 \
  --task-definition spam-detector-task-g3-mg04 \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxx],securityGroups=[sg-xxxxx],assignPublicIp=ENABLED}" \
  --region eu-north-1
```

---

## 🧪 Tester le Déploiement

Une fois déployé, testez votre API :

### 1. Health Check

```bash
curl https://votre-url.awsapprunner.com/health
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

### 2. Prédiction

```bash
curl -X POST "https://votre-url.awsapprunner.com/predict" \
  -H "Content-Type: application/json" \
  -d '{"message": "WIN FREE MONEY NOW!!!"}'
```

**Réponse attendue :**
```json
{
  "prediction": "spam",
  "is_spam": true,
  "confidence": 0.65,
  "message": "WIN FREE MONEY NOW!!!"
}
```

### 3. Métriques

```bash
curl https://votre-url.awsapprunner.com/metrics
```

---

## 📊 Monitoring et Logs

### CloudWatch Logs

```bash
# Voir les logs du service
aws logs tail /aws/apprunner/spam-detector-api-g3-mg04/application \
  --follow \
  --region eu-north-1
```

### Métriques CloudWatch

Les métriques suivantes sont automatiquement collectées :
- Requêtes par seconde
- Latence (P50, P90, P99)
- Erreurs 4xx/5xx
- CPU et mémoire utilisés

---

## 🔄 Mise à jour du Service

### App Runner

```bash
# Déclencher un nouveau déploiement
aws apprunner start-deployment \
  --service-arn <ARN_du_service> \
  --region eu-north-1
```

### ECS

```bash
# Forcer un nouveau déploiement
aws ecs update-service \
  --cluster g3-mg04-cluster \
  --service spam-detector-api-g3-mg04 \
  --force-new-deployment \
  --region eu-north-1
```

---

## 💰 Estimation des Coûts

### App Runner
- **CPU 1 vCPU + 2GB RAM** : ~$0.064/heure
- **Trafic** : $0.10/GB
- **Estimation mensuelle** : ~$50/mois (avec trafic modéré)

### ECS Fargate
- **CPU 1 vCPU + 2GB RAM** : ~$0.04856/heure
- **Load Balancer** : ~$16/mois
- **Estimation mensuelle** : ~$51/mois

---

## 🔒 Sécurité

### Variables d'environnement sensibles

Si vous avez des secrets (API keys, etc.), utilisez AWS Secrets Manager :

```bash
# Créer un secret
aws secretsmanager create-secret \
  --name spam-detector-secrets-g3-mg04 \
  --secret-string '{"API_KEY":"your-secret-key"}' \
  --region eu-north-1
```

---

## 🐛 Troubleshooting

### Le service ne démarre pas

1. Vérifiez les logs CloudWatch
2. Vérifiez que l'image ECR est accessible
3. Vérifiez le health check path (`/health`)
4. Vérifiez le port (doit être 8000)

### Erreur "Task failed to start"

```bash
# Vérifier les logs ECS
aws ecs describe-tasks \
  --cluster g3-mg04-cluster \
  --tasks <task-id> \
  --region eu-north-1
```

### L'API ne répond pas

1. Vérifiez le security group (port 8000 ouvert)
2. Vérifiez le health check
3. Testez en local avec Docker

---

## 📝 Checklist de Déploiement

- [ ] Image Docker pushée sur ECR
- [ ] Service App Runner créé
- [ ] Health check configuré (`/health`)
- [ ] URL publique récupérée
- [ ] Tests de l'API réussis
- [ ] Logs CloudWatch configurés
- [ ] Monitoring activé
- [ ] Documentation de l'URL dans le README

---

## 🎯 Prochaines Étapes

1. Configurer un nom de domaine personnalisé
2. Ajouter HTTPS avec certificat SSL
3. Configurer auto-scaling
4. Ajouter un WAF (Web Application Firewall)
5. Mettre en place des alertes CloudWatch

---

## 📚 Ressources

- [AWS App Runner Documentation](https://docs.aws.amazon.com/apprunner/)
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [AWS ECR Documentation](https://docs.aws.amazon.com/ecr/)
