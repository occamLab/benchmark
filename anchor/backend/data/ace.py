from pathlib import Path
from anchor.backend.data.extracted import Extracted
from anchor.backend.data.firebase import FirebaseDownloader, list_tars
from anchor.backend.data.error_summarizer import ErrorSummarizer
from anchor.third_party.ace.ace_network import Regressor
from torch.utils.mobile_optimizer import optimize_for_mobile, MobileOptimizerType
import shutil
import sys
import subprocess
import os
import torch
import tempfile
from dataclasses import dataclass
from scipy.spatial.transform import Rotation as R
import numpy as np
import json


def prepare_ace_data(extracted_data: Extracted):
    map_phase_to_ace_folder = {"mapping_phase": "train", "localization_phase": "test"}

    for phase in extracted_data.sensors_extracted:
        if not extracted_data.sensors_extracted[phase]["video"]:
            continue
        for data in extracted_data.sensors_extracted[phase]["video"]:
            ace_input = extracted_data.extract_root / "ace"
            write_location = ace_input / map_phase_to_ace_folder[phase]
            write_location.mkdir(parents=True, exist_ok=True)

            # copy the image itself
            dest_img_path = (
                write_location / "rgb" / (f'{data["frame_num"]:05}' + ".color.jpg")
            )
            dest_img_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(data["frame_path"], dest_img_path)

            # copy the intrinsics information
            dest_intrinsics_path = (
                write_location
                / "calibration"
                / (f'{data["frame_num"]:05}' + ".calibration.txt")
            )
            dest_intrinsics_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_intrinsics_path, "w") as intrinsics_file:
                intrinsics_data = data["intrinsics"]
                intrinsics_file.write(
                    f'{intrinsics_data["fx"]} 0 {intrinsics_data["cx"]}\n'
                    + f'0 {intrinsics_data["fy"]} {intrinsics_data["cy"]}\n'
                    + f"0 0 1\n"
                )

            # copy the pose information
            dest_pose_path = (
                write_location / "poses" / (f'{data["frame_num"]:05}' + ".pose.txt")
            )
            dest_pose_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_pose_path, "w") as pose_file:
                pose_data = data["poses"]["rotation_matrix"]
                pose_file.write(
                    f"{pose_data[0]} {pose_data[4]} {pose_data[8]} {pose_data[12]}\n"
                    + f"{pose_data[1]} {pose_data[5]} {pose_data[9]} {pose_data[13]}\n"
                    + f"{pose_data[2]} {pose_data[6]} {pose_data[10]} {pose_data[14]}\n"
                    + f"{pose_data[3]} {pose_data[7]} {pose_data[11]} {pose_data[15]}"
                )


def calculate_google_cloud_anchor_quality(extracted_data: Extracted):
    error_summarizer = ErrorSummarizer()
    ground_truth_location = extracted_data.sensors_extracted[
        Extracted.get_phase_key(True)
    ]["google_cloud_anchor"]["anchor_host_rotation_matrix"]
    for value in extracted_data.sensors_extracted[Extracted.get_phase_key(False)][
        "google_cloud_anchor"
    ]:
        error_summarizer.observe_pose(
            value["anchor_rotation_matrix"], ground_truth_location
        )
    error_summarizer.print_statistics()


""" 
    Converts the ACE model for mobile usage
"""


def save_model_for_mobile(ace_encoder_pretrained: Path, trained_weights: Path):
    encoder_state_dict = torch.load(ace_encoder_pretrained, map_location="cpu")
    head_network_dict = torch.load(trained_weights, map_location="cpu")

    device = torch.device("cuda")
    network = Regressor.create_from_split_state_dict(
        encoder_state_dict, head_network_dict
    )
    network = network.to(device)
    network.eval()

    scripted_module = torch.jit.script(network)
    # it looks it's not trivial to optimize for mobile gpu right because this issue: https://github.com/pytorch/pytorch/issues/69609
    optimized_model = optimize_for_mobile(scripted_module, backend="CPU")
    optimized_model.save(trained_weights.parent / "mobile.model.pt")
    optimized_model._save_for_lite_interpreter(
        (trained_weights.parent / "mobile.model.ptl").as_posix()
    )


