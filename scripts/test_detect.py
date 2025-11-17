# 학습완료된 모델을 사용하여 테스트 이미지를 한장씩 평가해보는것
from ultralytics import YOLO
import cv2
import os

def main():
    # YOLO 모델 로드
    model_path = r"../weights/best.pt"
    model = YOLO(model_path)

    # 테스트할 이미지 경로 (원하는 이미지로 바꿔도 됨)
    img_path = r"C:\Users\user\OneDrive\Desktop\csc\test_image\images632_jpg.rf.829f5519f8463e0f1cf4316e45977837.jpg"

    # 출력 폴더
    save_dir = r"C:\Users\user\OneDrive\Desktop\csc\result_image"
    os.makedirs(save_dir, exist_ok=True)

    # YOLO 추론
    results = model(img_path)

    # 탐지된 객체 정보 출력
    print("\n=== 탐지된 객체 정보 ===")
    for box in results[0].boxes:
        cls = int(box.cls)                       # 클래스 인덱스
        conf = float(box.conf)                   # confidence
        class_name = results[0].names[cls]       # 클래스 이름
        print(f"클래스: {class_name},  확률: {conf:.3f}")

    # YOLO가 그린 이미지(frames)
    annotated = results[0].plot()

    # 저장 경로
    save_path = os.path.join(save_dir, "result.jpg")

    # 저장
    cv2.imwrite(save_path, annotated)

    print(f"\n[완료] 바운딩박스 결과 이미지 저장됨 → {save_path}")

if __name__ == "__main__":
    main()
