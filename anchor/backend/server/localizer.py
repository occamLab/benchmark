from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
from anchor.third_party.ace.ace_network import Regressor
from anchor.backend.server.loaders import ModelLoader
from typing import List
import torch

from anchor.backend.data.firebase import FirebaseDownloader

# you can start the server by running: 
#   uvicorn anchor.backend.server.localizer:app --reload --host 10.26.26.130 --port 8000
app = FastAPI()
modelLoader = ModelLoader()

@app.get("/")
def read_root():
    return {"Hello": "World"}

class LocalizeImageReq(BaseModel):
    base64Jpg: str
    modelName: str


class LocalizeImageReq(BaseModel):
    base64Jpg: str
    modelName: str
    focal_length: float
    optical_x: float
    optical_y: float
    arkit_pose: List[float]

@app.post("/localize/")
def localizeImage(req: LocalizeImageReq):
    out_pose, inlier_count = modelLoader.localize_image(req.modelName, req.base64Jpg, req.focal_length, req.optical_x, req.optical_y, req.arkit_pose)
    return {
        "pose": out_pose.flatten().tolist(),
        "inlier_count":  inlier_count,
        "status": "ok"
    }
