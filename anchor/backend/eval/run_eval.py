from pathlib import Path
import json
from utils.error import compute_rotational_error, compute_translation_error
from utils.data_models import TestInfo, MapTestInfo
import matplotlib.pyplot as plt
import argparse
import os

DATASET_INFO_PATH = Path(__file__).parent / "utils/dataset.json"
DATASET_MAPPINGS = {
    1: "ayush_mar_1",
    2: "ayush_mar_2",
    3: "ayush_mar_3",
    4: "ayush_mar_4",
    5: "ayush_mar_5",
    6: "ayush_mar_6",
}
FIGURE_DIR = Path(__file__).parent / "imgs"


def append_test_stats():
    with open(DATASET_INFO_PATH, "r") as file:
        json_data = json.load(file)

    for map_name, map_data in json_data.items():
        for idx, test in enumerate(map_data["tests"]):
            try:
                if "error" in test:
                    del test["error"]
                test_info = TestInfo(data=None, **test)
                test_info.load_data()
                error = {
                    "ca_error": test_info.data.get_cloud_anchor_avg_translation_err(),
                    "ace_error": test_info.data.get_ace_avg_translation_errs(),
                }
                num_frames = {
                    "ca_frames": test_info.data.num_cloud_anchor_poses,
                    "ace_frames": test_info.data.num_ace_frames_by_inliers,
                }
                json_data[map_name]["tests"][idx]["error"] = error
                json_data[map_name]["tests"][idx]["num_frames"] = num_frames
            except Exception as e:
                print(e)
                continue

    with open(DATASET_INFO_PATH, "w") as file:
        json.dump(json_data, file, indent=4)


def pose_comp(dataset_name: str, visualize: bool, save: bool, two_d: bool):
    with open(DATASET_INFO_PATH, "r") as file:
        json_data = json.load(file)

    if dataset_name not in json_data:
        raise KeyError(f"Invalid map Name: {dataset_name}")

    map_data = json_data[dataset_name]
    map_data["tests"] = [TestInfo(data=None, **test) for test in map_data["tests"]]
    test_info = MapTestInfo(name=dataset_name, **map_data)
    test_info.load_all_data()

    plt.rcParams.update({"font.size": 7})

    for test in test_info.tests:
        data = test.data
        fig = plt.figure()
        if two_d:
            data.plot_2d_data(fig)
        else:
            data.plot_3d_data(fig)
        plt.suptitle(
            f"Pose Visualization - Map: {dataset_name} - Test Time: {test.time}",
            fontsize=12,
        )
        if visualize:
            plt.show()
        if save:
            plt.savefig(
                FIGURE_DIR
                / f"{dataset_name}/{'2d' if two_d else '3d'}_pose_viz_{test.time_clean}"
            )
    plt.close()


def translational_bar_chart(dataset_name: str, visualize: bool, save: bool):
    with open(DATASET_INFO_PATH, "r") as file:
        json_data = json.load(file)

    if dataset_name not in json_data:
        raise KeyError(f"Invalid map Name: {dataset_name}")

    map_data = json_data[dataset_name]

    fig = plt.figure()

    plt.rcParams.update({"font.size": 8})
    for idx, test in enumerate(map_data["tests"]):
        labels = ["CA"]
        labels.extend([f"{inlier}" for inlier in test["error"]["ace_error"]])
        heights = [test["error"]["ca_error"]]

        heights.extend([err for err in test["error"]["ace_error"].values()])

        ax = fig.add_subplot(2, 2, idx + 1)
        ax.bar(labels, heights)
        ax.set_title(f"{test['time']} PM", y=0.97, fontsize=10)
    plt.suptitle(
        "Translational Error of CA vs. ACE By Inlier Count \n(Missing Inlier Counts Resolved 0 Poses)",
        fontsize=12,
        y=0.99,
    )
    if visualize:
        plt.show()

    if save:
        plt.savefig(FIGURE_DIR / f"{dataset_name}/trans_err_bar")

    plt.close()


def frame_bar_chart(dataset_name: str, visualize: bool, save: bool):
    with open(DATASET_INFO_PATH, "r") as file:
        json_data = json.load(file)

    if dataset_name not in json_data:
        raise KeyError(f"Invalid map Name: {dataset_name}")

    map_data = json_data[dataset_name]

    fig = plt.figure()

    plt.rcParams.update({"font.size": 8})
    for idx, test in enumerate(map_data["tests"]):
        labels = ["CA"]
        labels.extend([f"{inlier}" for inlier in test["num_frames"]["ace_frames"]])
        heights = [test["num_frames"]["ca_frames"]]

        heights.extend([err for err in test["num_frames"]["ace_frames"].values()])

        ax = fig.add_subplot(2, 2, idx + 1)
        ax.bar(labels, heights)
        ax.set_title(f"{test['time']} PM", y=0.97, fontsize=10)
    plt.suptitle(
        "Num Frames Resolved by CA vs. ACE By Inlier Count",
        fontsize=12,
        y=0.99,
    )
    if visualize:
        plt.show()

    if save:
        plt.savefig(FIGURE_DIR / f"{dataset_name}/num_frames_bar")

    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Visualize ACE Comparisons",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-v", help="visualize figures", action="store_true", default=False
    )
    parser.add_argument("-s", help="save figure", action="store_true", default=False)
    parser.add_argument(
        "-um", help="update metadata", action="store_true", default=False
    )
    parser.add_argument(
        "-pose", help="visualize pose comparisons", action="store_true", default=False
    )
    parser.add_argument(
        "-bar_t",
        help="visualize bar chart of translational error comparisons",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-bar_f",
        help="visualize bar chart of number of frames resolved by each method",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-map_num", type=int, help="Map Number as they appear in `README.md`", default=1
    )
    parser.add_argument(
        "-all_maps",
        help="Run the user-specified analysis on all maps",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-twod", help="Plot 2D Mapping of Poses", action="store_true", default=True
    )

    args = parser.parse_args()

    if not (dataset_name := DATASET_MAPPINGS.get(args.map_num)):
        raise ValueError(f"Invalid Map Number: {args.map_num}")
    datasets = [dataset_name]
    if args.all_maps:
        datasets = DATASET_MAPPINGS.values()

    if args.um:
        append_test_stats()

    for dataset_name in datasets:
        if args.s and not (FIGURE_DIR / dataset_name).exists():
            os.mkdir(FIGURE_DIR / dataset_name)

        if args.pose:
            pose_comp(
                dataset_name=dataset_name,
                visualize=args.v,
                save=args.s,
                two_d=args.twod,
            )
        if args.bar_t:
            translational_bar_chart(
                dataset_name=dataset_name, visualize=args.v, save=args.s
            )
        if args.bar_f:
            frame_bar_chart(dataset_name=dataset_name, visualize=args.v, save=args.s)