"""
Runs the ace evaluator on the trained model. To run paste the following into main:
run_ace_evaluator(extracted_ace_folder, model_output, visualizer_enabled, render_flipped_portrait, render_target_path)
"""


def run_ace_evaluator(
    extracted_ace_folder: Path,
    model_output: Path,
    visualizer_enabled: bool,
    render_flipped_portrait: bool,
    render_target_path: Path,
    frame_exclusion=400,
):
    print("[INFO]: Running ace evaluater on dataset path: ", extracted_ace_folder)
    # TODO: thsi doesn't handle spaces properly
    subprocess.run(
        [
            "./test_ace.py",
            extracted_ace_folder.as_posix(),
            model_output.as_posix(),
            "--render_visualization",
            str(visualizer_enabled),
            "--render_flipped_portrait",
            str(render_flipped_portrait),
            "--render_target_path",
            render_target_path.as_posix(),
            "--frame_exclusion_threshold",
            str(frame_exclusion),
        ]
    )


def process_localization_phase(
    combined_path: str,
    downloader: FirebaseDownloader,
    ace_test_pose_file: str,
    from_mapping: bool = False,
):
    poses = []
    header = [
        "frame_num",
        "q_w",
        "q_x",
        "q_y",
        "q_z",
        "t_x",
        "t_y",
        "t_z",
        "r_err",
        "t_err",
        "inlier_counter",
    ]

    current_cloud_anchor_idx = 0
    ca_poses_by_timestamp = {}

    if downloader.extracted_data.sensors_extracted["localization_phase"][
        "google_cloud_anchor"
    ]:
        for pose in downloader.extracted_data.sensors_extracted["localization_phase"][
            "poses"
        ]:
            # Skip ARKIT Poses before first Cloud Anchor Detection
            if (
                downloader.extracted_data.sensors_extracted["localization_phase"][
                    "google_cloud_anchor"
                ][0]["timestamp"]
                > pose["timestamp"]
            ):
                continue
            homogeneous_pose = np.reshape(pose["rotation_matrix"], [4, 4], order="F")
            if not current_cloud_anchor_idx == len(
                downloader.extracted_data.sensors_extracted["localization_phase"][
                    "google_cloud_anchor"
                ]
            ) - 1 and (
                pose["timestamp"]
                >= downloader.extracted_data.sensors_extracted["localization_phase"][
                    "google_cloud_anchor"
                ][current_cloud_anchor_idx + 1]["timestamp"]
            ):
                current_cloud_anchor_idx += 1

            cloud_anchor_pose = np.reshape(
                downloader.extracted_data.sensors_extracted["localization_phase"][
                    "google_cloud_anchor"
                ][current_cloud_anchor_idx]["anchor_rotation_matrix"],
                [4, 4],
                order="F",
            )
            ca_poses_by_timestamp[pose["timestamp"]] = np.reshape(
                homogeneous_pose @ np.linalg.inv(cloud_anchor_pose), 16, order="F"
            )

    with open(ace_test_pose_file, "r") as file:
        for line in file.readlines():
            data = line.strip("\n").split(" ")
            data[0] = int(data[0].split(".")[0])
            ace_pose = PoseData(
                **{header[i]: data[i] for i in range(len(header))}
            ).as_matrix
            timestamp = downloader.extracted_data.sensors_extracted[
                "localization_phase"
            ]["poses"][data[0]]["timestamp"]
            arkit_pose = downloader.extracted_data.sensors_extracted[
                "localization_phase"
            ]["poses"][data[0]]["rotation_matrix"]
            ca_pose = ca_poses_by_timestamp.get(timestamp)
            poses.append(
                {
                    "frame_num": data[0],
                    "timestamp": timestamp,
                    "ACE": list(ace_pose),
                    "ARKIT": list(arkit_pose),
                    "CLOUD_ANCHOR": list(ca_pose) if ca_pose is not None else [],
                }
            )

    tmp_pose_path = Path(__file__).parent / ".cache/jsons/temp_pose_data.json"
    with open(tmp_pose_path, "w") as file:
        json.dump({"data": poses}, file, indent=4)

    print("[INFO]: Uploading processed JSON to firebase")
    firebase_processed_json_path: str = (
        Path(combined_path).parent.parent
        / f"processedJsons/{Path(downloader.tar_name).stem}.json"
    )
    downloader.upload_file(firebase_processed_json_path.as_posix(), tmp_pose_path)

    if len(sys.argv) != 2 and not from_mapping:
        firebase_tar_queue_path: str = Path(combined_path).parent
        firebase_processed_tar_path: str = str(
            Path(combined_path).parent.parent / f"processedTestTars/{tar_name}"
        )
        downloader.delete_file((Path(firebase_tar_queue_path) / tar_name).as_posix())
        downloader.upload_file(
            remote_location=firebase_processed_tar_path,
            local_location=downloader.local_tar_location,
        )
        print(
            "[INFO]: Moved tar from tarQueue to processedTestTars directory in firebase"
        )


