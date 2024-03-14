from anchor.backend.server.localizer import LocalizeImageReq
from anchor.backend.data.firebase import FirebaseDownloader
import requests
import numpy as np
from pathlib import Path
import os
import base64
import json

combined_model_name = "training_SOMETHING_ayush_mar_4_5_combined"
individual_model_names = [
    "training_SOMETHING_ayush_mar_4",
    "training_SOMETHING_ayush_mar_5"
]
test_dataset = "test_something"
OUTPUT_DIR = Path(__file__).parent / ".cache/multi_model_results" / test_dataset

def send_localization_request(
    model_name: str,
    base64_image: str,
    focal_length: float,
    optical_x: float,
    optical_y: float,
):
    server_url = "http://10.76.135.81:8000/localize"
    headers = {"Content-type": "application/json", "Accept": "application/json"}
    request_body = {
        "base64Jpg": base64_image,
        "modelName": model_name,
        "focal_length": focal_length,
        "optical_x": optical_x,
        "optical_y": optical_y,
        "arkit_pose": [0.0],
    }
    response = requests.post(server_url, json=request_body, headers=headers)
    response_body = response.json()

    pose = np.array(response_body["pose"]).reshape(4, 4)
    inlier_counts = response_body["inlier_count"]
    best_model = response_body["model"]
    return pose, inlier_counts, best_model

def send_localization_from_path(
    model_name: str, image_path: Path, intrinsics_path: Path
):
    image_b64: str = base64.b64encode(image_path.read_bytes()).decode()
    intrinsics = np.loadtxt(intrinsics_path)
    return send_localization_request(
        model_name, image_b64, intrinsics[0, 0], intrinsics[0, 2], intrinsics[1, 2]
    )

def main():
    # Assumes that all files have been downloaded from firebase and prepared for ACE already.
    test_dataset_dir = Path(__file__).parent / ".cache/firebase_data" / test_dataset
    ace_dir = test_dataset_dir / "ace"

    downloader = FirebaseDownloader("iosLoggerDemo/processedTestTars", test_dataset)
    downloader.extract_pose(test_dataset_dir, mapping_phase=False)

    images = list(
        map(
            lambda x: ace_dir / "rgb" / x,
            sorted(os.listdir(ace_dir / "rgb")),
        )
    )
    intrinsics = list(
        map(
            lambda x: ace_dir / "calibration" / x,
            sorted(os.listdir(ace_dir / "calibration")),
        )
    )
    assert len(images) == len(intrinsics)

    results_by_model = {
        name: [] for name in [combined_model_name, "arkit"] + individual_model_names
    }

    for idx, image_path in enumerate(images):
        for model_name in [combined_model_name] + individual_model_names:
            pose, inlier_counts, best_model = send_localization_from_path(
                model_name, Path(image_path), Path(intrinsics[idx]) 
            )
            assert best_model == model_name

            results_by_model[model_name].append({
                "frame_num": idx,
                "timestamp": None,
                "ACE": pose,
                "ACE_INLIER_COUNT": inlier_counts,
                "ARKIT": downloader.extracted_data.sensors_extracted["localization_phase"]["poses"][idx],
                "CLOUD_ANCHOR": None
            })

    with open(OUTPUT_DIR / "results.json", "w") as file:
        json.dump(results_by_model, file)

if __name__ == "__main__":
    main()