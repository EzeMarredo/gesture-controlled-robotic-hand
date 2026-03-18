# Script para probar la herramienta de detección de pose de mano de MediaPipe, comparando con el modelo YOLOv26m-pose entrenado. 
# Este script muestra en tiempo real la detección de keypoints y conexiones del esqueleto de la mano usando MediaPipe, para evaluar su rendimiento frente a nuestro modelo personalizado.
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import HandLandmarker, HandLandmarkerOptions, RunningMode

MODEL_PATH = "hand_landmarker.task"  

options = HandLandmarkerOptions(
    base_options=python.BaseOptions(model_asset_path=MODEL_PATH),
    running_mode=RunningMode.IMAGE,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

SKELETON = [
    (0,1),(1,2),(2,3),(3,4),
    (0,5),(5,6),(6,7),(7,8),
    (0,9),(9,10),(10,11),(11,12),
    (0,13),(13,14),(14,15),(15,16),
    (0,17),(17,18),(18,19),(19,20)
]

detector = HandLandmarker.create_from_options(options)
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    h, w = frame.shape[:2]

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB,
                        data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    result = detector.detect(mp_image)

    if result.hand_landmarks:
        landmarks = result.hand_landmarks[0]
        kpts = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]

        for x, y in kpts:
            cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)

        for a, b in SKELETON:
            cv2.line(frame, kpts[a], kpts[b], (255, 0, 0), 2)

    cv2.imshow("MediaPipe Hands", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
detector.close()