#Script para tomar fotos automáticamente cada N segundos y auto etiquetado de imágenes con MediaPipe Hands. Ideal para crear un dataset personalizado de mano robótica.

import cv2
import os
import argparse
import time
from datetime import datetime
import mediapipe as mp
from mediapipe.tasks import python
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

def tomar_fotos(carpeta_destino: str, intervalo: int = 3, camara: int = 0):
    os.makedirs(carpeta_destino, exist_ok=True)
    os.makedirs(os.path.join(carpeta_destino, "images"), exist_ok=True)
    os.makedirs(os.path.join(carpeta_destino, "labels"), exist_ok=True)
    print(f"📁 Carpeta de destino: {os.path.abspath(carpeta_destino)}")

    cap = cv2.VideoCapture(camara)
    if not cap.isOpened():
        print(f"❌ Error: No se pudo abrir la cámara (índice {camara})")
        return

    print(f"📷 Cámara iniciada. Tomando fotos cada {intervalo} segundos...")
    print("   Presiona 'q' para detener.\n")

    contador = 0
    ultima_foto = time.time() - intervalo  # tomar foto inmediatamente al arrancar

    while True:
        ret, frame = cap.read()

        h, w = frame.shape[:2]
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB,
                        data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        result = detector.detect(mp_image)           
              

        if not ret:
            print("❌ Error al capturar fotograma.")
            break

        ahora = time.time()
        tiempo_restante = intervalo - (ahora - ultima_foto)

        # Tomar foto cuando se cumple el intervalo
        if tiempo_restante <= 0:
            annotation = process_image(detector, result)

            if annotation is not None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_archivo = f"foto_{timestamp}.jpg"
                basename = os.path.splitext(nombre_archivo)[0]
                
                dst_img = os.path.join(carpeta_destino,"images", nombre_archivo)                
                dst_lbl = os.path.join(carpeta_destino, "labels", basename + ".txt")

                cv2.imwrite(dst_img , frame)

                with open(dst_lbl, "w") as f:
                    f.write(annotation)                
                
                contador += 1
                print(f"✅ [{contador}] Foto guardada: {nombre_archivo}")
            else:
                print("⚠️ No se detectó mano. Foto no guardada.")

            ultima_foto = ahora
            tiempo_restante = intervalo
            

        # Overlay sobre el frame
        overlay = frame.copy()
        cv2.putText(overlay, f"Proxima foto en: {int(tiempo_restante)}s", (10, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        cv2.putText(overlay, f"Fotos tomadas: {contador}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(overlay, "Presiona 'q' para salir", (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)


        cv2.imshow("Camara - Captura automatica", overlay)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print(f"\n🛑 Total de fotos tomadas: {contador}")
    cap.release()
    cv2.destroyAllWindows()
    print("📷 Cámara liberada.")

def process_image(detector, result):
    
    

    if not result.hand_landmarks:
        return None

    landmarks = result.hand_landmarks[0]

    xs = [lm.x for lm in landmarks]
    ys = [lm.y for lm in landmarks]

    x_min = max(0.0, min(xs) - 0.05)
    x_max = min(1.0, max(xs) + 0.05)
    y_min = max(0.0, min(ys) - 0.05)
    y_max = min(1.0, max(ys) + 0.05)

    x_center = (x_min + x_max) / 2
    y_center  = (y_min + y_max) / 2
    bw        = x_max - x_min
    bh        = y_max - y_min

    kpt_parts = []
    for lm in landmarks:
        kx = max(0.0, min(1.0, lm.x))
        ky = max(0.0, min(1.0, lm.y))
        kpt_parts.append(f"{kx:.6f} {ky:.6f} 2")

    line = f"0 {x_center:.6f} {y_center:.6f} {bw:.6f} {bh:.6f} " + " ".join(kpt_parts)
    return line


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Toma fotos automáticamente cada N segundos.")
    parser.add_argument("carpeta", type=str, help="Ruta donde guardar las fotos")
    parser.add_argument("--intervalo", "-i", type=int, default=3, help="Segundos entre fotos (default: 3)")
    parser.add_argument("--camara", "-c", type=int, default=0, help="Índice de la cámara (default: 0)")
    
    args = parser.parse_args()
    tomar_fotos(args.carpeta, args.intervalo, args.camara)