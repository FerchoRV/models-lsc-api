import numpy as np
import cv2
import mediapipe as mp


try:
    # cargar modelos de mediapipe
    mp_holistic = mp.solutions.holistic # Holistic model
    mp_drawing = mp.solutions.drawing_utils # Drawing utilities
except Exception as e:
    print(f"Error al importar MediaPipe: {e}")
    mp_holistic = None
    mp_drawing = None

def mediapipe_detection(image, model):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB) # COLOR CONVERSION BGR 2 RGB
    image.flags.writeable = False                  # Image is no longer writeable
    results = model.process(image)                 # Make prediction
    image.flags.writeable = True                   # Image is now writeable 
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR) # COLOR COVERSION RGB 2 BGR
    return image, results


def extract_keypoints_hands(results):
    
    lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
    rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
    return np.concatenate([lh, rh])

def extract_keypoints_pose_hands(results):
    pose = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten() if results.pose_landmarks else np.zeros(33*4)
    lh = np.array([[res.x, res.y, res.z] for res in results.left_hand_landmarks.landmark]).flatten() if results.left_hand_landmarks else np.zeros(21*3)
    rh = np.array([[res.x, res.y, res.z] for res in results.right_hand_landmarks.landmark]).flatten() if results.right_hand_landmarks else np.zeros(21*3)
    return np.concatenate([pose,lh, rh])

def process_video_sign(type_extract, url_video):
    if mp_holistic is None:
        raise RuntimeError("MediaPipe no está disponible. Asegúrate de que la biblioteca esté instalada correctamente.")
    
    cap = cv2.VideoCapture(url_video) # Usa url_video directamente
    if not cap.isOpened():
        print(f"Error: No se pudo abrir el video desde la URL: {url_video}")
        return None # O lanzar una excepción específica

    sequence_keypoints = []

    with mp_holistic.Holistic(static_image_mode=False, model_complexity=1, smooth_landmarks=True, enable_segmentation=False, min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break # Sale del bucle cuando no hay más frames o hay un error de lectura

            image, results = mediapipe_detection(frame, holistic)
            
            if type_extract == 'hands':
                keypoints = extract_keypoints_hands(results)
            elif type_extract == 'pose_hands':
                keypoints = extract_keypoints_pose_hands(results)
            else:
                # Esto ya se valida antes en el endpoint, pero es una buena práctica aquí también
                raise ValueError("El tipo de extracción enviado no existe debe ser 'hands' o 'pose_hands'.") 
            
            sequence_keypoints.append(keypoints)
    
    cap.release() # Cierra el objeto de captura de video
    cv2.destroyAllWindows() # Cierra las ventanas de OpenCV, si se abrieron

    return sequence_keypoints