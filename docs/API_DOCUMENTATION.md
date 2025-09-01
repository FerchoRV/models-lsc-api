# Documentación de la API de Reconocimiento LSC

## Información General

**Base URL**: `https://model-lsc-api-xxxxx-uc.a.run.app` (en producción)
**Versión**: 1.0
**Formato de Respuesta**: JSON
**Autenticación**: No requerida (público)

## Endpoints

### 1. Health Check

Verifica el estado de la API.

```http
GET /
```

**Respuesta Exitosa (200)**:
```json
"API de reconocimiento y generación de señas funcionando."
```

### 2. Reconocimiento de Alfabeto (Keypoints)

Procesa una secuencia de keypoints para reconocer letras del alfabeto LSC.

```http
POST /predict_recognition_alphabet
Content-Type: application/json
```

**Parámetros de Entrada**:
```json
{
  "keypoints": [
    [x1, y1, z1, x2, y2, z2, ...],  // Frame 1: 126 características (modo hands) o 258 (modo pose_hands)
    [x1, y1, z1, x2, y2, z2, ...],  // Frame 2
    ...                             // Hasta 30 frames
  ]
}
```

**Respuesta Exitosa (200)**:
```json
{
  "prediction": "A",
  "probabilities": [0.1, 0.8, 0.05, 0.02, ...]  // 27 probabilidades (una por letra)
}
```

**Códigos de Error**:
- `400`: Formato de datos incorrecto
- `500`: Error interno del servidor

### 3. Reconocimiento de Palabras V2 (Keypoints)

Procesa una secuencia de keypoints para reconocer palabras LSC.

```http
POST /predict_recognition_words_v2
Content-Type: application/json
```

**Parámetros de Entrada**:
```json
{
  "keypoints": [
    [x1, y1, z1, x2, y2, z2, ...],  // Frame 1: 126 características (modo hands) o 258 (modo pose_hands)
    [x1, y1, z1, x2, y2, z2, ...],  // Frame 2
    ...                             // Hasta 30 frames
  ]
}
```

**Respuesta Exitosa (200)**:
```json
{
  "prediction": "hola",
  "probabilities": [0.05, 0.8, 0.1, 0.02, ...]  // 28 probabilidades (una por palabra)
}
```

### 4. Reconocimiento de Alfabeto (Video)

Procesa un video completo para reconocer letras del alfabeto LSC.

```http
POST /predict_recognition_video_alphabet
Content-Type: application/json
```

**Parámetros de Entrada**:
```json
{
  "url_video": "https://ejemplo.com/video.mp4",
  "type_extract": "hands"  // "hands" o "pose_hands"
}
```

**Respuesta Exitosa (200)**:
```json
{
  "prediction": "B",
  "probabilities": [0.02, 0.85, 0.08, 0.03, ...]
}
```

### 5. Reconocimiento de Palabras V2 (Video)

Procesa un video completo para reconocer palabras LSC.

```http
POST /predict_recognition_video_words_v2
Content-Type: application/json
```

**Parámetros de Entrada**:
```json
{
  "url_video": "https://ejemplo.com/video.mp4",
  "type_extract": "pose_hands"  // "hands" o "pose_hands"
}
```

**Respuesta Exitosa (200)**:
```json
{
  "prediction": "gracias",
  "probabilities": [0.03, 0.1, 0.8, 0.05, ...]
}
```

## Especificaciones Técnicas

### Formato de Keypoints

#### Modo `hands` (126 características)
```
[LH_x1, LH_y1, LH_z1, LH_x2, LH_y2, LH_z2, ..., RH_x1, RH_y1, RH_z1, ...]
```
- 21 puntos por mano × 3 coordenadas × 2 manos = 126 valores
- Coordenadas normalizadas (0-1)

#### Modo `pose_hands` (258 características)
```
[POSE_x1, POSE_y1, POSE_z1, POSE_v1, ..., LH_x1, LH_y1, LH_z1, ..., RH_x1, RH_y1, RH_z1, ...]
```
- 33 puntos de pose × 4 coordenadas (x, y, z, visibility) = 132 valores
- 21 puntos por mano × 3 coordenadas × 2 manos = 126 valores
- Total: 258 valores

### Longitud de Secuencia

- **Requerida**: 30 frames
- **Videos más cortos**: Se aplica padding con ceros
- **Videos más largos**: Se aplica muestreo distribuido

### Clases de Salida

#### Alfabeto LSC (27 clases)
```
0: A, 1: B, 2: C, 3: D, 4: E, 5: F, 6: G, 7: H, 8: I, 9: J,
10: K, 11: L, 12: M, 13: N, 14: Ñ, 15: O, 16: P, 17: Q, 18: R,
19: S, 20: T, 21: U, 22: V, 23: W, 24: X, 25: Y, 26: Z
```

