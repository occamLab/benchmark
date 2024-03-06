from pathlib import Path
import json
from utils.error import compute_rotational_error, compute_translation_error
from utils.data_models import TestInfo, MapTestInfo
import matplotlib.pyplot as plt
import argparse

DATASET_INFO_PATH = Path(__file__).parent / "utils/dataset.json"
DATASET_NAME = "ayush_mar_1"
DATASET_MAPPINGS = {
    1: "ayush_mar_1",
    2: "ayush_mar_2",
    3: "ayush_mar_3",
    4: "ayush_mar_4",
    5: "ayush_mar_5",
}

def append_test_stats():
    with open(DATASET_INFO_PATH, "r") as file:
        json_data = json.load(file)

    if DATASET_NAME not in json_data:
        raise KeyError(f"Invalid map Name: {DATASET_NAME}")

    for map_name, map_data in json_data.items():
        for idx, test in enumerate(map_data["tests"]):
            if "error" not in test:
                test_info = TestInfo(data=None, **test)
                test_info.load_data()
                error = {
                    "ca_error": test_info.data.get_cloud_anchor_avg_translation_err(),
                    "ace_error": test_info.data.get_ace_avg_translation_errs()
                }
                json_data[map_name]["tests"][idx]["error"] = error
    
    with open(DATASET_INFO_PATH, "w") as file:
        json.dump(json_data, file)


def pose_comp(dataset_name: str, visualize: bool, save: bool):
    with open(DATASET_INFO_PATH, "r") as file:
        json_data = json.load(file)

    if dataset_name not in json_data:
        raise KeyError(f"Invalid map Name: {dataset_name}")

    map_data = json_data[dataset_name]
    map_data["tests"] = [TestInfo(data=None, **test) for test in map_data["tests"]]
    test_info = MapTestInfo(name=dataset_name, **map_data)
    test_info.load_all_data()
    
    
    data = test_info.tests[0].data
    fig = plt.figure()
    data.plot_data(fig)
    plt.show()

def bar_comp(dataset_name: str, visualize: bool, save: bool):
    with open(DATASET_INFO_PATH, "r") as file:
        json_data = json.load(file)

    if dataset_name not in json_data:
        raise KeyError(f"Invalid map Name: {dataset_name}")

    map_data = json_data[dataset_name]

    fig = plt.figure()
        for idx, test in enumerate(map_data["tests"]):
            labels = ["CA"]
            labels.extend([f"ACE:{inlier}" for inlier in test["error"]["ace_error"]])
            heights = [test["error"]["cloud_anchor_error"]]

            heights.extend([err for err in test["error"]["ace_error"].values()])

            ax = fig.add_subplot(2, 3, idx + 1)
            ax.bar(labels, heights)
            ax.title(test["time"])

    if args.v:
        plt.show()

    # if args.s:
        # plt.save()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Visualize ACE Comparisons",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-v", help="visualize figures", action="store_true", default=False
    )
    parser.add_argument(
        "-s", help="save figure", action="store_true", default=False
    )
    parser.add_argument(
        "-um", help="update metadata", action="store_true", default=False
    )
    parser.add_argument(
        "-pose", help="visualize pose comparisons", action="store_true", default=False 
    )
    parser.add_argument(
        "-bar", help="visualize bar chart comparisons", action="store_true", default=False
    )
    parser.add_argument(
        "-map_num",
        type=int,
        help="Map Number as they appear in `README.md`",
        default=1
    )

    args = parser.parse_args()

    if not (dataset_name := DATASET_MAPPINGS.get(args.map_num)):
        raise ValueError(f"Invalid Map Number: {args.map_num}")
    
    if args.um:
        append_test_stats()
    if args.pose:
        pose_comp(dataset_name=dataset_name, visualize=args.v, save=args.s)
    if args.bar:
        bar_comp(dataset_name=dataset_name, visualize=args.v, save=args.s)