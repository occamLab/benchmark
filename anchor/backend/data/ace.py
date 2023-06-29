from anchor.backend.data.extracted import Extracted
from anchor.backend.data.firebase import FirebaseDownloader
import shutil
import random


def prepare_ace_data(extracted_data: Extracted):
    # percentage of mapping data to use for training compared to test of model
    training_to_test_split = 0.800
    ace_input = extracted_data.extract_root / "ace"

    for data in extracted_data.sensors_extracted["mapping_phase"]["video"]:
        # randomly split between training and test
        if random.random() < training_to_test_split:
            write_location = ace_input / "train"
        else:
            write_location = ace_input / "test"

        write_location.mkdir(parents=True, exist_ok=True)

        # copy the image itself
        dest_img_path = write_location / "rgb" / (str(data["frame_num"]) + ".color.jpg")
        dest_img_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(data["frame_path"], dest_img_path)

        # copy the intrinsics information
        dest_intrinsics_path = write_location / "calibration" / (str(data["frame_num"]) + ".calibration.txt")
        dest_intrinsics_path.parent.mkdir(parents=True, exist_ok=True)

        with open(dest_intrinsics_path, "w") as intrinsics_file:
            intrinsics_data = data["intrinsics"]
            intrinsics_file.write(
                f'{intrinsics_data["fx"]} 0 {intrinsics_data["cx"]}\n' +
                f'0 {intrinsics_data["fy"]} {intrinsics_data["cy"]}\n' +
                f'0 0 1\n'
            )

        # copy the pose information
        dest_pose_path = write_location / "poses" / (str(data["frame_num"]) + ".pose.txt")
        dest_pose_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_pose_path, "w") as pose_file:
            pose_data = data["poses"]["rotation_matrix_with_translation"]
            print(pose_data)
            pose_file.write(
                f'{pose_data[0]} {pose_data[1]} {pose_data[2]} {pose_data[3]}\n' +
                f'{pose_data[4]} {pose_data[5]} {pose_data[6]} {pose_data[7]}\n' +
                f'{pose_data[8]} {pose_data[9]} {pose_data[10]} {pose_data[11]}\n' +
                f'{pose_data[12]} {pose_data[13]} {pose_data[14]} {pose_data[15]}'
            )

    # todo process localization frames and adjust based on global localization with april tags


# test the extractor here
if __name__ == '__main__':
    downloader = FirebaseDownloader("iosLoggerDemo/Ljur5BYFXdhsGnAlEsmjqyNG5fJ2",
                                    "2E49C166-E68C-47F2-A61B-17361AF5363C.tar")
    downloader.extract_ios_logger_tar()
    prepare_ace_data(downloader.extracted_data)
