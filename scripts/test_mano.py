# Script para probar el modelo YOLOv26m-pose con una cámara web en tiempo real, detectando la pose de la mano y dibujando los keypoints y conexiones del esqueleto.
import cv2
import numpy as np
from ultralytics import YOLO

#train 12 anda bien pero falla con los dedos individuales
model = YOLO("runs/pose/train27/weights/best.pt")

# Definir conexiones del esqueleto (según tu convención de keypoints)
SKELETON = [
    (0, 1), (1, 2), (2, 3), (3, 4),       # pulgar
    (0, 5), (5, 6), (6, 7), (7, 8),       # índice
    (0, 9), (9, 10), (10, 11), (11, 12),  # medio
    (0, 13), (13, 14), (14, 15), (15, 16), # anular
    (0, 17), (17, 18), (18, 19), (19, 20)  # meñique
]

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    results = model(frame)

    for result in results:
        if result.keypoints is not None and len(result.keypoints.xy) > 0:
            kpts = result.keypoints.xy[0].cpu().numpy()

            for x, y in kpts:
                cv2.circle(frame, (int(x), int(y)), 4, (0, 255, 0), -1)

            for a, b in SKELETON:
                x1, y1 = kpts[a]
                x2, y2 = kpts[b]
                cv2.line(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)


    cv2.imshow("Hand Pose", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()