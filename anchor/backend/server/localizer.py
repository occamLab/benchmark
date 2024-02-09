from typing import Union
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from pathlib import Path
from anchor.third_party.ace.ace_network import Regressor
from anchor.backend.data.firebase import FirebaseDownloader
from anchor.backend.server.loaders import ModelLoader
from anchor.backend.data.ace import process_training_data
import numpy as np
from anchor.backend.server.loaders import ModelLoader, MultiHeadedModelLoader
from typing import List
from time import perf_counter

from anchor.backend.data.firebase import FirebaseDownloader

# you can start the server by running:
#   uvicorn anchor.backend.server.localizer:app --reload --host 10.76.135.81 --port 8000
app = FastAPI()
downloader = FirebaseDownloader("none", "none")

MULTI_HEADED_LOCALIZATION = True

if MULTI_HEADED_LOCALIZATION:
    modelLoader = MultiHeadedModelLoader()
else:
    modelLoader = ModelLoader()


@app.get("/")
def read_root():
    return {"Hello": "World"}


class LocalizeImageReq(BaseModel):
    base64Jpg: str
    modelName: List[str]
    focal_length: float
    optical_x: float
    optical_y: float
    arkit_pose: List[float]


class GenerateAnchorReq(BaseModel):
    videoFilePath: str
    modelName: str


@app.post("/localize/")
def localizeImage(req: LocalizeImageReq):
    out_pose, inlier_count, model_name = modelLoader.localize_image(
        req.modelName,
        req.base64Jpg,
        req.focal_length,
        req.optical_x,
        req.optical_y,
    )
    print(
        f"Model {''.join(model_name.split('_')[-3:])} returned pose with {inlier_count} inliers."
        f"Position: [{np.array(out_pose[0,3]):.3f}, {np.array(out_pose[1,3]):.3f},"
        f" {np.array(out_pose[2,3]):.3f}]"
    )
    return {
        "pose": out_pose.flatten().tolist(),
        "inlier_count": inlier_count,
        "model": model_name,
        "status": "ok",
    }


class CreateAnchorReq(BaseModel):
    tar_path: str
    anchor_name: str


FIREBASE_UPLOAD_TIMEOUT_S = 5


def create_anchor(data=CreateAnchorReq):
    firebase_tar_queue_path: str = Path(data.tar_path).parent
    tar_name: str = Path(data.tar_path).parts[-1]
    tar_specific_downloader = FirebaseDownloader(firebase_tar_queue_path, tar_name)
    downloader.extract_ios_logger_tar()
    process_training_data(
        data.tar_path,
        tar_specific_downloader,
        run_tests=False,
        output_model_name=data.anchor_name,
    )
    pass


@app.post("/create_anchor/")
async def receive_anchor_req(req: CreateAnchorReq, background_tasks: BackgroundTasks):
    fb_path = req.tar_path

    time_start = perf_counter()

    while (perf_counter() - time_start) < FIREBASE_UPLOAD_TIMEOUT_S:
        if downloader.check_file_exists(fb_path):
            background_tasks.add_task(create_anchor, req)
            return {"status": "200"}
    return {"status": "404"}
