from pathlib import Path
import json
from anchor.backend.eval.utils.data_models import (
    TestInfo,
    MapTestInfo,
    FrameData,
    TestDatum,
    MultiModelAnalysis,
)
from anchor.backend.data.firebase import FirebaseDownloader

import matplotlib.pyplot as plt
import argparse
import os
import math
import numpy as np

DATASET_INFO_PATH = Path(__file__).parent / "utils/dataset.json"
DATASET_MAPPINGS = {
    1: "ayush_mar_1",
    2: "ayush_mar_2",
    3: "ayush_mar_3",
    4: "ayush_mar_4",
    5: "ayush_mar_5",
    6: "ayush_mar_6",
    7: "ayush_mar_4_5_combined",
}
MULTI_MODEL_TEST_MAPPINGS = {
    # 9:30
    1: "testing_2E4723D2-57C7-4AA1-B3B3-CE276ABF0DC7_ayush_mar_3",
    # 12:00
    2: "testing_7AAC6056-FEA5-4712-8134-26B13499316C_ayush_mar_3",
    # Days later
    3: "testing_FE49EDB3-4A95-4B60-A942-5E41463DAEEF_ayush_mar_3",
    # 4:30
    4: "training_ua-90ff6414f8f3669b1d685adc3f651e3d_ayush_mar_3",
}
MULTI_MODEL_TEST_METADATA_MAPPINGS = {
    "testing_2E4723D2-57C7-4AA1-B3B3-CE276ABF0DC7_ayush_mar_3": "9:30 PM",
    "testing_7AAC6056-FEA5-4712-8134-26B13499316C_ayush_mar_3": "12:00 PM",
    "training_ua-90ff6414f8f3669b1d685adc3f651e3d_ayush_mar_3": "4:30 PM",
    "testing_FE49EDB3-4A95-4B60-A942-5E41463DAEEF_ayush_mar_3": "9:30 PM (Days Later)",
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
                test_info = TestInfo(data=None, error=None, **test)
                test_info.load_data()
                error = {
                    "ca_error": test_info.data.get_cloud_anchor_avg_translation_err(),
                    "ace_error": {
                        "raw": test_info.data.get_ace_avg_translation_errs(),
                        "smooth": test_info.data.get_ace_avg_translation_errs_smooth(),
                    },
                }
                num_frames = {
                    "ca_frames": test_info.data.num_cloud_anchor_poses,
                    "ace_frames": {
                        "raw": test_info.data.num_ace_frames_by_inliers,
                        "smooth": test_info.data.num_ace_frames_by_inliers_smooth,
                    },
                }
                json_data[map_name]["tests"][idx]["error"] = error
                json_data[map_name]["tests"][idx]["num_frames"] = num_frames
            except Exception as e:
                print(e)
                continue

    with open(DATASET_INFO_PATH, "w") as file:
        json.dump(json_data, file, indent=4)


def run_analysis():
    model_names = [
        # "training_ua-90ff6414f8f3669b1d685adc3f651e3d_ayush_mar_3",
        # "training_ua-7c140933b99a14568ee768781fb5c9b2_ayush_mar_4",
        # "training_ua-1bab71c5f9279e0777539be4abd6ae2b_ayush_mar_5",
        # "training_ua-2e1d4e33982d950fcc727486f41ac8ed_ayush_mar_6",
        "training_ua-fde484ecee02694ad6ee5e87e7363785_ayush_april_5",
        "training_ua-2e324ef56fc8bb74e6c2271c4fa64870_ayush_april_7",
    ]
    # model_names = [
    # "training_ua-90ff6414f8f3669b1d685adc3f651e3d_ayush_mar_3",
    # ]
    # test_names = MULTI_MODEL_TEST_METADATA_MAPPINGS.keys()
    test_names = [
        "training_ua-fde484ecee02694ad6ee5e87e7363785_ayush_april_5",
        "training_ua-2e324ef56fc8bb74e6c2271c4fa64870_ayush_april_7",
    ]

    data = {}

    for model in model_names:
        data[model] = {}
        for test in test_names:
            metadata = {}
            downloader = FirebaseDownloader(None, test)
            downloader.extract_ios_logger_tar()
            raw_data = downloader.extracted_data.sensors_extracted["localization_phase"]
            ca_data = raw_data["google_cloud_anchor"]
            results_json_path = (
                Path(__file__).parent.parent
                / "data/.cache/firebase_data"
                / model
                / "ace/test"
                / test
                / "results.json"
            )
            with open(results_json_path, "r") as file:
                results = json.load(file)
            if isinstance(results, dict) and "data" in results:
                results = results["data"]
            test_data = TestDatum(
                frames=[FrameData(**args) for args in results],
                root_dir=Path(__file__).parent.parent
                / "data/.cache/firebase_data"
                / model,
            )
            metadata["num_anchors"] = {
                "ace": test_data.num_ace_frames_by_inliers,
                "ca": len(ca_data),
            }
            try:
                timestamps = [
                    math.floor(f.timestamp * 100) / 100 for f in test_data.frames
                ]
                # TODO: fix cloud anchor indexing
                ca_indices = np.array(
                    [
                        timestamps.index(math.floor(x * 100) / 100)
                        for x in [x["timestamp"] for x in ca_data]
                    ]
                )
                frame_errs = np.array(
                    [
                        test_data.get_cloud_anchor_traslational_err_at_idx(
                            idx - test_data.cloud_anchor_start_idx
                        )
                        for idx in ca_indices
                    ]
                )

                metadata["trans_err_at_anchor"] = {
                    "ace": test_data.get_ace_avg_translation_errs(),
                    "ca": np.mean(frame_errs),
                }
                metadata["first_img"] = {
                    "ace": {
                        num_inliers: (
                            (
                                Path(__file__).parent.parent
                                / "data/.cache/firebase_data"
                                / test
                                / "ace/test/rgb"
                                / f"{int(np.where(test_data.inliers > num_inliers)[0][0]):05}.color.jpg"
                            )
                            .relative_to(Path.cwd())
                            .as_posix()
                            if len(np.where(test_data.inliers > num_inliers)[0] > 0)
                            else float("NaN")
                        )
                        for num_inliers in [0, 100, 200, 500, 1000]
                    },
                    "ca": (
                        (
                            Path(__file__).parent.parent
                            / "data/.cache/firebase_data"
                            / test
                            / "ace/test/rgb"
                            / f"{ca_indices[0]:05}.color.jpg"
                        )
                        .relative_to(Path.cwd())
                        .as_posix()
                    ),
                }
                metadata["rot_err_at_anchor"] = {
                    "ace": test_data.get_ace_average_rotation_errs(),
                    "ca": test_data.get_cloud_anchor_average_rotation_errs(ca_indices),
                }

                data[model][test] = metadata
                counts, bins = np.histogram(test_data.ace_translational_errors, bins=100, range=[0.0, 1.0])
                plt.stairs(counts, bins)
                plt.title(f"Test: {test}, Train: {model}")
                plt.xlabel("Error (m)")
                plt.ylabel("Counts")
                plt.savefig(Path(__file__).parent / f"{model}_{test}")
                plt.clf()
            except IndexError as e:
                breakpoint()
                continue
    # with open(Path(__file__).parent / "temp2_results.json", "w") as file:
        # json.dump(data, file, indent=4)


run_analysis()


def pose_comp(
    dataset_name: str, visualize: bool, save: bool, two_d: bool, smooth_ace: bool
):
    with open(DATASET_INFO_PATH, "r") as file:
        json_data = json.load(file)

    if dataset_name not in json_data:
        raise KeyError(f"Invalid map Name: {dataset_name}")

    map_data = json_data[dataset_name]
    map_data["tests"] = [TestInfo(data=None, **test) for test in map_data["tests"]]
    test_info = MapTestInfo(name=dataset_name, **map_data)
    test_info.load_all_data()

    inliers = 3000
    extrap = test_info.tests[0].data.get_ace_poses_extrap_by_inlier(inliers)

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1, projection="3d")
    ax.set_ylim([-0.5, 0.5])

    ax.scatter(extrap[:, 0, 3], extrap[:, 1, 3], extrap[:, 2, 3])
    ax.scatter(
        test_info.tests[0].data.arkit_poses[:, 0, 3],
        test_info.tests[0].data.arkit_poses[:, 1, 3],
        test_info.tests[0].data.arkit_poses[:, 2, 3],
    )
    if smooth_ace:
        ax.scatter(
            test_info.tests[0].data.get_ace_poses_extrap_by_inlier(inliers)[:, 0],
            test_info.tests[0].data.get_ace_poses_extrap_by_inlier(inliers)[:, 1],
            test_info.tests[0].data.get_ace_poses_extrap_by_inlier(inliers)[:, 2],
        )
    else:
        ax.scatter(
            test_info.tests[0].data.get_ace_translations_with_inlier_thresh(inliers)[
                :, 0
            ],
            test_info.tests[0].data.get_ace_translations_with_inlier_thresh(inliers)[
                :, 1
            ],
            test_info.tests[0].data.get_ace_translations_with_inlier_thresh(inliers)[
                :, 2
            ],
        )

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
                / f"{dataset_name}/{'2d' if two_d else '3d'}_pose_viz_{test.time_clean}{'_smooth' if smooth_ace else ''}"
            )
    plt.close()


