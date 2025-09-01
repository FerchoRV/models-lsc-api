# Guía de Despliegue - API de Reconocimiento LSC

## Índice

1. [Despliegue Local](#despliegue-local)
2. [Despliegue en Docker](#despliegue-en-docker)
3. [Despliegue en Google Cloud Platform](#despliegue-en-google-cloud-platform)
4. [Despliegue con Cloud Build](#despliegue-con-cloud-build)
5. [Configuración de Producción](#configuración-de-producción)
6. [Monitoreo y Logs](#monitoreo-y-logs)
7. [Troubleshooting](#troubleshooting)

## Despliegue Local

### Prerrequisitos

- Python 3.10.11
- pip
- Git

### Pasos de Instalación

1. **Clonar el repositorio**:
```bash
git clone <repository-url>
cd models-lsc-api
```

2. **Crear entorno virtual**:
```bash
python -m venv _env

# Windows
_env\Scripts\activate

# Linux/Mac
source _env/bin/activate
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

4. **Verificar modelos**:
```bash
ls models/
# Debe mostrar:
# actionAbecedario.h5
# actionPalabrasV2.h5
```

5. **Ejecutar aplicación**:
```bash
python main.py
```

6. **Verificar funcionamiento**:
```bash
curl http://localhost:5000/
# Debe responder: "API de reconocimiento y generación de señas funcionando."
```

### Configuración de Desarrollo

Crear archivo `.env` basado en `env.example`:
```bash
cp env.example .env
```

Editar `.env` según necesidades:
```env
PORT=5000
FLASK_ENV=development
FLASK_DEBUG=True
LOG_LEVEL=DEBUG
```

## Despliegue en Docker

### Despliegue Local con Docker

1. **Construir imagen**:
```bash
docker build -t model-lsc-api .
```

2. **Ejecutar contenedor**:
```bash
docker run -p 5000:5000 model-lsc-api
```

3. **Verificar funcionamiento**:
```bash
curl http://localhost:5000/
```

### Despliegue con Docker Compose

1. **Ejecutar con docker-compose**:
```bash
docker-compose up -d
```

2. **Ver logs**:
```bash
docker-compose logs -f model-lsc-api
```

3. **Detener servicios**:
```bash
docker-compose down
```

### Configuración de Docker

El `Dockerfile` incluye:
- Python 3.10.11-slim como base
- Dependencias del sistema para OpenCV
- Instalación de dependencias Python
- Exposición del puerto 5000
- Comando de ejecución

## Despliegue en Google Cloud Platform

### Prerrequisitos de GCP

1. **Cuenta de GCP activa**
2. **Google Cloud SDK instalado**
3. **Docker instalado**
4. **Proyecto GCP creado**

### Configuración Inicial

1. **Instalar Google Cloud SDK**:
```bash
# Windows
# Descargar desde: https://cloud.google.com/sdk/docs/install

# Linux/Mac
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

2. **Autenticación**:
```bash
gcloud auth login
gcloud config set project tu-proyecto-id
```

3. **Habilitar servicios**:
```bash
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### Despliegue Automático

#### Windows (PowerShell)

1. **Editar configuración**:
```powershell
# Editar deploy-model-api.ps1
$PROJECT_ID = "tu-proyecto-id"
$REGION = "us-central1"
```

2. **Ejecutar despliegue**:
```powershell
.\deploy-model-api.ps1
```

#### Linux/Mac (Bash)

1. **Dar permisos de ejecución**:
```bash
chmod +x deploy-model-api.sh
```

2. **Editar configuración**:
```bash
# Editar deploy-model-api.sh
PROJECT_ID="tu-proyecto-id"
REGION="us-central1"
```

3. **Ejecutar despliegue**:
```bash
./deploy-model-api.sh
```

### Despliegue Manual

1. **Crear repositorio Artifact Registry**:
```bash
gcloud artifacts repositories create model-api-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="Repositorio Docker para modelos API"
```

2. **Configurar autenticación Docker**:
```bash
gcloud auth configure-docker us-central1-docker.pkg.dev
```

3. **Construir y etiquetar imagen**:
```bash
docker build -t model-lsc-api .
docker tag model-lsc-api:latest us-central1-docker.pkg.dev/tu-proyecto-id/model-api-repo/model-lsc-api:latest
```

4. **Subir imagen**:
```bash
docker push us-central1-docker.pkg.dev/tu-proyecto-id/model-api-repo/model-lsc-api:latest
```

5. **Desplegar en Cloud Run**:
```bash
gcloud run deploy model-lsc-api \
  --image=us-central1-docker.pkg.dev/tu-proyecto-id/model-api-repo/model-lsc-api:latest \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated \
  --port=5000 \
  --memory=2Gi \
  --cpu=1 \
  --timeout=300 \
  --concurrency=80
```

## Despliegue con Cloud Build

### Configuración de Cloud Build

1. **Habilitar Cloud Build**:
```bash
gcloud services enable cloudbuild.googleapis.com
```

2. **Configurar permisos**:
```bash
gcloud projects add-iam-policy-binding tu-proyecto-id \
  --member="serviceAccount:tu-proyecto-id@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding tu-proyecto-id \
  --member="serviceAccount:tu-proyecto-id@cloudbuild.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

3. **Configurar trigger (opcional)**:
```bash
gcloud builds triggers create github \
  --repo-name=tu-repositorio \
  --repo-owner=tu-usuario \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml
```

### Despliegue Automático

1. **Push a main branch**:
```bash
git add .
git commit -m "Actualización de API"
git push origin main
```

2. **Verificar build**:
```bash
gcloud builds list --limit=5
```

3. **Verificar despliegue**:
```bash
gcloud run services list --region=us-central1
```

## Configuración de Producción

### Variables de Entorno de Producción

```env
PORT=5000
FLASK_ENV=production
FLASK_DEBUG=False
LOG_LEVEL=INFO
GCP_PROJECT_ID=tu-proyecto-id
GCP_REGION=us-central1
```

### Configuración de Cloud Run

```bash
gcloud run services update model-lsc-api \
  --region=us-central1 \
  --memory=2Gi \
  --cpu=1 \
  --timeout=300 \
  --concurrency=80 \
  --max-instances=10 \
  --min-instances=0
```

### Configuración de Seguridad

1. **HTTPS obligatorio**:
```bash
gcloud run services update model-lsc-api \
  --region=us-central1 \
  --no-allow-unauthenticated
```

2. **Configurar autenticación**:
```bash
# Crear service account
gcloud iam service-accounts create api-service \
  --display-name="API Service Account"

# Asignar roles
gcloud projects add-iam-policy-binding tu-proyecto-id \
  --member="serviceAccount:api-service@tu-proyecto-id.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```

### Configuración de Monitoreo

1. **Habilitar Cloud Monitoring**:
```bash
gcloud services enable monitoring.googleapis.com
```

2. **Configurar alertas**:
```bash
# Crear política de alertas para latencia alta
gcloud alpha monitoring policies create \
  --policy-from-file=alerting-policy.yaml
```

## Monitoreo y Logs

### Ver Logs de Cloud Run

```bash
# Logs en tiempo real
gcloud run services logs tail model-lsc-api --region=us-central1

# Logs históricos
gcloud run services logs read model-lsc-api --region=us-central1 --limit=50
```

### Métricas de Cloud Run

```bash
# Ver métricas del servicio
gcloud run services describe model-lsc-api --region=us-central1

# Ver uso de recursos
gcloud run services list --region=us-central1 --format="table(name,status.url,status.conditions[0].status)"
```

### Configuración de Logging

Agregar al código para logging estructurado:

```python
import logging
import json

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Ejemplo de log estructurado
logger.info("Request processed", extra={
    "endpoint": "/predict_recognition_alphabet",
    "processing_time": 1.23,
    "prediction": "A"
})
```

## Troubleshooting

### Problemas Comunes

#### 1. Error de Memoria

**Síntoma**: `MemoryError` o timeout en Cloud Run

**Solución**:
```bash
gcloud run services update model-lsc-api \
  --region=us-central1 \
  --memory=4Gi
```

#### 2. Error de Carga de Modelo

**Síntoma**: `Modelo de reconocimiento no cargado`

**Solución**:
- Verificar que los archivos .h5 estén en la imagen Docker
- Verificar permisos de archivo
- Revisar logs de construcción

#### 3. Error de MediaPipe

**Síntoma**: `MediaPipe no está disponible`

**Solución**:
- Verificar instalación de dependencias
- Actualizar versión de OpenCV
- Verificar compatibilidad de versiones

#### 4. Timeout en Procesamiento de Video

**Síntoma**: Timeout después de 300 segundos

**Solución**:
```bash
gcloud run services update model-lsc-api \
  --region=us-central1 \
  --timeout=600
```

#### 5. Error de Autenticación Docker

**Síntoma**: `denied: access denied`

**Solución**:
```bash
gcloud auth configure-docker us-central1-docker.pkg.dev
gcloud auth login
```

### Comandos de Diagnóstico

```bash
# Verificar estado del servicio
gcloud run services describe model-lsc-api --region=us-central1

# Ver logs de errores
gcloud run services logs read model-lsc-api --region=us-central1 --filter="severity>=ERROR"

# Verificar conectividad
curl -v https://model-lsc-api-xxxxx-uc.a.run.app/

# Verificar uso de recursos
gcloud run services list --region=us-central1 --format="table(name,status.url,status.conditions[0].status,status.conditions[0].message)"
```

### Rollback de Versión

```bash
# Listar revisiones
gcloud run revisions list --service=model-lsc-api --region=us-central1

# Rollback a versión anterior
gcloud run services update-traffic model-lsc-api \
  --region=us-central1 \
  --to-revisions=REVISION_NAME=100
```

## Optimización de Performance

### Configuración Recomendada

```bash
gcloud run services update model-lsc-api \
  --region=us-central1 \
  --memory=2Gi \
  --cpu=1 \
  --timeout=300 \
  --concurrency=80 \
  --max-instances=10 \
  --min-instances=1
```

### Monitoreo de Performance

```bash
# Ver métricas de latencia
gcloud run services describe model-lsc-api --region=us-central1 --format="value(status.conditions[0].message)"

# Ver uso de CPU y memoria
gcloud run services list --region=us-central1 --format="table(name,status.url,status.conditions[0].status)"
```

---

**Nota**: Esta guía cubre los escenarios más comunes de despliegue. Para casos específicos o problemas únicos, consultar la documentación oficial de Google Cloud Platform.
