# from anchor.backend.data.supplements.anchor_maps import get_anchor_maps_data
# from anchor.backend.data.supplements.anchor_maps_v2 import get_anchor_maps_data
# from anchor.backend.data.supplements.cab_local import get_anchor_maps_data
from anchor.backend.data.supplements.cab_remote import get_anchor_maps_data, BASE_CAB_REMOTE_URL
from anchor.backend.data.firebase import FirebaseDownloader
from anchor.backend.data.ace import (
    prepare_ace_data,
    process_testing_data,
    process_training_data,
)
from pathlib import Path
from pydantic import BaseModel
import json
import os
import shutil

TEST_RESULT_DIR = Path(__file__).parent.parent / ".cache/test_data"
FIREBASE_DATA_DIR = Path(__file__).parent.parent / ".cache/firebase_data"


def load_test_results():
    results = {}

    if not TEST_RESULT_DIR.exists():
        return results

    for result_dir in os.listdir(TEST_RESULT_DIR):
        res_file = TEST_RESULT_DIR / result_dir / "parameters.json"
        if not res_file.exists():
            continue
        with open(res_file, "r") as jsonfile:
            data = json.load(jsonfile)
            results[(data["model_name"], data["scene_name"])] = (
                TEST_RESULT_DIR / result_dir
            )

    return results


class TestParameters(BaseModel):
    model_name: str
    scene_name: str
    encoder_name: str
    sift_filtering: bool


def main():
    same_scene_anchors = get_anchor_maps_data()
    test_results = load_test_results()

    for scene_anchors in same_scene_anchors:
        model_name_scene_name_iterations = (
            scene_anchors.get_model_name_scene_name_pairs()
        )

        for model_name, scene_name in model_name_scene_name_iterations:
            # Check if the test iteration has already been conducted
            if (model_name, scene_name) in test_results:
                continue

            if model_name != scene_name:
                continue

            local_scene_dir = FIREBASE_DATA_DIR / scene_name
            # if not local_scene_dir.exists():
            test_downloader = FirebaseDownloader("idk", f"{scene_name}.tar")
            test_downloader.unpack_cab_data(scene_name)

            if BASE_CAB_REMOTE_URL in model_name:
                actual_model_name = model_name.split("/")[-1]
                actual_scene_name = scene_name.split("/")[-1]
            else:
                actual_model_name = model_name
                actual_scene_name = scene_name
            local_model_dir = FIREBASE_DATA_DIR / actual_model_name
            if not local_model_dir.exists():
                model_downloader = FirebaseDownloader("idk", f"{model_name}.tar")
                model_downloader.unpack_cab_data(model_name)

            # try:
            # Check if the tars for the model_name and scene_name have been
            # downloaded
            # local_model_dir = FIREBASE_DATA_DIR / model_name
            # if not local_model_dir.exists():
            #     try:
            #         model_downloader = FirebaseDownloader(
            #             "ACEAnchors/tarQueue", f"{model_name}.tar"
            #         )
            #         model_downloader.extract_ios_logger_tar()
            #     except Exception as e:
            #         print(f"[WARNING] skipping {model_name} because of {e}")
            #     prepare_ace_data(model_downloader.extracted_data)

            # local_scene_dir = FIREBASE_DATA_DIR / scene_name
            # if not local_scene_dir.exists():
            #     try:
            #         scene_downloader = FirebaseDownloader(
            #             "ACEAnchors/tarQueue", f"{scene_name}.tar"
            #         )
            #         scene_downloader.extract_ios_logger_tar()
            #     except Exception as e:
            #         print(f"[WARNING] skipping {scene_name} because of {e}")
            #     prepare_ace_data(scene_downloader.extracted_data)

            # # # Next, check if the model has already been created. If it hasn't,
            # # # then run the ACE trainer
            model_path = local_model_dir / "ace/model.pt"
            if not model_path.exists():
                training_downloader = FirebaseDownloader(
                    "ACEAnchors/tarQueue", f"{model_name}.tar"
                )
                process_training_data(
                    f"ACEAnchors/tarQueue/{model_name}.tar",
                    training_downloader,
                    run_tests=False,
                )

            # Finally, run the localization test
            # test_downloader = FirebaseDownloader(
            #     "ACEAnchors/tarQueue", f"{scene_name}.tar"
            # )
            # test_downloader.extract_pose(
            #     test_downloader.local_extraction_location, True
            # )

            results_dir = process_testing_data(
                f"{scene_name}.tar",
                test_downloader,
                FIREBASE_DATA_DIR / f"{actual_model_name}/ace",
            )
            test_parameters = TestParameters(
                model_name=actual_model_name,
                scene_name=actual_scene_name,
                encoder_name="superpoint",
                sift_filtering=True,
            )
            annotated_image_dir = FIREBASE_DATA_DIR / actual_scene_name / "ace/annotated" / actual_model_name
            res_img_dir = results_dir / "annotated_imgs"
            shutil.copytree(annotated_image_dir, res_img_dir)

            with open(results_dir / "parameters.json", "w") as jsonfile:
                json.dump(test_parameters.__dict__, jsonfile, indent=4)
            # except Exception as e:
            #     print(f"[WARNING] Skipping Model: {model_name}, Scene: {scene_name} due to {e}")
            #     continue


if __name__ == "__main__":
    main()
