"""
Convierte anotaciones COCO JSON (keypoints) a formato YOLO Pose para YOLO26.

Estructura esperada del dataset:
    dataset/
    ├── train/
    │   ├── _annotations.coco.json
    │   └── (imágenes .jpg)
    ├── valid/
    │   ├── _annotations.coco.json
    │   └── (imágenes .jpg)
    └── test/
        ├── _annotations.coco.json
        └── (imágenes .jpg)

Resultado (estructura compatible con YOLO26):
    dataset_yolo/
    ├── images/
    │   ├── train/
    │   ├── val/
    │   └── test/
    ├── labels/
    │   ├── train/
    │   ├── val/
    │   └── test/
    └── data.yaml
"""

import json
import os
import shutil

# ─── CONFIGURACIÓN ────────────────────────────────────────────────────────────
DATASET_DIR   = "hand_keypoint_dataset_26k"
OUTPUT_DIR    = "hand_keypoint_dataset_26k-yolo26"
NUM_KEYPOINTS = 21

# Mapeo de splits: carpeta_origen → nombre_yolo
# YOLO26 espera "val", no "valid"
SPLITS = {
    "train": "train",
    "valid": "val",
    "test":  "test",
}

# flip_idx para mano derecha ↔ izquierda (volteo horizontal en augmentation)
# Índices MediaPipe: 0=wrist, 1-4=thumb, 5-8=index, 9-12=middle, 13-16=ring, 17-20=pinky
# Al voltear una mano, los dedos se invierten lateralmente.

FLIP_IDX = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
# ──────────────────────────────────────────────────────────────────────────────


def convert_split(split_src, split_dst):
    coco_json_path = os.path.join(DATASET_DIR, split_src, "_annotations.coco.json")
    images_src_dir = os.path.join(DATASET_DIR, split_src)

    
    out_images_dir = os.path.join(OUTPUT_DIR, "images", split_dst)
    out_labels_dir = os.path.join(OUTPUT_DIR, "labels", split_dst)
    os.makedirs(out_images_dir, exist_ok=True)
    os.makedirs(out_labels_dir, exist_ok=True)

    with open(coco_json_path) as f:
        coco = json.load(f)

    images_by_id = {img["id"]: img for img in coco["images"]}

    anns_by_image = {}
    for ann in coco["annotations"]:
        anns_by_image.setdefault(ann["image_id"], []).append(ann)

    converted = 0
    skipped   = 0
    no_labels = 0

    for img_id, img_info in images_by_id.items():
        img_w    = img_info["width"]
        img_h    = img_info["height"]
        filename = img_info["file_name"]

        # Copiar imagen
        src = os.path.join(images_src_dir, filename)
        dst = os.path.join(out_images_dir, filename)
        if not os.path.exists(src):
            print(f"  [WARN] Imagen no encontrada: {src}")
            skipped += 1
            continue
        shutil.copy2(src, dst)

        # Construir labels
        anns = anns_by_image.get(img_id, [])

        if not anns:
            # Imagen sin anotaciones: crear txt vacío 
            label_path = os.path.join(out_labels_dir, os.path.splitext(filename)[0] + ".txt")
            open(label_path, "w").close()
            no_labels += 1
            converted += 1
            continue

        lines = []
        for ann in anns:
            # Bounding box 
            bx, by, bw, bh = ann["bbox"]

            # Clamp para evitar valores fuera de [0, 1] por errores de anotación
            x_center = max(0.0, min(1.0, (bx + bw / 2) / img_w))
            y_center = max(0.0, min(1.0, (by + bh / 2) / img_h))
            bw_norm  = max(0.0, min(1.0, bw / img_w))
            bh_norm  = max(0.0, min(1.0, bh / img_h))

            # Keypoints
            kpts = ann.get("keypoints", [])

            if len(kpts) < NUM_KEYPOINTS * 3:
                # Rellenar con ceros si faltan keypoints
                kpts = kpts + [0] * (NUM_KEYPOINTS * 3 - len(kpts))

            kpt_parts = []
            for i in range(NUM_KEYPOINTS):
                kx = max(0.0, min(1.0, kpts[i * 3]     / img_w))
                ky = max(0.0, min(1.0, kpts[i * 3 + 1] / img_h))
                kv = int(kpts[i * 3 + 2])  # visibilidad: 0, 1 o 2
                kpt_parts.append(f"{kx:.6f} {ky:.6f} {kv}")

            line = (f"0 {x_center:.6f} {y_center:.6f} {bw_norm:.6f} {bh_norm:.6f} "
                    + " ".join(kpt_parts))
            lines.append(line)

        label_name = os.path.splitext(filename)[0] + ".txt"
        label_path = os.path.join(out_labels_dir, label_name)
        with open(label_path, "w") as f:
            f.write("\n".join(lines))

        converted += 1

    print(f"  [{split_src} → {split_dst}] ✓ {converted} imágenes "
          f"| ⚠ {skipped} saltadas | 📭 {no_labels} sin anotaciones")


