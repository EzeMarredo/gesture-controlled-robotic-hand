# Script para dividir un dataset personalizado de mano robótica en conjuntos de entrenamiento y validación, manteniendo la estructura YOLO26. 
# El script fotos.py guarda las imágenes en una sola carpeta y los labels en otra, sin splits. Este script toma esas imágenes y las distribuye aleatoriamente en carpetas "train" y "valid", copiando también los labels correspondientes.

import os
import shutil
import random

INPUT_DIR     = "/home/eze/Desktop/PPS/fotos/augmented_dataset"
OUTPUT_DIR    = "/home/eze/Desktop/PPS/fotos/augmented_custom_dataset"
TRAIN_RATIO   = 0.8
SEED          = 42
NUM_KEYPOINTS = 21


all_images = []
for root, dirs, files in os.walk(INPUT_DIR):
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            all_images.append(os.path.join(root, file))

print(f"Total de imágenes encontradas: {len(all_images)}")

# Split train/valid
random.seed(SEED)
random.shuffle(all_images)
split_idx  = int(len(all_images) * TRAIN_RATIO)
train_imgs = all_images[:split_idx]
valid_imgs = all_images[split_idx:]

print(f"Train: {len(train_imgs)} | Valid: {len(valid_imgs)}\n")

# Crear carpetas de salida
for split in ["train", "valid"]:
    os.makedirs(os.path.join(OUTPUT_DIR, split, "images"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, split, "labels"), exist_ok=True)

# Procesar imágenes
stats = {"train": 0, "valid": 0}

for split, img_list in [("train", train_imgs), ("valid", valid_imgs)]:
    print(f"Procesando {split}...")
    for img_path in img_list:
        fname    = os.path.basename(img_path)
        basename = os.path.splitext(fname)[0]

        img_dir = os.path.dirname(img_path)
        base_dir = os.path.dirname(img_dir)  
        label_path = os.path.join(base_dir, "labels", basename + ".txt")

        if not os.path.exists(label_path):
            print(f"  Advertencia: No se encontró label para {img_path}, saltando.")
            continue

        # Copiar imagen
        dst_img = os.path.join(OUTPUT_DIR, split, "images", fname)
        shutil.copy2(img_path, dst_img)

        # Copiar label
        dst_lbl = os.path.join(OUTPUT_DIR, split, "labels", basename + ".txt")
        shutil.copy2(label_path, dst_lbl)

        stats[split] += 1

    print(f"  [{split}] Procesadas: {stats[split]}")

# Crear data.yaml
yaml_content = f"""# Dataset de gestos de manos - etiquetas existentes
path: {os.path.abspath(OUTPUT_DIR)}
train: train/images
val:   valid/images

kpt_shape: [{NUM_KEYPOINTS}, 3]

names:
0: hand
"""
with open(os.path.join(OUTPUT_DIR, "data.yaml"), "w") as f:
    f.write(yaml_content)

total_processed = stats["train"] + stats["valid"]

print(f"\n✓ Completado.")
print(f"  Imágenes procesadas: {total_processed}")
print(f"  Dataset guardado en: {OUTPUT_DIR}/")