# API de Reconocimiento de Lenguaje de Señas Colombiano (LSC)

## Descripción del Proyecto

Este proyecto implementa una API REST para el reconocimiento automático de señas del Lenguaje de Señas Colombiano (LSC) utilizando modelos de Machine Learning basados en TensorFlow/Keras. La API puede procesar tanto secuencias de keypoints extraídos de videos como videos completos para identificar señas del alfabeto y palabras comunes.

## Características Principales

- **Reconocimiento de Alfabeto LSC**: 27 letras (A-Z, Ñ)
- **Reconocimiento de Palabras LSC**: 28 palabras comunes
- **Procesamiento de Videos**: Extracción automática de keypoints usando MediaPipe
- **Múltiples Modos de Extracción**: 
  - `hands`: Solo puntos de las manos (126 características)
  - `pose_hands`: Puntos del cuerpo completo + manos (258 características)
- **Muestreo Distribuido**: Adaptación inteligente de secuencias de video de diferentes longitudes
- **API REST**: Endpoints para predicción directa y procesamiento de videos

## Arquitectura del Sistema

### Componentes Principales

1. **API Flask**: Servidor web para manejo de requests HTTP
2. **Modelos TensorFlow**: 
   - `actionAbecedario.h5`: Modelo para reconocimiento del alfabeto
   - `actionPalabrasV2.h5`: Modelo para reconocimiento de palabras
3. **MediaPipe**: Extracción de keypoints de poses y manos
4. **OpenCV**: Procesamiento de video
5. **Docker**: Containerización para despliegue

### Estructura de Datos

- **Secuencia de Entrada**: Array de keypoints por frame
- **Longitud de Secuencia**: 30 frames (configurable en `constants.py`)
- **Características por Frame**:
  - Modo `hands`: 126 características (21 puntos × 3 coordenadas × 2 manos)
  - Modo `pose_hands`: 258 características (33 puntos pose × 4 coordenadas + 42 puntos manos × 3 coordenadas)

## Instalación y Configuración

### Prerrequisitos

- Python 3.10.11
- Docker (para despliegue)
- Google Cloud SDK (para despliegue en GCP)
- Git

### Instalación Local

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
Asegúrate de que los archivos de modelo estén en la carpeta `models/`:
- `models/actionAbecedario.h5`
- `models/actionPalabrasV2.h5`

5. **Ejecutar la aplicación**:
```bash
python main.py
```

La API estará disponible en `http://localhost:5000`

### Configuración de Variables de Entorno

```bash
# Puerto de la aplicación (por defecto: 5000)
PORT=5000

# Configuración de CORS (ya configurado en el código)
# origins = ["http://localhost:3000", "https://www.colsign.com.co", "https://colsigns-app.vercel.app"]
```

## Uso de la API

### Endpoints Disponibles

#### 1. Health Check
```http
GET /
```
**Respuesta**: Mensaje de confirmación de funcionamiento

#### 2. Reconocimiento de Alfabeto (Keypoints)
```http
POST /predict_recognition_alphabet
Content-Type: application/json

{
  "keypoints": [[x1, y1, z1, ...], [x2, y2, z2, ...], ...]
}
```

#### 3. Reconocimiento de Palabras V2 (Keypoints)
```http
POST /predict_recognition_words_v2
Content-Type: application/json

{
  "keypoints": [[x1, y1, z1, ...], [x2, y2, z2, ...], ...]
}
```

#### 4. Reconocimiento de Alfabeto (Video)
```http
POST /predict_recognition_video_alphabet
Content-Type: application/json

{
  "url_video": "https://ejemplo.com/video.mp4",
  "type_extract": "hands"  // o "pose_hands"
}
```

#### 5. Reconocimiento de Palabras V2 (Video)
```http
POST /predict_recognition_video_words_v2
Content-Type: application/json

{
  "url_video": "https://ejemplo.com/video.mp4",
  "type_extract": "pose_hands"  // o "hands"
}
```

