from pathlib import Path
from anchor.backend.data.extracted import Extracted
from anchor.backend.data.firebase import FirebaseDownloader, list_tars
from anchor.backend.data.error_summarizer import ErrorSummarizer
from anchor.third_party.ace.ace_network import Regressor
from torch.utils.mobile_optimizer import optimize_for_mobile, MobileOptimizerType
import shutil
import random
import sys
import os
import torch


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
    ground_truth_location = extracted_data.sensors_extracted[Extracted.get_phase_key(True)]["google_cloud_anchor"]["anchor_host_rotation_matrix"]
    for value in extracted_data.sensors_extracted[Extracted.get_phase_key(False)]["google_cloud_anchor"]:
        error_summarizer.observe_pose(value["anchor_rotation_matrix"], ground_truth_location)
    error_summarizer.print_statistics()

""" 
    Converts the ACE model for mobile usage
"""
def save_model_for_mobile(ace_encoder_pretrained: Path, trained_weights: Path):     
    encoder_state_dict = torch.load(ace_encoder_pretrained, map_location="cpu")
    head_network_dict = torch.load(trained_weights, map_location="cpu")

    device = torch.device("cuda")
    network = Regressor.create_from_split_state_dict(encoder_state_dict, head_network_dict)
    network = network.to(device)
    network.eval()

    scripted_module = torch.jit.script(network)
    # it looks it's not trivial to optimize for mobile gpu right because this issue: https://github.com/pytorch/pytorch/issues/69609
    optimized_model = optimize_for_mobile(scripted_module, backend='CPU')
    optimized_model.save(trained_weights.parent / "mobile.model.pt")
    optimized_model._save_for_lite_interpreter((trained_weights.parent / "mobile.model.ptl").as_posix())
    
"""
Runs the ace evaluator on the trained model. To run paste the following into main:
run_ace_evaluator(extracted_ace_folder, model_output, visualizer_enabled, render_flipped_portrait, render_target_path)
"""
def run_ace_evaluator(extracted_ace_folder, model_output, visualizer_enabled, render_flipped_portrait, render_target_path):
    print("[INFO]: Running ace evaluater on dataset path: ", extracted_ace_folder)
    os.system(f'./test_ace.py {extracted_ace_folder.as_posix()} {model_output.as_posix()} --render_visualization {"True" if visualizer_enabled else "False"}   --render_flipped_portrait {"True" if render_flipped_portrait else "False"} --render_target_path "{render_target_path.as_posix()}"')


# test the benchmark here
if __name__ == '__main__':
    if len(sys.argv) == 2:
        combined_path = sys.argv[1]
    
    else:
        combined_path = list_tars()
        print(combined_path)

    if combined_path != None:
        firebase_path: str = Path(combined_path).parent # ex: iosLoggerDemo/vyjFKi2zgLQDsxI1koAOjD899Ba2
        tar_name: str = Path(combined_path).parts[-1] # ex: 6B62493C-45C8-43F3-A540-41B5216429EC.tar

        print("[INFO]: Running e2e benchmark on tar with path: ", firebase_path, " and file name: ", tar_name)

        downloader = FirebaseDownloader(firebase_path, tar_name)
        downloader.extract_ios_logger_tar()
        prepare_ace_data(downloader.extracted_data)
        if len(sys.argv) != 2:
            downloader.delete_file((Path(firebase_path) / tar_name).as_posix())
            print("deleted tar from firebase")

        print("[INFO]: Summarizing google cloud anchor observations: ")
        calculate_google_cloud_anchor_quality(downloader.extracted_data)

        extracted_ace_folder = downloader.local_extraction_location / "ace"
        model_output = extracted_ace_folder / "model.pt"
        render_target_path = extracted_ace_folder / "debug_visualizer"
        render_target_path.mkdir(parents=True, exist_ok=True)
        pretrained_model = Path(__file__).parent.parent.parent / "third_party" / "ace" / "ace_encoder_pretrained.pt"
        visualizer_enabled = False
        render_flipped_portrait = False 
        training_epochs = 1

        print("[INFO]: Running ace training on dataset path: ", extracted_ace_folder)
        os.chdir("anchor/third_party/ace")
        os.system(f'./train_ace.py {extracted_ace_folder.as_posix()} {model_output.as_posix()} --render_visualization {"True" if visualizer_enabled else "False"} --render_flipped_portrait {"True" if render_flipped_portrait else "False"} --render_target_path "{render_target_path.as_posix()}" --epochs {training_epochs}')

        print("[INFO]: Converting ACE model for mobile use")
        save_model_for_mobile(pretrained_model, model_output)
        
        firebase_upload_dir = "iosLoggerDemo/trainedModels/"
        vid_name = combined_path.rsplit(".", 1)[0]
        vid_name = vid_name.rsplit("/", 1)[1]+".pt"
        firebase_upload_path = Path(firebase_upload_dir) / Path(vid_name)
        print("[INFO]: Saving model to firebase as {}".format(firebase_upload_path))
        downloader.upload_file(firebase_upload_path.as_posix(), pretrained_model)
        
        if visualizer_enabled: 
            os.system(f'/usr/bin/ffmpeg -framerate 30 -pattern_type glob -i "{render_target_path.as_posix()}/**/*.png" -c:v libx264 -pix_fmt yuv420p "{render_target_path.as_posix()}/out.mp4"')
