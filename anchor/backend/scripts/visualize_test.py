import argparse
from pathlib import Path
import os
import json
from typing import List
import numpy as np
import matplotlib.pyplot as plt
from eval.utils.data_models import FrameData, TestDatum

import shutil

TEST_NAME = "testing_8E1E9222-15B0-4BDD-B9B1-3922F88E2B4B_ayush_nov30_1"
TEST_TIME = None
DATA_DIR = Path(__file__).parent.parent / "data/.cache/firebase_data"
TEST_DIR = DATA_DIR / f"{TEST_NAME}/ace/test"


def load_cache_data() -> TestDatum:
    exclusion_dirs = ["calibration", "poses", "rgb", "annotated_rgb"]
    if TEST_TIME:
        curr_test_inst_dir = TEST_DIR / TEST_TIME
    else:
        test_instances = [
            y for y in [x for x in os.walk(TEST_DIR)][0][1] if y not in exclusion_dirs
        ]
        if len(test_instances) != 1:
            raise ValueError(
                f"Multiple test instances found for {TEST_NAME}. Specify a specific time. Instances found: {', '.join(test_instances)}"
            )
        curr_test_inst_dir = TEST_DIR / test_instances[0]

    mapped_json_fp = curr_test_inst_dir / "mapped_poses.json"
    if not mapped_json_fp.exists():
        raise ValueError("Rerun ACE Testing, the results JSON was not generated.")

    with open(mapped_json_fp, "r") as file:
        data = json.load(file)["data"]

    frames = [FrameData(**frame) for frame in data]
    test_data = TestDatum(frames=frames, root_dir=curr_test_inst_dir)
    return test_data


def visualize_graph(inlier_thresholds: List[int]):
    test_data = load_cache_data()
    for inlier_thresh in inlier_thresholds:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        filt_ace_poses = test_data.get_ace_translations_with_inlier_thresh(
            inlier_thresh
        )
        ax.scatter(
            filt_ace_poses[:, 0],
            filt_ace_poses[:, 1],
            filt_ace_poses[:, 2],
            label="ACE",
            marker="x",
        )
        ax.scatter(
            test_data.arkit_translations[:, 0],
            test_data.arkit_translations[:, 1],
            test_data.arkit_translations[:, 2],
            label="ARKIT",
            marker="o",
        )

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.legend()

        plt.suptitle(f"ACE vs. ARKIT Poses (Inlier Thresh: {inlier_thresh})")
        ax.set_title(
            f"Ace Resolved {np.shape(filt_ace_poses)[0]}/{np.shape(test_data.arkit_translations)[0]} Frames"
        )

        ax.view_init(elev=0, azim=90)
        plt.show()


def step_graph(
    inlier_thresh: int = 0,
    step_fps: int = 1,
    annotated_frames=False,
    save=True,
):
    test_data = load_cache_data()
    viz_datums = test_data.get_viz_frames(step_fps, annotated_frames)
    if save:
        save_dir = test_data.root_dir / "step_images"
        if save_dir.exists():
            shutil.rmtree(save_dir)
        os.mkdir(save_dir)

    for idx, viz_datum in enumerate(viz_datums):
        plt.suptitle(
            f"Frame: {viz_datum.frame_num}, Inlier Count: {viz_datum.inlier_count}"
        )
        plt.title(f"Translational Error: {viz_datum.t_err}m")
        plt.imshow(viz_datum.img_rgb)
        if save:
            plt.savefig(save_dir / f"{viz_datum.frame_num}.jpg")
            print(f"Generated Image {idx+1}/{len(viz_datums)}")
        else:
            plt.show()


def counts_splitter(arg):
    return [int(x) for x in arg.split(",")]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Visualize ACE Data results",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-v", help="visualize graph", action="store_true", default=False
    )
    parser.add_argument(
        "-in_count", type=int, help="Number of inliers to filter ACE with", default=0
    )
    parser.add_argument(
        "-in_counts",
        type=counts_splitter,
        help="List of inlier thresholds to filter ACE with",
        default=None,
    )
    parser.add_argument(
        "-step",
        help="Step through the images of a test",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-save_step",
        help="Save step images",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-step_size",
        type=float,
        help="Frames per second while stepping through a test",
        default=1,
    )
    parser.add_argument(
        "-ann_frames",
        help="Use images annotated with inliers when stepping through a dataset",
        action="store_true",
        default=False,
    )
    args = parser.parse_args()

    if args.v:
        if args.in_count is not None and args.in_counts is not None:
            raise ValueError(
                "Cannot specify 'in_count' and 'in_counts' at the same time."
            )
        if args.in_count is not None:
            inliers = [args.in_count]
        elif args.in_counts is not None:
            inliers = args.in_counts
        else:
            raise ValueError("Must specify either 'in_count' or 'in_counts'")
        visualize_graph(inlier_thresholds=inliers)
    if args.step:
        if args.in_counts:
            raise ValueError(
                "Cannot step through a test with multiple inliers, please choose one."
            )
        step_graph(
            inlier_thresh=args.in_count,
            step_fps=args.step_size,
            save=args.save_step,
            annotated_frames=args.ann_frames,
        )
