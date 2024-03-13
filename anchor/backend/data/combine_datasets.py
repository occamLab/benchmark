import os
from pathlib import Path
import shutil


DATASET_NAMES = [
    "training_ua-7c140933b99a14568ee768781fb5c9b2_ayush_mar_4",
    "training_ua-1bab71c5f9279e0777539be4abd6ae2b_ayush_mar_5"
]
OUTPUT_NAME = "training_ua-7c140933b99a14568ee768781fb5c9b2_ayush_mar_4_5_combined"

FB_DATA_DIR = Path(__file__).parent / ".cache/firebase_data"

def main():
    if not (FB_DATA_DIR / OUTPUT_NAME).exists():
        os.mkdir(FB_DATA_DIR / OUTPUT_NAME)
    
    for idx, name in enumerate(DATASET_NAMES):
        shutil.copytree(FB_DATA_DIR / name, FB_DATA_DIR / f"{OUTPUT_NAME}/map_{idx}")

if __name__ == "__main__":
    main()