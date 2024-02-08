from typing import Union
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from pathlib import Path
from anchor.backend.server.loaders import ModelLoader, MultiHeadedModelLoader
from typing import List
import torch

from anchor.backend.data.firebase import FirebaseDownloader

# you can start the server by running:
#   uvicorn anchor.backend.server.localizer:app --reload --host 10.76.135.81 --port 8000
app = FastAPI()

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
    modelName: str
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
        req.arkit_pose,
    )
    return {
        "pose": out_pose.flatten().tolist(),
        "inlier_count": inlier_count,
        "model": model_name,
        "status": "ok",
    }

@app.post("/generate_anchor/")
async def generateAnchor(req: GenerateAnchorReq, background_tasks: BackgroundTasks):
    pass