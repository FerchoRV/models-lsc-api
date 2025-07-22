# main.py
import os
import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify
from tensorflow.keras.models import load_model
import constants
from utils import process_video_sign
from flask_cors import CORS # Importa la extensión CORS

app = Flask(__name__)

origins = ["http://localhost:3000", "https://www.colsign.com.co", "https://colsigns-app.vercel.app"]
CORS(app, origins=origins)

# Rutas de los modelos (ajusta si tus modelos están en otro lugar)
# Cloud Run buscará estos archivos en la misma carpeta que main.py
MODEL_RECOGNITION_ABECEDARIO_PATH = './models/actionAbecedario.h5'
MODEL_RECOGNITION_PALABRASV2_PATH = './models/actionPalabrasV2.h5'


# Carga de modelos (se cargarán una vez al iniciar la aplicación)
# Usamos un bloque try-except para manejar errores si los modelos no se encuentran
try:
    # Modelo de reconocimiento de señas (entrada: keypoints, salida: etiqueta de seña)
    print(f"Cargando el modelo de reconocimiento abecedario desde: {MODEL_RECOGNITION_ABECEDARIO_PATH}")
    model_recognition_abcedario = load_model(MODEL_RECOGNITION_ABECEDARIO_PATH, compile=False) # compile=False si no vas a reentrenar
    # Compilar el modelo si necesitas usarlo para inferencia después de cargarlo sin compile=True
    # model_recognition.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    print("Modelo de reconocimiento para abecedario cargado exitosamente.")   

    # Modelo de reconocimiento de señas (entrada: keypoints, salida: etiqueta de seña)
    print(f"Cargando el modelo de reconocimiento palabras V2 desde: {MODEL_RECOGNITION_PALABRASV2_PATH}")
    model_recognition_palabrasv2 = load_model(MODEL_RECOGNITION_PALABRASV2_PATH, compile=False) # compile=False si no vas a reentrenar
    # Compilar el modelo si necesitas usarlo para inferencia después de cargarlo sin compile=True
    # model_recognition.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    print("Modelo de reconocimiento para palabras V2 cargado exitosamente.")

except Exception as e:
    print(f"Error al cargar uno o ambos modelos: {e}")
    model_recognition_abcedario = None
    model_recognition_palabrasv2 = None
    # En un entorno de producción, aquí podrías querer que la aplicación falle
    # o que el endpoint de salud (health check) falle para que Cloud Run no dirija tráfico.

# Define el número de clases de salida para el modelo de reconocimiento
# DEBES AJUSTAR ESTO AL NÚMERO REAL DE SEÑAS EN TU ENTRENAMIENTO
# Por ejemplo, si tienes 28 señas, sería 28. Si tienes 500, sería 500.
NUM_SIGN_CLASSES_alphabet = len(constants.signs_abc) # Reemplaza con tu número real de clases (acciones.shape[0])
NUM_SIGN_CLASSES_wordsv2 = len(constants.signs_wordsV2) # Reemplaza con tu número real de clases (acciones.shape[0])

# Opcional: Define una lista de etiquetas de señas para mapear las predicciones numéricas
# Esto es útil para devolver nombres legibles en lugar de solo números.
# Asegúrate de que el índice corresponda a la salida de tu modelo.
SIGN_LABELS_alphabet = constants.signs_abc
SIGN_LABELS_wordsv2 = constants.signs_wordsV2 # Ejemplo: seña_0, seña_1, ...
# Si tienes tus etiquetas reales:
# SIGN_LABELS = ["hola", "gracias", "adios", ...] # Reemplaza con tus etiquetas reales