def process_training_data(combined_path: str, downloader: FirebaseDownloader):
    prepare_ace_data(downloader.extracted_data)

    # TODO: fix cloud anchor analysis
    # print("[INFO]: Summarizing google cloud anchor observations: ")
    # calculate_google_cloud_anchor_quality(downloader.extracted_data)

    extracted_ace_folder = downloader.local_extraction_location / "ace"
    model_output = extracted_ace_folder / "model.pt"
    render_target_path = extracted_ace_folder / "debug_visualizer"
    render_target_path.mkdir(parents=True, exist_ok=True)
    pretrained_model = (
        Path(__file__).parent.parent.parent
        / "third_party"
        / "ace"
        / "ace_encoder_pretrained.pt"
    )
    visualizer_enabled = False
    render_flipped_portrait = False
    training_epochs = 8

    print("[INFO]: Running ace training on dataset path: ", extracted_ace_folder)
    os.chdir(Path(__file__).parent.parent.parent / "third_party/ace")
    subprocess.run(
        [
            "./train_ace.py",
            extracted_ace_folder.as_posix(),
            model_output.as_posix(),
            "--render_visualization",
            str(visualizer_enabled),
            "--render_flipped_portrait",
            str(render_flipped_portrait),
            "--render_target_path",
            render_target_path.as_posix(),
            "--epochs",
            str(training_epochs),
        ]
    )

    print("[INFO]: Running ace evaluation on dataset path: ", extracted_ace_folder)
    run_ace_evaluator(
        extracted_ace_folder, model_output, False, True, extracted_ace_folder
    )

    print("[INFO]: Converting ACE model for mobile use")
    save_model_for_mobile(pretrained_model, model_output)

    firebase_upload_dir = "iosLoggerDemo/trainedModels/"
    vid_name = Path(tar_name)
    vid_name = vid_name.stem.split("training_")[-1] + ".pt"
    firebase_upload_path = Path(firebase_upload_dir) / Path(vid_name)
    print("[INFO]: Saving model to firebase as {}".format(firebase_upload_path))
    downloader.upload_file(firebase_upload_path.as_posix(), model_output)

    if len(sys.argv) != 2:
        firebase_tar_queue_path: str = Path(combined_path).parent
        firebase_processed_tar_path: str = str(
            Path(combined_path).parent.parent / f"processedTrainingTars/{tar_name}"
        )
        downloader.delete_file((Path(firebase_tar_queue_path) / tar_name).as_posix())
        downloader.upload_file(
            remote_location=firebase_processed_tar_path,
            local_location=downloader.local_tar_location,
        )
        print("[INFO]: Moved tar from tarQueue to processedTars directory in firebase")

    ace_test_pose_file = (
        downloader.root_download_dir / f"{Path(tar_name).stem}/ace/poses_ace_.txt"
    )
    process_localization_phase(combined_path, downloader, ace_test_pose_file, True)

    if visualizer_enabled:
        subprocess.run(
            [
                "/usr/bin/ffmpeg",
                "-framerate",
                "30",
                "-pattern_type",
                "glob",
                "-i",
                f"{render_target_path.as_posix()}/**/*.png",
                "-c:v",
                "libx264",
                "-pix_fmt",
                "yuv420p",
                f"{render_target_path.as_posix()}/out.mp4",
            ]
        )