### Formato de Respuesta

```json
{
  "prediction": "A",
  "probabilities": [0.1, 0.8, 0.05, ...]
}
```

### Códigos de Error

- `400`: Error en el formato de la solicitud
- `500`: Error interno del servidor

## Despliegue en Google Cloud Platform (GCP)

### Prerrequisitos de GCP

1. **Proyecto GCP configurado**
2. **Google Cloud SDK instalado**
3. **Docker instalado**
4. **Servicios habilitados**:
   - Cloud Run
   - Artifact Registry

### Configuración del Proyecto

Edita el archivo `deploy-model-api.ps1` con tus configuraciones:

```powershell
$PROJECT_ID = "tu-proyecto-id"
$REGION = "us-central1"
$REPO_NAME = "model-api-repo"
$IMAGE_NAME = "model-lsc-api"
$SERVICE_NAME = "model-lsc-api"
```

### Despliegue Automático

1. **Autenticación**:
```bash
gcloud auth login
gcloud config set project tu-proyecto-id
```

2. **Ejecutar script de despliegue**:
```bash
# Windows PowerShell
.\deploy-model-api.ps1

# Linux/Mac (convertir a bash)
chmod +x deploy-model-api.sh
./deploy-model-api.sh
```

### Despliegue Manual

1. **Construir imagen Docker**:
```bash
docker build -t model-lsc-api .
```

2. **Etiquetar imagen**:
```bash
docker tag model-lsc-api:latest us-central1-docker.pkg.dev/tu-proyecto-id/model-api-repo/model-lsc-api:latest
```

3. **Subir a Artifact Registry**:
```bash
docker push us-central1-docker.pkg.dev/tu-proyecto-id/model-api-repo/model-lsc-api:latest
```

4. **Desplegar en Cloud Run**:
```bash
gcloud run deploy model-lsc-api \
  --image=us-central1-docker.pkg.dev/tu-proyecto-id/model-api-repo/model-lsc-api:latest \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated \
  --port=5000
```

### Configuración de Cloud Run

- **Memoria**: 2GB (recomendado para modelos ML)
- **CPU**: 1 vCPU
- **Concurrencia**: 80 requests simultáneos
- **Timeout**: 300 segundos (para procesamiento de video)

## Estructura del Proyecto

```
models-lsc-api/
├── main.py                 # Aplicación Flask principal
├── utils.py               # Utilidades para procesamiento de video
├── constants.py           # Constantes y configuraciones
├── tools.py              # Herramientas adicionales
├── requirements.txt      # Dependencias principales
├── requirements_full.txt # Dependencias completas
├── Dockerfile           # Configuración de Docker
├── deploy-model-api.ps1 # Script de despliegue (Windows)
├── deploy-model-api.sh  # Script de despliegue (Linux/Mac)
├── cloudbuild.yaml      # Configuración CI/CD
├── docker-compose.yml   # Configuración para desarrollo
├── env.example         # Variables de entorno de ejemplo
├── docs/               # 📚 Documentación completa
│   ├── INDEX.md        # Índice de documentación
│   ├── README.md       # Documentación principal
│   ├── API_DOCUMENTATION.md
│   ├── DEPLOYMENT_GUIDE.md
│   └── test_api.py
├── models/             # Modelos entrenados
│   ├── actionAbecedario.h5
│   └── actionPalabrasV2.h5
├── test/              # Archivos de prueba
│   ├── secuencia_r.json
│   └── secuencia_adios.json
└── datasets/          # Datasets de entrenamiento
```

## Modelos de Machine Learning

### Especificaciones Técnicas

- **Framework**: TensorFlow 2.17.0 / Keras 3.5.0
- **Arquitectura**: LSTM/CNN (dependiendo del modelo)
- **Entrada**: Secuencias de keypoints (30 frames × 126/258 características)
- **Salida**: Clasificación multiclase

