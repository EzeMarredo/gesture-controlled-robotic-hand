"""
Combina dos datasets en formato YOLO Pose en uno solo.
Renombra los archivos del dataset2 con un prefijo para evitar colisiones.

Uso:
    Configurar DATASET1_DIR, DATASET2_DIR y OUTPUT_DIR abajo y ejecutar.
"""

import os
import shutil

# CONFIGURACIÓN
DATASET1_DIR = "/home/eze/Desktop/PPS/fotos/augmented_custom_dataset"   # dataset principal (no se renombra)
DATASET2_DIR = "/home/eze/Desktop/PPS/Mano_Robótica/all_datasets/dataset_merged"           # dataset secundario (se renombra con prefijo)
OUTPUT_DIR   = "/home/eze/Desktop/PPS/Mano_Robótica/all_datasets/augmented_dataset_merged_v1"
PREFIX       = "augmented_custom_v1_"                     # prefijo para archivos del dataset2
SPLITS       = ["train", "valid"]


def copy_files(src_dir, dst_dir, prefix=""):
    # Copia archivos de src_dir a dst_dir, opcionalmente renombrando con prefijo.
    if not os.path.exists(src_dir):
        print(f"  [SKIP] No existe: {src_dir}")
        return 0

    os.makedirs(dst_dir, exist_ok=True)
    count = 0
    for fname in os.listdir(src_dir):
        src = os.path.join(src_dir, fname)
        dst = os.path.join(dst_dir, prefix + fname)
        shutil.copy2(src, dst)
        count += 1
    return count


def main():
    print("=== Merge de datasets YOLO Pose ===\n")

    total_imgs   = 0
    total_labels = 0

    for split in SPLITS:
        print(f"Procesando split: {split}")

        # Carpetas de salida
        out_images = os.path.join(OUTPUT_DIR, split, "images")
        out_labels = os.path.join(OUTPUT_DIR, split, "labels")
        os.makedirs(out_images, exist_ok=True)
        os.makedirs(out_labels, exist_ok=True)

        # Dataset 1 — sin prefijo
        n = copy_files(os.path.join(DATASET1_DIR, split, "images"), out_images)
        copy_files(os.path.join(DATASET1_DIR, split, "labels"), out_labels)
        print(f"  dataset1 [{split}]: {n} imágenes")
        total_imgs += n

        # Dataset 2 — con prefijo
        n = copy_files(os.path.join(DATASET2_DIR, split, "images"), out_images, PREFIX)
        copy_files(os.path.join(DATASET2_DIR, split, "labels"), out_labels, PREFIX)
        print(f"  dataset2 [{split}]: {n} imágenes")
        total_imgs += n

    # Contar labels totales
    for split in SPLITS:
        lbl_dir = os.path.join(OUTPUT_DIR, split, "labels")
        total_labels += len(os.listdir(lbl_dir))

    # Generar data.yaml
    yaml_content = f"""# Dataset combinado 
path: {os.path.abspath(OUTPUT_DIR)}
train: train/images
val:   valid/images

kpt_shape: [21, 3]

names:
  0: hand
"""
    with open(os.path.join(OUTPUT_DIR, "data.yaml"), "w") as f:
        f.write(yaml_content)

    print(f"\n✓ Completado.")
    print(f"  Total imágenes: {total_imgs}")
    print(f"  Total labels:   {total_labels}")
    print(f"  Dataset en:     {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()