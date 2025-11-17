import os

EXCLUDED_DIRS = {
    "train",
    "valid",
    "test",
    ".git"
}

BASE_PATH = r"C:\Users\user\OneDrive\Desktop\csc"

def print_tree(path, prefix=""):
    items = sorted(os.listdir(path))
    for idx, item in enumerate(items):
        if item in EXCLUDED_DIRS:
            continue

        full_path = os.path.join(path, item)
        connector = "└── " if idx == len(items) - 1 else "├── "

        # dataset 내부의 train/valid/test는 표시만 하고 내부는 생략
        if os.path.basename(path) == "dataset" and item in {"train", "valid", "test"}:
            print(prefix + connector + item + "/ (내용 생략)")
            continue

        if os.path.isdir(full_path):
            print(prefix + connector + item + "/")
            new_prefix = prefix + ("    " if idx == len(items) - 1 else "│   ")
            print_tree(full_path, new_prefix)
        else:
            print(prefix + connector + item)

print("폴더 구조 (dataset 내부 생략, .git 제외):\n")
print_tree(BASE_PATH)
