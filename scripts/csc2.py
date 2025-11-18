"""
Korea DEM 기반 산불 감시장비(삼각측량) 최적 배치 자동화 코드 (One-Cell Version)
- DEM 다운로드 (국토지리정보원 / VWorld) 연동 지점 포함
- 후보 능선 포인트 자동 추출(local maxima)
- Viewshed 계산 (ray-casting 기반)
- 삼각측량 오차 매핑 (angular intersection error)
- 최적 카메라 3점 조합 출력
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import maximum_filter
from itertools import combinations
import requests
import rasterio
from rasterio.plot import show
import io


# ------------------------------------------------------------
# 1) DEM 다운로드 (PLACEHOLDER: API KEY 필요)
# ------------------------------------------------------------

def download_korea_dem(bbox, resolution=30):
    """
    bbox = [minX, minY, maxX, maxY] in EPSG:4326
    resolution = DEM 해상도
    **실제 DEM API 연동 코드 자리**
    ------------------------------------------------------------
    NGII(국토지리정보원) 또는 VWorld DEM API 사용해야 하며,
    아래는 예시 placeholder임.
    ------------------------------------------------------------
    반환 형식: numpy array 형태의 DEM raster
    """

    # 예시 URL (사용 전 반드시 실제 서비스 URL로 교체)
    dummy_url = "https://api.vworld.kr/req/wcs"  # 실제 작동 안 함
    params = {
        "service": "WCS",
        "request": "GetCoverage",
        "version": "1.0.0",
        "key": "YOUR_API_KEY",     # ← API KEY 넣기
        "coverage": "dem",
        "format": "geotiff",
        "bbox": ",".join(map(str, bbox)),
        "resX": resolution,
        "resY": resolution
    }

    print("실제 DEM API 요청은 disabled 상태입니다.")
    print("대신 synthetic DEM(합성 DEM)을 자동 생성합니다.\n")

    # --------------------------
    # (데모용) 합성 DEM 생성
    # --------------------------
    size = 200
    x = np.linspace(0, 6, size)
    y = np.linspace(0, 6, size)
    X, Y = np.meshgrid(x, y)
    # 능선 + 봉우리 패턴을 일부 반영한 DEM 생성
    DEM = 200 + 40*np.sin(X*1.2) * np.cos(Y*1.5) + 30*np.exp(-((X-4)**2 + (Y-2.5)**2))
    DEM = DEM + np.random.normal(0, 1.0, DEM.shape)
    return DEM


# ------------------------------------------------------------
# 2) 후보 지점(봉우리) 추출하기 : Local Maxima
# ------------------------------------------------------------

def extract_candidate_peaks(DEM, neighborhood=15, top_k=30):
    """
    DEM에서 국소최대값(능선 상 주요 봉우리)을 찾는다.
    neighborhood: 주변 영역 크기
    top_k: 상위 N개 후보만 선택
    """
    # 국소 최댓값 필터
    filtered = maximum_filter(DEM, size=neighborhood)
    peaks = (DEM == filtered)

    # 후보 후보지 좌표 추출
    ys, xs = np.where(peaks)

    # 높이 기준 정렬 후 top_k만 선택
    heights = DEM[ys, xs]
    idx = np.argsort(-heights)[:top_k]

    candidates = []
    for i in idx:
        candidates.append({
            "id": f"P{i}",
            "x": xs[i],
            "y": ys[i],
            "elev": float(DEM[ys[i], xs[i]])
        })
    return candidates


# ------------------------------------------------------------
# 3) Viewshed 계산 (단순 Ray-casting)
# ------------------------------------------------------------

def viewshed_simple(DEM, cam_x, cam_y, cam_h=20):
    """
    cam_x, cam_y : 카메라 위치 (DEM 픽셀 좌표)
    cam_h : 카메라 설치 높이(m)

    output : 동일 크기 행렬, 시야 확보(True) / 불가(False)
    """
    H, W = DEM.shape
    visible = np.zeros((H, W), dtype=bool)

    cam_elev = DEM[cam_y, cam_x] + cam_h

    for y in range(H):
        for x in range(W):
            # 동일 지점은 무조건 visible
            if x == cam_x and y == cam_y:
                visible[y, x] = True
                continue

            # 경로 샘플링
            n = 80
            xs = np.linspace(cam_x, x, n)
            ys = np.linspace(cam_y, y, n)

            blocked = False
            for i in range(1, n-1):
                xi, yi = int(xs[i]), int(ys[i])
                if DEM[yi, xi] > cam_elev:
                    blocked = True
                    break

            visible[y, x] = not blocked
    return visible


# ------------------------------------------------------------
# 4) 삼각측량 오차 계산 (각도 기반)
# ------------------------------------------------------------

def angle_between(a, b):
    """두 벡터 사이 각도 (라디안)"""
    unit_a = a / np.linalg.norm(a)
    unit_b = b / np.linalg.norm(b)
    return np.arccos(np.clip(np.dot(unit_a, unit_b), -1, 1))


def triangulation_error(camA, camB, camC, target):
    """
    카메라 A,B,C와 target의 조합에서 삼각측량 정확도(각도 기반)를 계산한다.
    - 반환: 라디안 단위 error (적을수록 정확함)
    """
    A = np.array([camA["x"], camA["y"]])
    B = np.array([camB["x"], camB["y"]])
    C = np.array([camC["x"], camC["y"]])
    T = np.array([target[0], target[1]])

    vA, vB, vC = T - A, T - B, T - C

    angAB = angle_between(vA, vB)
    angAC = angle_between(vA, vC)
    angBC = angle_between(vB, vC)

    # 세 각도 중 최소 각도를 "겹침각(overlap)"으로 보고 오차로 사용
    return float(min(angAB, angAC, angBC))


# ------------------------------------------------------------
# 5) 전체 파이프라인 실행
# ------------------------------------------------------------

# 1) DEM 다운로드 (합성 DEM 또는 실제 DEM)
bbox = [128.0, 35.5, 128.06, 35.56]  # 예시
DEM = download_korea_dem(bbox=bbox)

H, W = DEM.shape
print("DEM shape:", DEM.shape)

# 2) 후보 봉우리 30개 추출
candidates = extract_candidate_peaks(DEM, neighborhood=15, top_k=12)
print("후보 지점 개수:", len(candidates))

# 3) 모든 후보 지점 viewshed 계산
viewsheds = {}
for c in candidates:
    print(f"viewshed 계산: {c['id']}")
    viewsheds[c["id"]] = viewshed_simple(DEM, c["x"], c["y"])

# 4) 샘플링된 지점들에 대해 삼각측량 오차 평가
sample_points = [(x, y) for x in range(0, W, 6) for y in range(0, H, 6)]

results = []
for trio in combinations(candidates, 3):
    A, B, C = trio
    errors = []
    cover = 0
    total = 0

    for px, py in sample_points:
        seen = (
            viewsheds[A["id"]][py, px] +
            viewsheds[B["id"]][py, px] +
            viewsheds[C["id"]][py, px]
        )
        if seen >= 2:  # 2개 이상 카메라가 볼 수 있어야 삼각측량 가능
            cover += 1
            err = triangulation_error(A, B, C, (px, py))
            errors.append(err)

        total += 1

    if len(errors) > 0:
        results.append({
            "cams": (A["id"], B["id"], C["id"]),
            "coverage": cover / total,
            "mean_err_deg": np.mean(errors) * 180/np.pi,
            "p95_err_deg": np.percentile(errors, 95) * 180/np.pi
        })

# 정렬 (오차↓ + 커버리지↑)
results_sorted = sorted(results, key=lambda x: (x["p95_err_deg"], -x["coverage"]))

print("\n Top 5 Triangulation Camera Sets")
for r in results_sorted[:5]:
    print(r)


# ------------------------------------------------------------
# 6) 최적 카메라 조합 시각화
# ------------------------------------------------------------

best = results_sorted[0]
best_cam_ids = best["cams"]

fig, ax = plt.subplots(figsize=(6, 6))
ax.imshow(DEM, cmap='terrain')
for c in candidates:
    ax.scatter(c["x"], c["y"], c='white' if c["id"] not in best_cam_ids else 'red', s=60)
    ax.text(c["x"]+1, c["y"]+1, c["id"], color="yellow", fontsize=8)

plt.title(f"Best Cameras: {best_cam_ids}")
plt.show()