def create_yaml():
    flip_str = "[" + ", ".join(str(i) for i in FLIP_IDX) + "]"

    yaml_content = f"""# Dataset mano robótica - formato YOLO26 Pose
# Documentación: https://docs.ultralytics.com/datasets/pose/

path: {os.path.abspath(OUTPUT_DIR)}
train: images/train   # {sum(1 for _ in open(os.path.join(OUTPUT_DIR, 'images', 'train'), 'r') if False) if False else ''}
val:   images/val
test:  images/test

# Keypoints
kpt_shape: [{NUM_KEYPOINTS}, 3]  # [num_keypoints, dims] (x, y, visibilidad)
flip_idx: {flip_str}

# Clases
names:
  0: hand

# Nombres de keypoints (MediaPipe Hand)
kpt_names:
  0:
    - wrist
    - thumb_cmc
    - thumb_mcp
    - thumb_ip
    - thumb_tip
    - index_mcp
    - index_pip
    - index_dip
    - index_tip
    - middle_mcp
    - middle_pip
    - middle_dip
    - middle_tip
    - ring_mcp
    - ring_pip
    - ring_dip
    - ring_tip
    - pinky_mcp
    - pinky_pip
    - pinky_dip
    - pinky_tip
"""
    yaml_path = os.path.join(OUTPUT_DIR, "data.yaml")
    with open(yaml_path, "w") as f:
        f.write(yaml_content)
    print(f"\n✅ data.yaml creado en: {yaml_path}")


def verify_output():
    """Verifica que la conversión fue exitosa comparando imágenes vs labels."""
    print("\n─── Verificación ───────────────────────────────")
    for split_dst in ["train", "val", "test"]:
        img_dir = os.path.join(OUTPUT_DIR, "images", split_dst)
        lbl_dir = os.path.join(OUTPUT_DIR, "labels", split_dst)
        if not os.path.exists(img_dir):
            continue
        n_imgs = len([f for f in os.listdir(img_dir) if f.lower().endswith((".jpg", ".png", ".jpeg"))])
        n_lbls = len([f for f in os.listdir(lbl_dir) if f.endswith(".txt")]) if os.path.exists(lbl_dir) else 0
        status = "✓" if n_imgs == n_lbls else "⚠ MISMATCH"
        print(f"  [{split_dst:5}] {status}  imágenes: {n_imgs} | labels: {n_lbls}")
    print("────────────────────────────────────────────────")


def main():
    print("=== Conversión COCO → YOLO26 Pose ===\n")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for split_src, split_dst in SPLITS.items():
        json_path = os.path.join(DATASET_DIR, split_src, "_annotations.coco.json")
        if not os.path.exists(json_path):
            print(f"  [{split_src}] No encontrado, saltando...")
            continue
        convert_split(split_src, split_dst)

    create_yaml()
    verify_output()

    print(f"\n✓ Dataset listo en: {OUTPUT_DIR}/")
    print("\nPara entrenar:")
    print(f"  from ultralytics import YOLO")
    print(f"  model = YOLO('yolo26n-pose.pt')")
    print(f"  model.train(data='{os.path.abspath(OUTPUT_DIR)}/data.yaml', epochs=100, imgsz=640)")


if __name__ == "__main__":
    main()