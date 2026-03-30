#Script para entrenar el modelo YOLOv26m-pose con un dataset personalizado de mano robótica.

from ultralytics import YOLO

"""
model = YOLO("yolo26m-pose.pt") 
#model = YOLO("runs/pose/train4/weights/last.pt")

model.train(
    data="/home/eze/Desktop/PPS/Mano_Robótica/all_datasets/augmented_dataset_merged_v1/data.yaml", 
    epochs=100, 
    imgsz=640,
    batch=24, 
    device=0,
    workers=4,    # menos procesos de carga en paralelo
    amp = True,       # usar precisión mixta para acelerar y reducir uso de memoria
    )   

"""

# SI YA SE ENTRENÓ ANTES, DESCOMENTAR PARA REANUDAR EL ENTRENAMIENTO DESDE EL ÚLTIMO CHECKPOINT GUARDADO
# SI VOY A REANUDAR EL ENTRENAMIENTO, CAMBIAR LAS EPOCAS EN ARCHIVO args.yaml DEL ENTRENAMIENTO DESEADO

model = YOLO("runs/pose/train27/weights/last.pt")
model.train(resume=True)
