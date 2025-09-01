# API de Reconocimiento de Lenguaje de Señas Colombiano (LSC)

## 📖 Descripción

Este proyecto implementa una API REST para el reconocimiento automático de señas del Lenguaje de Señas Colombiano (LSC) utilizando modelos de Machine Learning basados en TensorFlow/Keras.

## 🚀 Inicio Rápido

### Prerrequisitos
- Python 3.10.11
- Docker (opcional)
- Google Cloud SDK (para despliegue)

### Instalación Local
```bash
# Clonar el repositorio
git clone <repository-url>
cd models-lsc-api

# Crear entorno virtual
python -m venv _env
_env\Scripts\activate  # Windows
# source _env/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python main.py
```

La API estará disponible en `http://localhost:5000`

## 📚 Documentación

Toda la documentación detallada se encuentra en la carpeta [`docs/`](./docs/):

- **[📋 README Completo](./docs/README.md)** - Documentación principal del proyecto
- **[🔌 Documentación de la API](./docs/API_DOCUMENTATION.md)** - Endpoints, ejemplos y especificaciones técnicas
- **[🚀 Guía de Despliegue](./docs/DEPLOYMENT_GUIDE.md)** - Instrucciones para desplegar en diferentes entornos
- **[🧪 Script de Testing](./docs/test_api.py)** - Herramientas para validar la API

## 🏗️ Arquitectura

- **API Flask** con 5 endpoints principales
- **2 modelos de ML** (alfabeto y palabras LSC)
- **Procesamiento de video** con MediaPipe
- **Containerización** con Docker
- **Despliegue** en Google Cloud Platform

## 🎯 Características

- **Reconocimiento de Alfabeto LSC**: 27 letras (A-Z, Ñ)
- **Reconocimiento de Palabras LSC**: 28 palabras comunes
- **Procesamiento de Videos**: Extracción automática de keypoints
- **Múltiples Modos**: `hands` (126 características) y `pose_hands` (258 características)
- **Muestreo Distribuido**: Adaptación inteligente de secuencias de video

## 🔧 Endpoints Principales

- `GET /` - Health check
- `POST /predict_recognition_alphabet` - Reconocimiento de alfabeto
- `POST /predict_recognition_words_v2` - Reconocimiento de palabras
- `POST /predict_recognition_video_alphabet` - Reconocimiento de alfabeto con video
- `POST /predict_recognition_video_words_v2` - Reconocimiento de palabras con video

## 🚀 Despliegue

### Despliegue Local con Docker
```bash
docker build -t model-lsc-api .
docker run -p 5000:5000 model-lsc-api
```

### Despliegue en GCP
```bash
# Windows
.\deploy-model-api.ps1

# Linux/Mac
chmod +x deploy-model-api.sh
./deploy-model-api.sh
```

## 📁 Estructura del Proyecto

```
models-lsc-api/
├── main.py                 # Aplicación Flask principal
├── utils.py               # Utilidades para procesamiento de video
├── constants.py           # Constantes y configuraciones
├── requirements.txt      # Dependencias principales
├── Dockerfile           # Configuración de Docker
├── deploy-model-api.ps1 # Script de despliegue (Windows)
├── deploy-model-api.sh  # Script de despliegue (Linux/Mac)
├── cloudbuild.yaml      # Configuración CI/CD
├── docker-compose.yml   # Configuración para desarrollo
├── env.example         # Variables de entorno de ejemplo
├── docs/               # 📚 Documentación completa
│   ├── README.md
│   ├── API_DOCUMENTATION.md
│   ├── DEPLOYMENT_GUIDE.md
│   └── test_api.py
├── models/             # Modelos entrenados
│   ├── actionAbecedario.h5
│   └── actionPalabrasV2.h5
├── test/              # Archivos de prueba
└── datasets/         # Datasets de entrenamiento
```

## 🧪 Testing

Ejecutar el script de testing:
```bash
python docs/test_api.py
# o para una URL específica
python docs/test_api.py --url https://tu-api-url.com
```

## 📊 Especificaciones Técnicas

- **Framework**: TensorFlow 2.17.0 / Keras 3.5.0
- **API**: Flask 3.1.1
- **Procesamiento**: MediaPipe + OpenCV
- **Containerización**: Docker
- **Despliegue**: Google Cloud Run
- **Memoria**: 2GB (recomendado)
- **Timeout**: 300 segundos

## 🤝 Contribución

1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

[Especificar licencia del proyecto]

## 📞 Contacto

[Información de contacto del equipo de desarrollo]

---

**💡 Tip**: Para obtener información detallada sobre cualquier aspecto del proyecto, consulta la documentación en la carpeta [`docs/`](./docs/).
