from anchor_maps import get_anchor_maps_data
# from anchor.backend.data.supplements.anchor_maps import get_anchor_maps_data
from pathlib import Path
from anchor.backend.data.firebase import FirebaseDownloader
from anchor.backend.data.ace import prepare_ace_data, process_testing_data, process_training_data

TEST_RESULT_DIR = Path(__file__).parent.parent / ".cache/test_data"
FIREBASE_DATA_DIR = Path(__file__).parent.parent / ".cache/firebase_data"

def load_test_results():
    # TODO: actual logic lol
    return {}

def main():
    same_scene_anchors = get_anchor_maps_data()
    test_results = load_test_results()

    for scene_anchors in same_scene_anchors:
        model_name_scene_name_iterations = scene_anchors.get_model_name_scene_name_pairs()

        for model_name, scene_name in model_name_scene_name_iterations:
            # Check if the test iteration has already been conducted
            if (model_name, scene_name) in test_results:
                continue

            # Check if the tars for the model_name and scene_name have been
            # downloaded
            local_model_dir = FIREBASE_DATA_DIR / model_name
            if not local_model_dir.exists():
                model_downloader = FirebaseDownloader("ACEAnchors/tarQueue", f"{model_name}.tar")
                model_downloader.extract_ios_logger_tar()
                prepare_ace_data(model_downloader.extracted_data)

            local_scene_dir = FIREBASE_DATA_DIR / model_name
            if not local_scene_dir.exists():
                scene_downloader = FirebaseDownloader("ACEAnchors/tarQueue", f"{scene_name}.tar")
                scene_downloader.extract_ios_logger_tar()
                prepare_ace_data(scene_downloader.extracted_data)

            # Next, check if the model has already been created. If it hasn't,
            # then run the ACE trainer
            model_path = local_model_dir / "model.pt"
            if not model_path.exists():
                training_downloader = FirebaseDownloader("ACEAnchors/tarQueue", f"{model_name}.tar")
                process_training_data(
                    f"ACEAnchors/tarQueue/{model_name}.tar", training_downloader
                )

            # Finally, run the localization test
            test_downloader = FirebaseDownloader("ACEAnchors/tarQueue", f"{scene_name}.tar")
            process_testing_data(f"{scene_name}.tar", test_downloader, FIREBASE_DATA_DIR / f"{model_name}/ace")

if __name__ == "__main__":
    main()