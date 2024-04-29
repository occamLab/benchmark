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

# combined_model_name = (
#     "training_ua-7c140933b99a14568ee768781fb5c9b2_ayush_mar_4_5_combined"
# )
# individual_model_names = [
#     "training_ua-7c140933b99a14568ee768781fb5c9b2_ayush_mar_4",
#     "training_ua-1bab71c5f9279e0777539be4abd6ae2b_ayush_mar_5",
# ]
model_names = [
    # 2:00 PM
    "training_ua-fde484ecee02694ad6ee5e87e7363785_ayush_april_5",
    # 10:00 PM
    "training_ua-2e324ef56fc8bb74e6c2271c4fa64870_ayush_april_7",
    # "training_ua-90ff6414f8f3669b1d685adc3f651e3d_ayush_mar_3",
    # "training_ua-7c140933b99a14568ee768781fb5c9b2_ayush_mar_4",
    # "training_ua-1bab71c5f9279e0777539be4abd6ae2b_ayush_mar_5",
    # "training_ua-2e1d4e33982d950fcc727486f41ac8ed_ayush_mar_6",
]
test_datasets = [
    # "training_ua-fde484ecee02694ad6ee5e87e7363785_ayush_april_5.tar",
    # "training_ua-2e324ef56fc8bb74e6c2271c4fa64870_ayush_april_7.tar",
    # # 9:30
    "testing_FE49EDB3-4A95-4B60-A942-5E41463DAEEF_ayush_mar_3.tar",
    # # 12:00
    "testing_7AAC6056-FEA5-4712-8134-26B13499316C_ayush_mar_3.tar",
    # # Days later
    # "testing_2E4723D2-57C7-4AA1-B3B3-CE276ABF0DC7_ayush_mar_3.tar",
    # # 4:30
    # "training_ua-90ff6414f8f3669b1d685adc3f651e3d_ayush_mar_3.tar",
]
model_test_pairs = [
    # # Test 2:00 AM
    # (
    #     "testing_79CB3863-8E05-41A4-92D1-9F9C9058AD38_ayush_mar_4",
    #     "training_ua-7c140933b99a14568ee768781fb5c9b2_ayush_mar_4",
    # ),
    # # Test 2:00 AM
    # (
    #     "testing_233A663A-0B1B-4B31-B6DD-C25570ED3D9C_ayush_mar_5",
    #     "training_ua-1bab71c5f9279e0777539be4abd6ae2b_ayush_mar_5",
    # ),
    # Test 12:00 PM
    (
        "testing_E5BD7C45-F682-49B6-A01F-5811DA3FDE5D_ayush_mar_4",
        "training_ua-7c140933b99a14568ee768781fb5c9b2_ayush_mar_4",
    ),
    # Test 12:00 PM
    (
        "testing_0666A135-8BB1-4100-97C2-BE2D2C2E38E8_ayush_mar_5",
        "training_ua-1bab71c5f9279e0777539be4abd6ae2b_ayush_mar_5",
    ),
]
# OUTPUT_BASE_DIR = Path(__file__).parent / ".cache/multi_model_results"
FIREBASE_DIR = Path(__file__).parent / ".cache/firebase_data"


# TODO: this shouldn't be needed in the new paradigm where the runner just picks
# a train set of weights and test tar to run
def main2():
    # for test_name in test_datasets:
    #     downloader = FirebaseDownloader(
    #         Path(test_name).parent, Path(test_name).parts[-1]
    #     )
    #     downloader.extract_ios_logger_tar()

    #     for model_name in model_names:
    for test_name, model_name in model_test_pairs:
        downloader = FirebaseDownloader(
            "iosLoggerDemo/tarQueue/",
            Path(test_name).parts[-1] + ".tar",
        )
        downloader.extract_ios_logger_tar()
        # if test_name[:-4] == model_name:
        #     continue
        results = process_testing_data(
            test_name,
            downloader,
            Path(__file__).parent / f".cache/firebase_data/{model_name}/ace",
        )
        res_dir = FIREBASE_DIR / model_name / "ace/test" / test_name[:-4]

        if not res_dir.exists():
            os.mkdir(res_dir)

        output_fp = res_dir / "results.json"
        with open(output_fp, "w") as file:
            json.dump(results, file, indent=4)
        # output_dir = OUTPUT_BASE_DIR / test_name.rstrip(".tar")
        # if not output_dir.exists():
        #     os.mkdir(output_dir)

        # output_fp = output_dir / "results.json"
        # with open(output_fp, "w") as file:
        #     json.dump(results_by_model, file, indent=4)


if __name__ == "__main__":
    # main()
    main2()