def translational_bar_chart(
    dataset_name: str, visualize: bool, save: bool, smooth_ace: bool
):
    with open(DATASET_INFO_PATH, "r") as file:
        json_data = json.load(file)

    if dataset_name not in json_data:
        raise KeyError(f"Invalid map Name: {dataset_name}")

    map_data = json_data[dataset_name]

    fig = plt.figure()

    plt.rcParams.update({"font.size": 8})
    for idx, test in enumerate(map_data["tests"]):
        labels = ["CA"]
        heights = [test["error"]["ca_error"]]
        if smooth_ace:
            labels.extend(
                [f"{inlier}" for inlier in test["error"]["ace_error"]["smooth"]]
            )
            heights.extend(
                [err for err in test["error"]["ace_error"]["smooth"].values()]
            )
        else:
            labels.extend([f"{inlier}" for inlier in test["error"]["ace_error"]["raw"]])
            heights.extend([err for err in test["error"]["ace_error"]["raw"].values()])

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
        plt.savefig(
            FIGURE_DIR
            / f"{dataset_name}/trans_err_bar{'_smooth' if smooth_ace else ''}"
        )

    plt.close()


def frame_bar_chart(dataset_name: str, visualize: bool, save: bool, smooth_ace: bool):
    with open(DATASET_INFO_PATH, "r") as file:
        json_data = json.load(file)

    if dataset_name not in json_data:
        raise KeyError(f"Invalid map Name: {dataset_name}")

    map_data = json_data[dataset_name]

    fig = plt.figure()

    plt.rcParams.update({"font.size": 8})
    for idx, test in enumerate(map_data["tests"]):
        labels = ["CA"]
        heights = [test["num_frames"]["ca_frames"]]

        if smooth_ace:
            labels.extend(
                [f"{inlier}" for inlier in test["num_frames"]["ace_frames"]["smooth"]]
            )
            heights.extend(
                [err for err in test["num_frames"]["ace_frames"]["smooth"].values()]
            )
        else:
            labels.extend(
                [f"{inlier}" for inlier in test["num_frames"]["ace_frames"]["raw"]]
            )
            heights.extend(
                [err for err in test["num_frames"]["ace_frames"]["raw"].values()]
            )

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
        plt.savefig(
            FIGURE_DIR
            / f"{dataset_name}/num_frames_bar{'_smooth' if smooth_ace else ''}"
        )

    plt.close()