### Alfabeto LSC (27 clases)
```
A, B, C, D, E, F, G, H, I, J, K, L, M, N, Ñ, O, P, Q, R, S, T, U, V, W, X, Y, Z
```

### Palabras LSC V2 (28 clases)
```
sordo, hola, bien, mal, adios, bienvenido, gracias, perdon, permiso,
yo, tu, el, ella, nosotros, usted, ustedes, que, cuando, donde,
como, quien, cuanto, cual, buenos dias, buenas tardes, buenas noches, 
como estas, por favor
```

## Procesamiento de Video

### Pipeline de Procesamiento

1. **Captura de Video**: OpenCV lee frames del video
2. **Detección MediaPipe**: Extracción de keypoints de pose y manos
3. **Normalización**: Conversión a formato estándar
4. **Muestreo**: Adaptación a longitud de secuencia requerida
5. **Predicción**: Inferencia del modelo
6. **Post-procesamiento**: Mapeo a etiquetas legibles

### Tipos de Extracción

#### Modo `hands` (126 características)
- 21 puntos por mano × 3 coordenadas (x, y, z) × 2 manos
- Ideal para señas que involucran principalmente las manos

#### Modo `pose_hands` (258 características)
- 33 puntos de pose × 4 coordenadas (x, y, z, visibility)
- 21 puntos por mano × 3 coordenadas × 2 manos
- Incluye contexto del cuerpo completo

## Monitoreo y Logs

### Logs de Aplicación

La aplicación registra:
- Carga de modelos
- Errores de predicción
- Información de procesamiento de video

### Métricas Recomendadas

- **Latencia de respuesta**: < 5 segundos para keypoints, < 30 segundos para video
- **Throughput**: Requests por segundo
- **Tasa de error**: Porcentaje de predicciones fallidas
- **Uso de recursos**: CPU, memoria, GPU

## Seguridad

### Configuraciones de Seguridad

- **CORS**: Configurado para dominios específicos
- **Validación de entrada**: Verificación de formato de datos
- **Manejo de errores**: Respuestas de error estructuradas
- **Autenticación**: Configurable según necesidades

### Recomendaciones

1. **HTTPS**: Usar siempre en producción
2. **Rate Limiting**: Implementar límites de requests
3. **Validación**: Verificar URLs de video y formatos de datos
4. **Logs**: Monitorear acceso y errores

## Mantenimiento

### Actualización de Modelos

1. **Entrenar nuevo modelo**
2. **Reemplazar archivo .h5 en models/**
3. **Actualizar constants.py si cambian las clases**
4. **Redesplegar aplicación**

### Backup y Recuperación

- **Modelos**: Backup de archivos .h5
- **Configuración**: Versionado en Git
- **Datos**: Backup de datasets de entrenamiento

## Troubleshooting

### Problemas Comunes

1. **Error de carga de modelo**:
   - Verificar que los archivos .h5 estén en models/
   - Verificar permisos de archivo

2. **Error de MediaPipe**:
   - Verificar instalación de dependencias
   - Verificar versión de OpenCV

3. **Error de memoria en Cloud Run**:
   - Aumentar memoria asignada
   - Optimizar carga de modelos

4. **Timeout en procesamiento de video**:
   - Aumentar timeout de Cloud Run
   - Optimizar algoritmo de procesamiento

### Logs de Debug

```python
# Habilitar logs detallados
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contribución

### Guías de Desarrollo

1. **Código**: Seguir PEP 8
2. **Documentación**: Actualizar README.md
3. **Testing**: Probar endpoints antes de commit
4. **Versionado**: Usar versionado semántico

### Proceso de Contribución

1. Fork del repositorio
2. Crear rama feature
3. Implementar cambios
4. Probar localmente
5. Crear Pull Request

## Licencia

[Especificar licencia del proyecto]

## Contacto

[Información de contacto del equipo de desarrollo]

---

**Nota**: Esta documentación está diseñada para desarrolladores y DevOps que necesiten desplegar y mantener la API de reconocimiento de LSC en entornos de producción.
