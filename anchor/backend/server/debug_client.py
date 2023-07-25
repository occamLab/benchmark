from pathlib import Path
import numpy as np
import requests, base64, os, shutil, tempfile
from anchor.backend.data.firebase import FirebaseDownloader
from anchor.backend.data.ace import run_ace_evaluator

"""
    We are trying to debug why the inlier counts seem very low/wrong when sending images to the server
    from the app. This script pretends to be a app and can send an image to the server in a reproducable manner
    for testing/debug purposes.

    Returns:  pose: np.matrix, inlier_counts: int
"""

def send_localization_request(model_name: str, base64_image: str, focal_length: float, optical_x: float, optical_y: float): 
    server_url = "http://10.26.26.130:8000/localize"
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    request_body = {
        "base64Jpg": base64_image,
        "modelName": model_name,
        "focal_length": focal_length,
        "optical_x": optical_x,
        "optical_y": optical_y
    }
    response = requests.post(server_url, json=request_body, headers=headers)
    response_body = response.json()

    pose = np.array(response_body["pose"]).reshape(4,4)
    inlier_counts = response_body["inlier_count"]

    return pose, inlier_counts

"""
    Intrinsics data should be in the same format as fed into https://github.com/nianticlabs/ace/blob/main/test_ace.py
"""
def send_localization_from_path(model_name: str, image_path: Path, intrinsics_path: Path):
    image_b64: str = base64.b64encode(image_path.read_bytes()).decode()
    intrinsics = np.loadtxt(intrinsics_path)
    return send_localization_request(model_name, image_b64, intrinsics[0,0], intrinsics[0,2], intrinsics[1,2])


"""
    Provide a partially complete ace dataset for https://github.com/nianticlabs/ace/blob/main/test_ace.py 
    with folders for rgb and calibration

    Writes out the poses folder by relocing from server 
"""
def write_localization_from_dataset(model_name: str, partial_ace_data_set: Path):
    images = list(map(lambda x: partial_ace_data_set / "rgb" / x, sorted(os.listdir(partial_ace_data_set / "rgb"))))
    intrinsics =  list(map(lambda x: partial_ace_data_set / "calibration" / x, sorted(os.listdir(partial_ace_data_set / "calibration"))))
    assert len(images) == len(intrinsics)

    for idx, _ in enumerate(images):
        pose, inlier_counts = send_localization_from_path(model_name, Path(images[idx]), Path(intrinsics[idx]))
        item_prefix = Path(images[idx])
        sequence_number = os.path.splitext(item_prefix.stem)[0]

        shutil.rmtree(partial_ace_data_set / "poses", ignore_errors=True)
        shutil.rmtree(partial_ace_data_set / "inlier_count", ignore_errors=True)
        (partial_ace_data_set / "poses").mkdir(parents=True, exist_ok=True)
        (partial_ace_data_set / "inlier_count").mkdir(parents=True, exist_ok=True)
        np.savetxt((partial_ace_data_set / "poses" / f'{sequence_number}.pose.txt').as_posix(), pose, fmt='%f')
        with open((partial_ace_data_set / "inlier_count" / f"{sequence_number}.inliers.txt"), "w") as file:
            file.write(str(inlier_counts))

"""
    Runs dataset localization through the server and then compares it to test_ace.py reference implementation 
    from https://github.com/nianticlabs/ace/blob/main/test_ace.py

    Provide a partially complete ace dataset for https://github.com/nianticlabs/ace/blob/main/test_ace.py 
    with folders for rgb and calibration

"""
def test_dataset_e2e(model_name: str, partial_ace_data_set: Path): 
    write_localization_from_dataset(model_name, partial_ace_data_set / "test")

    ace_folder_path: Path = Path(__file__).parent.parent.parent / "third_party" / "ace"
    print(ace_folder_path)
    os.chdir(ace_folder_path)
    
    with tempfile.NamedTemporaryFile() as tmp:
        firebase_downloader = FirebaseDownloader("", "")
        firebase_downloader.download_file((Path("iosLoggerDemo") / "trainedModels" / model_name).as_posix(), tmp.name)
        run_ace_evaluator(partial_ace_data_set, Path(tmp.name), False, False, Path("/dev/null"))

test_dataset_e2e("Library_circle.pt", Path("/tmp/repro/batch1"))