@app.route('/predict_recognition_alphabet', methods=['POST'])
def predict_recognition_alphabet():
    """
    Endpoint para el reconocimiento de señas.
    Recibe una secuencia de puntos de control y devuelve la seña predicha.
    """
    if model_recognition_abcedario is None:
        return jsonify({"error": "Modelo de reconocimiento no cargado."}), 500

    if not request.is_json:
        return jsonify({"error": "La solicitud debe ser en formato JSON."}), 400

    data = request.get_json()
    keypoints_sequence = data.get('keypoints')

    if keypoints_sequence is None:
        return jsonify({"error": "Falta el campo 'keypoints' en la solicitud."}), 400

    try:
        # Convertir la lista de Python a un array NumPy
        # Asegúrate de que el formato de los keypoints sea consistente (ej. [frame1_flat_array, frame2_flat_array, ...])
        # Y que la longitud de la secuencia coincida con la entrada del modelo.
        input_data = np.array(keypoints_sequence, dtype=np.float32)

        # Verificar y ajustar la forma del array
        # El modelo espera (1, SEQUENCE_LENGTH, 258)
        # Asumimos que SEQUENCE_LENGTH es la longitud esperada por tu modelo (30 o 60)
        # La dimensión de las características por fotograma es 258 (x,y,z para 86 keypoints, o 258 si es X,Y,Z para cada keypoint)
        # Ajusta `expected_sequence_length` según la longitud que estés usando en tu entrenamiento (30 o 60)
        expected_sequence_length = model_recognition_abcedario.input_shape[1] # Obtiene la longitud de secuencia del modelo
        expected_feature_dim = model_recognition_abcedario.input_shape[2] # Obtiene la dimensión de las características (258)

        if input_data.shape[0] != expected_sequence_length or input_data.shape[1] != expected_feature_dim:
            # Aquí puedes implementar padding/truncation si es necesario,
            # o simplemente rechazar la solicitud con un error.
            return jsonify({
                "error": "Forma de la secuencia de keypoints incorrecta.",
                "expected_shape": (expected_sequence_length, expected_feature_dim),
                "received_shape": input_data.shape
            }), 400
        
        # Añadir la dimensión del batch (1 para una única inferencia)
        input_data = np.expand_dims(input_data, axis=0) # Ahora la forma es (1, SEQUENCE_LENGTH, 258)

        # Realizar la predicción
        predictions = model_recognition_abcedario.predict(input_data)

        # Obtener la clase predicha (el índice con la probabilidad más alta)
        predicted_class_index = np.argmax(predictions, axis=1)[0]
        
        # Mapear el índice a una etiqueta legible
        predicted_sign_label = SIGN_LABELS_alphabet[predicted_class_index] if predicted_class_index < len(SIGN_LABELS_alphabet) else f"clase_desconocida_{predicted_class_index}"

        # Devolver la predicción y las probabilidades
        return jsonify({
            "prediction": predicted_sign_label,
            "probabilities": predictions[0].tolist() # Convertir a lista para JSON
        })

    except Exception as e:
        print(f"Error durante la inferencia de reconocimiento: {e}")
        return jsonify({"error": f"Error interno del servidor durante la predicción: {str(e)}"}), 500

