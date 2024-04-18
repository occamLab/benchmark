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

combined_model_name = (
    "training_ua-7c140933b99a14568ee768781fb5c9b2_ayush_mar_4_5_combined_better_enhancement"
)
individual_model_names = [
    "training_ua-7c140933b99a14568ee768781fb5c9b2_ayush_mar_4_better_enhancement",
    "training_ua-1bab71c5f9279e0777539be4abd6ae2b_ayush_mar_5_better_enhancement",
]
test_datasets = [
    # 9:30
    "testing_FE49EDB3-4A95-4B60-A942-5E41463DAEEF_ayush_mar_3_better_enhancement",
    # 12:00
    "testing_7AAC6056-FEA5-4712-8134-26B13499316C_ayush_mar_3_better_enhancement",
    # Days later
    "testing_2E4723D2-57C7-4AA1-B3B3-CE276ABF0DC7_ayush_mar_3_better_enhancement",
]
OUTPUT_BASE_DIR = Path(__file__).parent / ".cache/better_enhancement_multi_model_results"


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


def main():
    # Assumes that all files have been downloaded from firebase and prepared for ACE already.
    for test_dataset in test_datasets:
        test_dataset_dir = (
            Path(__file__).parent / ".cache/firebase_data" / test_dataset.rstrip(".tar")
        )
        ace_dir = test_dataset_dir / "ace/test"

        downloader = FirebaseDownloader("iosLoggerDemo/processedTestTars", test_dataset)
        downloader.extract_pose(
            Path(str(test_dataset_dir).rstrip(".tar")), mapping_phase=False
        )

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
            name: [] for name in [combined_model_name] + individual_model_names
        }

        for idx in tqdm(range(len(images))):
            for model_name in [combined_model_name] + individual_model_names:
                pose, inlier_counts, best_model = send_localization_from_path(
                    model_name, Path(images[idx]), Path(intrinsics[idx])
                )
                assert best_model == model_name[9:]

                arkit_pose = {
                    key: (
                        list(value)
                        if isinstance(
                            value,
                            google.protobuf.internal.containers.RepeatedScalarFieldContainer,
                        )
                        else value
                    )
                    for key, value in downloader.extracted_data.sensors_extracted[
                        "localization_phase"
                    ]["poses"][idx].items()
                }
                results_by_model[model_name].append(
                    {
                        "frame_num": idx,
                        "timestamp": arkit_pose["timestamp"],
                        "ACE": np.reshape(pose, [16], order="F").tolist(),
                        "ACE_INLIER_COUNT": inlier_counts,
                        "ARKIT": arkit_pose["rotation_matrix"],
                        "CLOUD_ANCHOR": None,
                    }
                )

        if not OUTPUT_BASE_DIR.exists():
            os.mkdir(OUTPUT_BASE_DIR)

        output_dir = OUTPUT_BASE_DIR / test_dataset.rstrip(".tar")
        if not output_dir.exists():
            os.mkdir(output_dir)

        output_fp = output_dir / "results.json"
        with open(output_fp, "w") as file:
            json.dump(results_by_model, file, indent=4)


def main2():
    for test_name in test_datasets:
        downloader = FirebaseDownloader(
            Path(test_name).parent, Path(test_name).parts[-1]
        )
        downloader.extract_ios_logger_tar()

        results_by_model = {}
        for model_name in [combined_model_name] + individual_model_names:
            results_by_model[model_name] = process_testing_data(
                test_name,
                downloader,
                Path(__file__).parent / f".cache/firebase_data/{model_name}/ace",
            )

        if not OUTPUT_BASE_DIR.exists():
            os.mkdir(OUTPUT_BASE_DIR)

        output_dir = OUTPUT_BASE_DIR / test_name.rstrip(".tar")
        if not output_dir.exists():
            os.mkdir(output_dir)

        output_fp = output_dir / "results.json"
        with open(output_fp, "w") as file:
            json.dump(results_by_model, file, indent=4)


if __name__ == "__main__":
    # main()
    main2()
