# CONFIGURACIÓN INICIAL
$PROJECT_ID = "Tu ID de proyecto en GCP"                # Cambia esto si tu ID real es otro
$REGION = "us-central1" # o la region que prefieras
$REPO_NAME = "Nombre de tu repositorio de Artifact Registry"
$IMAGE_NAME = "nombre de tu imagen Docker" # Por ejemplo, "model-lsc-api"
$SERVICE_NAME = "nombre de tu servicio en Cloud Run" # Por ejemplo, "mi-proyecto-api"
$PORT = 5000 # Puerto en el que tu aplicación escucha por defecto con flask

# LOGIN Y CONFIGURACIÓN
gcloud auth login
gcloud config set project $PROJECT_ID

# HABILITAR SERVICIOS NECESARIOS
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# CREAR EL REPOSITORIO DE ARTIFACTOS (si no existe ya)
gcloud artifacts repositories describe $REPO_NAME --location=$REGION 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Creando repositorio Artifact Registry..."
    gcloud artifacts repositories create $REPO_NAME `
        --repository-format=docker `
        --location=$REGION `
        --description="Repositorio Docker para modelos API"
} else {
    Write-Host "Repositorio ya existe. Continuando..."
}

# AUTENTICAR DOCKER CON ARTIFACT REGISTRY
gcloud auth configure-docker "$REGION-docker.pkg.dev"

# CONSTRUIR Y ETIQUETAR LA IMAGEN
docker build -t $IMAGE_NAME:latest .
docker tag $IMAGE_NAME:latest "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:latest"

# SUBIR LA IMAGEN
docker push "$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:latest"

# DESPLEGAR EN CLOUD RUN
gcloud run deploy $SERVICE_NAME `
  --image="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/$IMAGE_NAME:latest" `
  --platform=managed `
  --region=$REGION `
  --allow-unauthenticated `
  --port=$PORT