@app.route('/predict_recognition_words_v2', methods=['POST'])
def predict_recognition_words_v2():
    """
    Endpoint para el reconocimiento de señas.
    Recibe una secuencia de puntos de control y devuelve la seña predicha.
    """
    if model_recognition_palabrasv2 is None:
        return jsonify({"error": "Modelo de reconocimiento de palabras V2 no cargado."}), 500

    if not request.is_json:
        return jsonify({"error": "La solicitud debe ser en formato JSON."}), 400

    data = request.get_json()
    keypoints_sequence = data.get('keypoints')

    if keypoints_sequence is None:
        return jsonify({"error": "Falta el campo 'keypoints' en la solicitud."}), 400

    try:
        # Convertir la lista de Python a un array NumPy
        # Asegúrate de que el formato de los keypoints sea consistente (ej. [frame1_flat_array, frame2_flat_array, ...])
        # Y que la longitud de la secuencia coincida con la entrada del modelo.
        input_data = np.array(keypoints_sequence, dtype=np.float32)

        # Verificar y ajustar la forma del array
        # El modelo espera (1, SEQUENCE_LENGTH, 258)
        # Asumimos que SEQUENCE_LENGTH es la longitud esperada por tu modelo (30 o 60)
        # La dimensión de las características por fotograma es 258 (x,y,z para 86 keypoints, o 258 si es X,Y,Z para cada keypoint)
        # Ajusta `expected_sequence_length` según la longitud que estés usando en tu entrenamiento (30 o 60)
        expected_sequence_length = model_recognition_palabrasv2.input_shape[1] # Obtiene la longitud de secuencia del modelo
        expected_feature_dim = model_recognition_palabrasv2.input_shape[2] # Obtiene la dimensión de las características (258)

        if input_data.shape[0] != expected_sequence_length or input_data.shape[1] != expected_feature_dim:
            # Aquí puedes implementar padding/truncation si es necesario,
            # o simplemente rechazar la solicitud con un error.
            return jsonify({
                "error": "Forma de la secuencia de keypoints incorrecta.",
                "expected_shape": (expected_sequence_length, expected_feature_dim),
                "received_shape": input_data.shape
            }), 400
        
        # Añadir la dimensión del batch (1 para una única inferencia)
        input_data = np.expand_dims(input_data, axis=0) # Ahora la forma es (1, SEQUENCE_LENGTH, 258)

        # Realizar la predicción
        predictions = model_recognition_palabrasv2.predict(input_data)

        # Obtener la clase predicha (el índice con la probabilidad más alta)
        predicted_class_index = np.argmax(predictions, axis=1)[0]
        
        # Mapear el índice a una etiqueta legible
        predicted_sign_label = SIGN_LABELS_wordsv2[predicted_class_index] if predicted_class_index < len(SIGN_LABELS_wordsv2) else f"clase_desconocida_{predicted_class_index}"

        # Devolver la predicción y las probabilidades
        return jsonify({
            "prediction": predicted_sign_label,
            "probabilities": predictions[0].tolist() # Convertir a lista para JSON
        })

    except Exception as e:
        print(f"Error durante la inferencia de reconocimiento: {e}")
        return jsonify({"error": f"Error interno del servidor durante la predicción: {str(e)}"}), 500

