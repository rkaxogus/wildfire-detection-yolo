#테스트 데이터셋으로 모델의 성능 평가
from ultralytics import YOLO

def main():
    model_path = r"C:\Users\user\OneDrive\Desktop\csc\weights\best.pt"
    data_yaml  = r"C:\Users\user\OneDrive\Desktop\csc\dataset\data.yaml"

    model = YOLO(model_path)

    results = model.val(
        data=data_yaml,
        split='train',
        imgsz=640,
        workers=0   # Windows 오류 방지를 위한 추가 옵션
    )

    print("\n===== Evaluation Results =====")
    print(f"mAP50:      {results.box.map50:.4f}")
    print(f"mAP50-95:   {results.box.map:.4f}")
    print(f"Precision:  {results.box.mp:.4f}")
    print(f"Recall:     {results.box.mr:.4f}")
    print("================================\n")


if __name__ == '__main__':
    main()
