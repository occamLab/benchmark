from pathlib import Path
import numpy as np
import requests, base64

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


pose, inlier_counts = send_localization_from_path("Library_circle.pt", Path("/tmp/repro/batch1/test/rgb/0001.color.jpg"), Path("/tmp/repro/batch1/test/calibration/0001.calibration.txt"))
print("inliers: ", inlier_counts)