@dataclass
class PoseData:
    frame_num: int
    q_w: float
    q_x: float
    q_y: float
    q_z: float
    t_x: float
    t_y: float
    t_z: float
    r_err: float
    t_err: float
    inlier_counter: int

    @property
    def as_matrix(self):
        homogeneous = np.zeros([4, 4])
        rot = R.from_quat([self.q_x, self.q_y, self.q_z, self.q_w]).as_matrix()
        homogeneous[0:3, 0:3] = rot
        homogeneous[0, 3] = self.t_x
        homogeneous[1, 3] = self.t_y
        homogeneous[2, 3] = self.t_z
        homogeneous[3, 3] = 1

        return np.linalg.inv(homogeneous).reshape(16, order="F")


def process_testing_data(combined_path: str, downloader: FirebaseDownloader):
    prepare_ace_data(downloader.extracted_data)
    os.chdir(Path(__file__).parent.parent.parent / "third_party/ace")
    extracted_ace_folder = downloader.local_extraction_location / "ace"
    model_name = Path(combined_path).stem.split("training_")[-1]
    model_name = "_".join(model_name.split("_")[2:])

    for (dir, _, _) in os.walk(downloader.root_download_dir):
        dir_path = Path(dir)
        if str(dir_path).endswith(model_name) and dir_path.parts[-1].startswith("training_"):
            model_data_folder = Path(dir) / "ace"
            model_weights_path = model_data_folder / "model.pt"
            break
    else:
        raise NotImplementedError
        # if not model_weights_path.exists():
        #     downloader.download_file(
        #         f"iosLoggerDemo/trainedModels/{model_name}.pt", model_weights_path
        #     )

    ace_test_pose_file = model_data_folder / "poses_ace_.txt"
    run_ace_evaluator(
        extracted_ace_folder, model_weights_path, False, True, extracted_ace_folder
    )
    breakpoint()
    process_localization_phase(combined_path, downloader, ace_test_pose_file)


# test the benchmark here
if __name__ == "__main__":
    if len(sys.argv) == 2:
        tars = sys.argv[1]

    else:
        tars = list_tars()

    for combined_path in tars:
        firebase_tar_queue_path: str = Path(
            combined_path
        ).parent  # ex: iosLoggerDemo/vyjFKi2zgLQDsxI1koAOjD899Ba2
        tar_name: str = Path(combined_path).parts[
            -1
        ]  # ex: 6B62493C-45C8-43F3-A540-41B5216429EC.tar
        print(
            combined_path
        )  # logger will use this to know that new log needs to be uploaded

        print(
            "[INFO]: Running e2e benchmark on tar with path: ",
            firebase_tar_queue_path,
            " and file name: ",
            tar_name,
        )
        downloader: FirebaseDownloader = FirebaseDownloader(
            firebase_tar_queue_path, tar_name
        )

        downloader.extract_ios_logger_tar()
        if Path(combined_path).parts[-1].startswith("training"):
            process_training_data(combined_path, downloader)
        elif Path(combined_path).parts[-1].startswith("testing"):
            process_testing_data(combined_path, downloader)
        else:
            raise RuntimeError(
                'Invalid file name (must have "testing" or "training" in the name).'
            )
