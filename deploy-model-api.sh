#!/bin/bash

# CONFIGURACIÓN INICIAL
PROJECT_ID="id-proyecto-gcp"                # Cambia esto si tu ID real es otro
REGION="us-central1"
REPO_NAME="model-api-repo"
IMAGE_NAME="model-lsc-api"
SERVICE_NAME="model-lsc-api"
PORT=5000

# LOGIN Y CONFIGURACIÓN
echo "Iniciando proceso de despliegue..."
gcloud auth login
gcloud config set project $PROJECT_ID

# HABILITAR SERVICIOS NECESARIOS
echo "Habilitando servicios de GCP..."
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# CREAR EL REPOSITORIO DE ARTIFACTOS (si no existe ya)
echo "Verificando repositorio Artifact Registry..."
if ! gcloud artifacts repositories describe $REPO_NAME --location=$REGION 2>/dev/null; then
    echo "Creando repositorio Artifact Registry..."
    gcloud artifacts repositories create $REPO_NAME \
        --repository-format=docker \
        --location=$REGION \
        --description="Repositorio Docker para modelos API"
else
    echo "Repositorio ya existe. Continuando..."
fi

# AUTENTICAR DOCKER CON ARTIFACT REGISTRY
echo "Configurando autenticación de Docker..."
gcloud auth configure-docker "$REGION-docker.pkg.dev"

# CONSTRUIR Y ETIQUETAR LA IMAGEN
echo "Construyendo imagen Docker..."
docker build -t $IMAGE_NAME:latest .

echo "Etiquetando imagen..."
docker tag $IMAGE_NAME:latest "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:latest"

# SUBIR LA IMAGEN
echo "Subiendo imagen a Artifact Registry..."
docker push "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:latest"

# DESPLEGAR EN CLOUD RUN
echo "Desplegando en Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:latest" \
  --platform=managed \
  --region=$REGION \
  --allow-unauthenticated \
  --port=$PORT \
  --memory=2Gi \
  --cpu=1 \
  --timeout=300 \
  --concurrency=80

echo "Despliegue completado exitosamente!"
echo "URL del servicio: $(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')"