@app.route('/predict_recognition_video_alphabet', methods=['POST'])
def predict_recognition_video__alphabet():
    """
    Endpoint para el reconocimiento de señas mediante procesamiento de videos.
    Recibe una URL de video y devuelve la seña predicha utilizando muestreo distribuido.
    """
    if model_recognition_abcedario is None:
        return jsonify({"error": "Modelo de reconocimiento no cargado."}), 500

    if not request.is_json:
        return jsonify({"error": "La solicitud debe ser en formato JSON."}), 400

    data = request.get_json()
    url_video = data.get('url_video')
    type_extract = data.get('type_extract', 'hands')  # Por defecto, extrae keypoints de las manos

    if url_video is None:
        return jsonify({"error": "Falta el campo 'url_video' en la solicitud."}), 400
    if type_extract not in ['hands', 'pose_hands']:
        return jsonify({"error": "El campo 'type_extract' debe ser 'hands' o 'pose_hands'."}), 400

    try:
        # 1. Obtener la longitud de secuencia y la dimensión de características esperada por el modelo
        expected_sequence_length = model_recognition_abcedario.input_shape[1]
        expected_feature_dim = model_recognition_abcedario.input_shape[2]

        # 2. Procesar el video y extraer TODOS los keypoints disponibles
        # La función process_video_sign permanece inalterada y retorna todos los keypoints.
        all_extracted_keypoints = process_video_sign(type_extract, url_video)

        if all_extracted_keypoints is None or len(all_extracted_keypoints) == 0:
            return jsonify({"error": "No se pudieron extraer keypoints del video. El video podría estar vacío o inaccesible."}), 400

        # --- Lógica de Muestreo Distribuido (dentro del endpoint) ---
        total_frames_extracted = len(all_extracted_keypoints)
        final_sequence_for_model = []

        if total_frames_extracted <= expected_sequence_length:
            # Si el video es más corto o igual a la longitud esperada:
            # Usar todos los fotogramas y rellenar con ceros si es necesario (padding).
            final_sequence_for_model = all_extracted_keypoints
            if total_frames_extracted < expected_sequence_length:
                # Determinar la dimensión de la característica a partir del primer keypoint extraído
                # Esto es seguro porque ya verificamos que all_extracted_keypoints no está vacío.
                feature_dim = len(all_extracted_keypoints[0]) 
                padding_needed = expected_sequence_length - total_frames_extracted
                padding_array = np.zeros((padding_needed, feature_dim), dtype=np.float32)
                final_sequence_for_model.extend(padding_array.tolist()) # Añadir el padding
        else:
            # Si el video es más largo:
            # Seleccionar 'expected_sequence_length' fotogramas distribuidos uniformemente (muestreo distribuido/truncamiento inteligente).
            indices = np.linspace(0, total_frames_extracted - 1, expected_sequence_length).astype(int)
            final_sequence_for_model = [all_extracted_keypoints[i] for i in indices]

        # Convertir la lista de Python a un array NumPy
        input_data = np.array(final_sequence_for_model, dtype=np.float32)

        # Verificar y ajustar la forma del array (esta verificación ahora es más para asegurar que la lógica funcionó)
        if input_data.shape[0] != expected_sequence_length or input_data.shape[1] != expected_feature_dim:
            # Este error debería ser raro si la lógica de muestreo es correcta
            return jsonify({
                "error": "Error interno: La forma final de la secuencia de keypoints es incorrecta después del muestreo.",
                "expected_shape": (expected_sequence_length, expected_feature_dim),
                "received_shape": input_data.shape
            }), 500
        
        # Añadir la dimensión del batch (1 para una única inferencia)
        input_data = np.expand_dims(input_data, axis=0) # Ahora la forma es (1, SEQUENCE_LENGTH, 258)

        # Realizar la predicción
        predictions = model_recognition_abcedario.predict(input_data)

        # Obtener la clase predicha (el índice con la probabilidad más alta)
        predicted_class_index = np.argmax(predictions, axis=1)[0]
        
        # Mapear el índice a una etiqueta legible
        predicted_sign_label = SIGN_LABELS_alphabet[predicted_class_index] if predicted_class_index < len(SIGN_LABELS_alphabet) else f"clase_desconocida_{predicted_class_index}"

        # Devolver la predicción y las probabilidades
        return jsonify({
            "prediction": predicted_sign_label,
            "probabilities": predictions[0].tolist() # Convertir a lista para JSON
        })

    except Exception as e:
        print(f"Error durante la inferencia de reconocimiento: {e}")
        return jsonify({"error": f"Error interno del servidor durante la predicción: {str(e)}"}), 500

