#욜로 파인튜닝 학습모델 코드
from ultralytics import YOLO
import shutil
import os

def main():
    model = YOLO("yolov8n.pt") 
    results = model.train(
        data="../dataset/data.yaml",
        epochs=20,
        imgsz=640,
        batch=8,
        workers=0,     # Windows 안전 설정
        plots=False
    )

    default_path = "runs/detect/train/weights/best.pt"
    target_path = "../weights/best.pt"

    if os.path.exists(default_path):
        shutil.copy(default_path, target_path)
        print(f"[INFO] best.pt saved to: {target_path}")
    else:
        print("[WARNING] best.pt not found.")

if __name__ == "__main__":
    main()
