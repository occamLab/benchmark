from pathlib import Path
from anchor.backend.data.extracted import Extracted
from anchor.backend.data.firebase import FirebaseDownloader
from anchor.backend.data.error_summarizer import ErrorSummarizer
import shutil
import random
import sys
import os


def prepare_ace_data(extracted_data: Extracted):

    map_phase_to_ace_folder = {
        "mapping_phase": "train",
        "localization_phase": "test"
    }

    for phase in extracted_data.sensors_extracted:
        for data in extracted_data.sensors_extracted[phase]["video"]:

            ace_input = extracted_data.extract_root / "ace"
            write_location = ace_input / map_phase_to_ace_folder[phase]
            write_location.mkdir(parents=True, exist_ok=True)

            # copy the image itself
            dest_img_path = write_location / "rgb" / (f'{data["frame_num"]:05}' + ".color.jpg")
            dest_img_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(data["frame_path"], dest_img_path)

            # copy the intrinsics information
            dest_intrinsics_path = write_location / "calibration" / (f'{data["frame_num"]:05}' + ".calibration.txt")
            dest_intrinsics_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_intrinsics_path, "w") as intrinsics_file:
                intrinsics_data = data["intrinsics"]
                intrinsics_file.write(
                    f'{intrinsics_data["fx"]} 0 {intrinsics_data["cx"]}\n' +
                    f'0 {intrinsics_data["fy"]} {intrinsics_data["cy"]}\n' +
                    f'0 0 1\n'
                )

            # copy the pose information
            dest_pose_path = write_location / "poses" / (f'{data["frame_num"]:05}' + ".pose.txt")
            dest_pose_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_pose_path, "w") as pose_file:
                pose_data = data["poses"]["rotation_matrix"]
                pose_file.write(
                    f'{pose_data[0]} {pose_data[4]} {pose_data[8]} {pose_data[12]}\n' +
                    f'{pose_data[1]} {pose_data[5]} {pose_data[9]} {pose_data[13]}\n' +
                    f'{pose_data[2]} {pose_data[6]} {pose_data[10]} {pose_data[14]}\n' +
                    f'{pose_data[3]} {pose_data[7]} {pose_data[11]} {pose_data[15]}'
                )

def calculate_google_cloud_anchor_quality(extracted_data: Extracted):
    error_summarizer = ErrorSummarizer()
    for value in extracted_data[Extracted.get_phase_key(False)]["google_cloud_anchor"]:
        error_summarizer.observe_pose(value["anchor_rotation_matrix"], value["arkit_rotation_matrix"], )


# test the benchmark here
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("[ERROR]: Usage: python -m anchor.backend.data.ace iosLoggerDemo/vyjFKi2zgLQDsxI1koAOjD899Ba2/6B62493C-45C8-43F3-A540-41B5216429EC.tar")

    combined_path = sys.argv[1]
    firebase_path: str = Path(combined_path).parent # ex: iosLoggerDemo/vyjFKi2zgLQDsxI1koAOjD899Ba2
    tar_name: str = Path(combined_path).parts[-1] # ex: 6B62493C-45C8-43F3-A540-41B5216429EC.tar

    print("[INFO]: Running e2e benchmark on tar with path: ", firebase_path, " and file name: ", tar_name)

    downloader = FirebaseDownloader(firebase_path, tar_name)
    downloader.extract_ios_logger_tar()
    prepare_ace_data(downloader.extracted_data)

    print("[INFO]: Summarizing google cloud anchor observations: ")
    calculate_google_cloud_anchor_quality(downloader.extracted_data)

    extracted_ace_folder = downloader.local_extraction_location / "ace"
    model_output = extracted_ace_folder / "model.pt"
    render_target_path = extracted_ace_folder / "debug_visualizer"
    render_target_path.mkdir(parents=True, exist_ok=True)
    visualizer_enabled = True
    render_flipped_portrait = False

    exit(0)
    

    print("[INFO]: Running ace training on dataset path: ", extracted_ace_folder)
    os.chdir("third_party/ace")
    os.system(f'./train_ace.py {extracted_ace_folder.as_posix()} {model_output.as_posix()} --render_visualization {"True" if visualizer_enabled else "False"} --render_flipped_portrait {"True" if render_flipped_portrait else "False"} --render_target_path "{render_target_path.as_posix()}"')
    print("[INFO]: Running ace evaluater on dataset path: ", extracted_ace_folder)
    os.system(f'./test_ace.py --render_visualization {"True" if visualizer_enabled else "False"} {extracted_ace_folder.as_posix()} {model_output.as_posix()} --render_target_path "{render_target_path.as_posix()}"')
    if visualizer_enabled: 
      os.system(f'/usr/bin/ffmpeg -framerate 30 -pattern_type glob -i "{render_target_path.as_posix()}/**/*.png" -c:v libx264 -pix_fmt yuv420p "{render_target_path.as_posix()}/out.mp4"')
