# Wildfire Detection (YOLO 기반 산불·연기 탐지 시스템)

본 프로젝트는 **YOLO 모델을 파인튜닝하여 산불 및 연기(Class 5개)를 탐지**하고,  
훈련된 모델 성능을 평가하며, 단일 이미지에 대한 추론 결과를 생성하는 시스템입니다.

---

# 📁 Project Structure
csc/
├── dataset/
│ ├── README.dataset.txt
│ ├── README.roboflow.txt
│ ├── data.yaml
│ ├── train/ 
│ ├── valid/ 
│ └── test/ 
│
├── scripts/
│ ├── train.py-> 모델 학습코드
│ ├── test_evaluate.py-> 모델 검증코드
│ ├── test_evaluate2.py
│ ├── test_detect.py-> 개별 이미지 검증코드
│ ├── yolov8n.pt
│ └── yolo11n.pt
│
├── weights/
│ ├── best.pt
│ └── last.pt
│
├── result_image/
│ ├── result1.jpg
│ ├── result2.jpg
│ └── result3.jpg
│
├── runs/detect/
│ ├── val4/
│ └── val5/
│
├── test_image/
│ ├── *.jpg
│
└── README.md

---

# 🔥 학습된 클래스 (5개)
0: Heavy smoke
1: Large fire
2: Low smoke
3: Medium fire
4: Small fire

---

# 📄 data.yaml

```yaml
train: ./train/images
val: ./valid/images
test: ./test/images

nc: 5
names: ['Heavy smoke', 'Large fire', 'Low smoke', 'Medium fire', 'Small fire']


## Collaboration Workflow
본 프로젝트는 GitHub Flow를 기반으로 협업했습니다.

1. main 브랜치 유지
2. 팀원별 개인 브랜치 생성  
   - gyuri  
   - haeyun  
   - seoyeon  
   - taehyun
3. 개인 브랜치에서 기능 단위로 작업 후 commit/push
4. Pull Request를 생성하여 코드 리뷰 진행
5. 리뷰 승인 후 main에 merge

## Acknowledgement
본 프로젝트는 YOLOv7 기반 오픈소스를 참고하여 확장 및 커스터마이징했습니다..