def analyze_multi_model_datasets(dataset_name, visualize: bool, save: bool):
    data_file = (
        Path(__file__).parent.parent
        / "data/.cache/multi_model_results"
        / dataset_name
        / "results.json"
    )
    with open(data_file, "r") as file:
        results = json.load(file)

    for model_name, data in results.items():
        results[model_name] = TestDatum(
            frames=[FrameData(**args) for args in data],
            root_dir=Path(__file__).parent.parent
            / "data/.cache/firebase_data"
            / model_name,
        )

    mm_analyzer = MultiModelAnalysis(results)

    fig = plt.figure()

    plt.rcParams.update({"font.size": 8})
    ax = fig.add_subplot(2, 2, 1)
    independent_trans_errs = mm_analyzer.independent_avg_translation_errs
    ax.bar(
        [str(int(x)) for x in independent_trans_errs[:, 0]],
        independent_trans_errs[:, 1],
    )
    ax.set_title("Independent Models Stitched Together", y=0.97)
    ax.set_ylim(0, 2)
    ax.set_ylabel("Error (m)")
    # ax.set_xlabel("Inlier Count")

    labels = []
    heights = []
    ax = fig.add_subplot(2, 2, 2)
    independent_trans_errs = mm_analyzer.combined_avg_translation_errs
    labels.extend([str(int(x)) for x in independent_trans_errs.keys()])
    heights.extend(independent_trans_errs.values())
    ax.bar(
        labels,
        heights,
    )
    ax.set_title("Combined Model", y=0.97)
    ax.set_ylim(0, 2)
    ax.set_ylabel("Error (m)")
    # ax.set_xlabel("Inlier Count")

    labels = []
    heights = []
    ax = fig.add_subplot(2, 2, 3)
    independent_trans_errs = mm_analyzer.model0_avg_translation_errs
    labels.extend([str(int(x)) for x in independent_trans_errs.keys()])
    heights.extend(independent_trans_errs.values())
    ax.bar(
        labels,
        heights,
    )
    ax.set_title("Model 0 (Recorded 9:30 PM)", y=0.97)
    ax.set_ylim(0, 2)
    ax.set_ylabel("Error (m)")
    # ax.set_xlabel("Inlier Count")

    labels = []
    heights = []
    ax = fig.add_subplot(2, 2, 4)
    independent_trans_errs = mm_analyzer.model1_avg_translation_errs
    labels.extend([str(int(x)) for x in independent_trans_errs.keys()])
    heights.extend(independent_trans_errs.values())
    ax.bar(
        labels,
        heights,
    )
    ax.set_title("Model 1 (Recorded 12:00 PM)", y=0.97)
    ax.set_ylim(0, 2)
    ax.set_ylabel("Error (m)")
    # ax.set_xlabel("Inlier Count")

    plt.suptitle(
        f"Translational Error of Various Multi-Time Models\nTest: {MULTI_MODEL_TEST_METADATA_MAPPINGS[dataset_name]}",
        fontsize=12,
        y=0.99,
    )

    if save:
        plt.savefig(
            FIGURE_DIR / f"multimodel/{dataset_name.split('_')[1]}/trans_err_bar"
        )

    if visualize:
        plt.show()

    plt.close()

    fig = plt.figure()

    plt.rcParams.update({"font.size": 8})
    ax = fig.add_subplot(2, 2, 1)
    independent_trans_errs = mm_analyzer.independent_num_frames
    ax.bar(
        [str(int(x)) for x in independent_trans_errs[:, 0]],
        independent_trans_errs[:, 1],
    )
    ax.set_title("Independent Models Stitched Together", y=0.97)
    ax.set_ylabel("Num Frames")
    # ax.set_xlabel("Inlier Count")

    labels = []
    heights = []
    ax = fig.add_subplot(2, 2, 2)
    independent_trans_errs = mm_analyzer.combined_num_frames
    labels.extend([str(int(x)) for x in independent_trans_errs.keys()])
    heights.extend(independent_trans_errs.values())
    ax.bar(
        labels,
        heights,
    )
    ax.set_title("Combined Model", y=0.97)
    ax.set_ylabel("Num Frames")
    # ax.set_xlabel("Inlier Count")

    labels = []
    heights = []
    ax = fig.add_subplot(2, 2, 3)
    independent_trans_errs = mm_analyzer.model0_num_frames
    labels.extend([str(int(x)) for x in independent_trans_errs.keys()])
    heights.extend(independent_trans_errs.values())
    ax.bar(
        labels,
        heights,
    )
    ax.set_title("Model 0 (Recorded 9:30 PM)", y=0.97)
    ax.set_ylabel("Num Frames")
    # ax.set_xlabel("Inlier Count")

    labels = []
    heights = []
    ax = fig.add_subplot(2, 2, 4)
    independent_trans_errs = mm_analyzer.model1_num_frames
    labels.extend([str(int(x)) for x in independent_trans_errs.keys()])
    heights.extend(independent_trans_errs.values())
    ax.bar(
        labels,
        heights,
    )
    ax.set_title("Model 1 (Recorded 12:00 PM)", y=0.97)
    ax.set_ylabel("Num Frames")
    # ax.set_xlabel("Inlier Count")

    plt.suptitle(
        f"Translational Error of Various Multi-Time Models\nTest: {MULTI_MODEL_TEST_METADATA_MAPPINGS[dataset_name]}",
        fontsize=12,
        y=0.99,
    )

    if save:
        plt.savefig(FIGURE_DIR / f"multimodel/{dataset_name.split('_')[1]}/frame_bar")

    if visualize:
        plt.show()


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
    parser.add_argument(
        "-smooth",
        help="Run Smoothing algorithm on ACE poses to better compare against cloud anchors",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-mm", help="Run multi-model comparisons", action="store_true", default=False
    )

    args = parser.parse_args()

    if not (dataset_name := DATASET_MAPPINGS.get(args.map_num)) or not (
        dataset_name := MULTI_MODEL_TEST_MAPPINGS.get(args.map_num)
    ):
        raise ValueError(f"Invalid Map Number: {args.map_num}")
    datasets = [dataset_name]
    if args.all_maps:
        if args.mm:
            datasets = MULTI_MODEL_TEST_MAPPINGS.values()
        else:
            datasets = DATASET_MAPPINGS.values()

    if args.um:
        append_test_stats()

    for dataset_name in datasets:
        if args.s and not (FIGURE_DIR / dataset_name).exists() and not args.mm:
            os.mkdir(FIGURE_DIR / dataset_name)
        if (
            args.s
            and args.mm
            and not (
                dir := FIGURE_DIR / f"multimodel/{dataset_name.split('_')[1]}"
            ).exists()
        ):
            os.mkdir(dir)

        if args.pose:
            pose_comp(
                dataset_name=dataset_name,
                visualize=args.v,
                save=args.s,
                two_d=args.twod,
                smooth_ace=args.smooth,
            )
        if args.bar_t:
            translational_bar_chart(
                dataset_name=dataset_name,
                visualize=args.v,
                save=args.s,
                smooth_ace=args.smooth,
            )
        if args.bar_f:
            frame_bar_chart(
                dataset_name=dataset_name,
                visualize=args.v,
                save=args.s,
                smooth_ace=args.smooth,
            )

        if args.mm:
            analyze_multi_model_datasets(
                dataset_name=dataset_name,
                visualize=args.v,
                save=args.s,
            )
