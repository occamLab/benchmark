from anchor.backend.data.firebase import FirebaseDownloader
from anchor.backend.data.ace import process_testing_data
import requests
import numpy as np
from pathlib import Path
import os
import base64
import json
from tqdm import tqdm
import google

individual_model_names = [
    # "training_ua-99ba1aa14ca0c3cac62a791242681b40_ayush_oct_2",
    "training_ua-d0b5902a2b1b46c668dfb206d75c22fa_ayush_oct_1",
]
test_datasets = [
    # "training_ua-d0b5902a2b1b46c668dfb206d75c22fa_ayush_oct_1.tar",
    "training_ua-99ba1aa14ca0c3cac62a791242681b40_ayush_oct_2.tar"
]
OUTPUT_BASE_DIR = Path(__file__).parent / ".cache/multi_model_results"


def send_localization_request(
    model_name: str,
    base64_image: str,
    focal_length: float,
    optical_x: float,
    optical_y: float,
):
    server_url = "http://10.76.135.119:8000/localize"
    headers = {"Content-type": "application/json", "Accept": "application/json"}
    request_body = {
        "base64Jpg": base64_image,
        "modelName": [model_name],
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


def main2():
    for test_name in test_datasets:
        downloader = FirebaseDownloader(
            f"iosLoggerDemo/processedTrainingTars", Path(test_name).parts[-1]
        )
        downloader.extract_ios_logger_tar()

        results_by_model = {}
        for model_name in individual_model_names:
            results_by_model[model_name] = process_testing_data(
                test_name,
                downloader,
                Path(__file__).parent / f".cache/firebase_data/{model_name}/ace",
            )

        output_dir = OUTPUT_BASE_DIR / test_name.rstrip(".tar")
        if not output_dir.exists():
            os.mkdir(output_dir)

        output_fp = output_dir / "results.json"
        with open(output_fp, "w") as file:
            json.dump(results_by_model, file, indent=4)


if __name__ == "__main__":
    main2()