#### Palabras LSC V2 (28 clases)
```
0: sordo, 1: hola, 2: bien, 3: mal, 4: adios, 5: bienvenido,
6: gracias, 7: perdon, 8: permiso, 9: yo, 10: tu, 11: el,
12: ella, 13: nosotros, 14: usted, 15: ustedes, 16: que,
17: cuando, 18: donde, 19: como, 20: quien, 21: cuanto,
22: cual, 23: buenos dias, 24: buenas tardes, 25: buenas noches,
26: como estas, 27: por favor
```

## Ejemplos de Uso

### Ejemplo 1: Reconocimiento de Alfabeto con Keypoints

```bash
curl -X POST https://model-lsc-api-xxxxx-uc.a.run.app/predict_recognition_alphabet \
  -H "Content-Type: application/json" \
  -d '{
    "keypoints": [
      [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, ...],  // 126 valores para frame 1
      [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, ...],  // 126 valores para frame 2
      ...  // 28 frames más para completar 30
    ]
  }'
```

### Ejemplo 2: Reconocimiento de Palabras con Video

```bash
curl -X POST https://model-lsc-api-xxxxx-uc.a.run.app/predict_recognition_video_words_v2 \
  -H "Content-Type: application/json" \
  -d '{
    "url_video": "https://storage.googleapis.com/ejemplo/video_hola.mp4",
    "type_extract": "pose_hands"
  }'
```

### Ejemplo 3: JavaScript/Fetch

```javascript
const response = await fetch('https://model-lsc-api-xxxxx-uc.a.run.app/predict_recognition_alphabet', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    keypoints: keypointsArray  // Array de 30 frames × 126 características
  })
});

const result = await response.json();
console.log('Predicción:', result.prediction);
console.log('Probabilidades:', result.probabilities);
```

### Ejemplo 4: Python/Requests

```python
import requests
import json

url = "https://model-lsc-api-xxxxx-uc.a.run.app/predict_recognition_alphabet"
data = {
    "keypoints": keypoints_sequence  # Lista de 30 frames × 126 características
}

response = requests.post(url, json=data)
result = response.json()

print(f"Predicción: {result['prediction']}")
print(f"Confianza: {max(result['probabilities']):.2%}")
```

## Límites y Restricciones

### Límites de Tiempo
- **Keypoints**: < 5 segundos
- **Video**: < 30 segundos (dependiendo del tamaño)

### Límites de Tamaño
- **Video**: Máximo 50MB
- **URL de video**: Debe ser accesible públicamente

### Límites de Rate
- **Requests por minuto**: 100 (configurable)
- **Concurrencia**: 80 requests simultáneos

## Códigos de Error Detallados

### 400 Bad Request
```json
{
  "error": "La solicitud debe ser en formato JSON."
}
```

```json
{
  "error": "Falta el campo 'keypoints' en la solicitud."
}
```

```json
{
  "error": "Forma de la secuencia de keypoints incorrecta.",
  "expected_shape": [30, 126],
  "received_shape": [25, 126]
}
```

### 500 Internal Server Error
```json
{
  "error": "Modelo de reconocimiento no cargado."
}
```

```json
{
  "error": "No se pudieron extraer keypoints del video. El video podría estar vacío o inaccesible."
}
```

## Mejores Prácticas

### 1. Preprocesamiento de Keypoints
- Normalizar coordenadas a rango [0, 1]
- Asegurar longitud de secuencia de 30 frames
- Validar que no haya valores NaN o infinitos

### 2. Optimización de Videos
- Usar formatos compatibles (MP4, AVI, MOV)
- Resolución recomendada: 640x480 o superior
- Duración: 1-5 segundos para mejor precisión

### 3. Manejo de Errores
- Implementar retry logic para errores temporales
- Validar respuestas antes de procesar
- Logging de errores para debugging

### 4. Performance
- Usar conexiones persistentes (HTTP keep-alive)
- Implementar caching para requests repetidos
- Monitorear latencia y throughput

## Monitoreo y Métricas

### Métricas Recomendadas
- **Latencia promedio**: < 5s (keypoints), < 30s (video)
- **Tasa de éxito**: > 95%
- **Throughput**: Requests por segundo
- **Uso de memoria**: < 2GB

### Logs de Aplicación
La API registra automáticamente:
- Requests recibidos
- Errores de procesamiento
- Tiempo de respuesta
- Uso de recursos

## Soporte

Para soporte técnico o reportar problemas:
- **Documentación**: Este archivo
- **Issues**: [Repositorio del proyecto]
- **Email**: [Contacto del equipo]

---

**Última actualización**: [Fecha]
**Versión de la API**: 1.0