@app.route('/predict_recognition_video_words_v2', methods=['POST'])
def predict_recognition_video_words_v2():
    """
    Endpoint para el reconocimiento de señas mediante procesamiento de videos.
    Recibe una URL de video y devuelve la seña predicha utilizando muestreo distribuido.
    """
    if model_recognition_palabrasv2 is None:
        return jsonify({"error": "Modelo de reconocimiento de palabras V2 no cargado."}), 500

    if not request.is_json:
        return jsonify({"error": "La solicitud debe ser en formato JSON."}), 400

    data = request.get_json()
    url_video = data.get('url_video')
    type_extract = data.get('type_extract', 'pose_hands')
    
    if url_video is None:
        return jsonify({"error": "Falta el campo 'url_video' en la solicitud."}), 400
    if type_extract not in ['hands', 'pose_hands']:
        return jsonify({"error": "El campo 'type_extract' debe ser 'hands' o 'pose_hands'."}), 400
    try:
        # 1. Obtener la longitud de secuencia y la dimensión de características esperada por el modelo
        expected_sequence_length = model_recognition_palabrasv2.input_shape[1]
        expected_feature_dim = model_recognition_palabrasv2.input_shape[2]

        # 2. Procesar el video y extraer TODOS los keypoints disponibles
        # La función process_video_sign permanece inalterada y retorna todos los keypoints.
        all_extracted_keypoints = process_video_sign(type_extract, url_video)

        if all_extracted_keypoints is None or len(all_extracted_keypoints) == 0:
            return jsonify({"error": "No se pudieron extraer keypoints del video. El video podría estar vacío o inaccesible."}), 400

        # --- Lógica de Muestreo Distribuido (dentro del endpoint) ---
        total_frames_extracted = len(all_extracted_keypoints)
        final_sequence_for_model = []

        if total_frames_extracted <= expected_sequence_length:
            # Si el video es más corto o igual a la longitud esperada:
            # Usar todos los fotogramas y rellenar con ceros si es necesario (padding).
            final_sequence_for_model = all_extracted_keypoints
            if total_frames_extracted < expected_sequence_length:
                # Determinar la dimensión de la característica a partir del primer keypoint extraído
                # Esto es seguro porque ya verificamos que all_extracted_keypoints no está vacío.
                feature_dim = len(all_extracted_keypoints[0]) 
                padding_needed = expected_sequence_length - total_frames_extracted
                padding_array = np.zeros((padding_needed, feature_dim), dtype=np.float32)
                final_sequence_for_model.extend(padding_array.tolist()) # Añadir el padding
        else:
            # Si el video es más largo:
            # Seleccionar 'expected_sequence_length' fotogramas distribuidos uniformemente (muestreo distribuido/truncamiento inteligente).
            indices = np.linspace(0, total_frames_extracted - 1, expected_sequence_length).astype(int)
            final_sequence_for_model = [all_extracted_keypoints[i] for i in indices]

        # Convertir la lista de Python a un array NumPy
        input_data = np.array(final_sequence_for_model, dtype=np.float32)

        # Verificar y ajustar la forma del array (esta verificación ahora es más para asegurar que la lógica funcionó)
        if input_data.shape[0] != expected_sequence_length or input_data.shape[1] != expected_feature_dim:
            # Este error debería ser raro si la lógica de muestreo es correcta
            return jsonify({
                "error": "Error interno: La forma final de la secuencia de keypoints es incorrecta después del muestreo.",
                "expected_shape": (expected_sequence_length, expected_feature_dim),
                "received_shape": input_data.shape
            }), 500 
        # Añadir la dimensión del batch (1 para una única inferencia)
        input_data = np.expand_dims(input_data, axis=0) # Ahora la forma es

        predictions = model_recognition_palabrasv2.predict(input_data)

        predicct_class_index = np.argmax(predictions, axis=1)[0]
        # Mapear el índice a una etiqueta legible
        predicted_sign_label = SIGN_LABELS_wordsv2[predicct_class_index] if predicct_class_index < len(SIGN_LABELS_wordsv2) else f"clase_desconocida_{predicct_class_index}"

        # Devolver la predicción y las probabilidades
        # Devolver la predicción y las probabilidades
        return jsonify({
            "prediction": predicted_sign_label,
            "probabilities": predictions[0].tolist() # Convertir a lista para JSON
        })

    except Exception as e:
        print(f"Error durante la inferencia de reconocimiento: {e}")
        return jsonify({"error": f"Error interno del servidor durante la predicción: {str(e)}"}), 500


@app.route('/')
def health_check():
    """Endpoint simple para verificar la salud del servicio."""
    return "API de reconocimiento y generación de señas funcionando."

if __name__ == '__main__':
    # Cloud Run asigna el puerto a través de la variable de entorno PORT
    # Si ejecutas localmente, usará el puerto 8080 por defecto
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)