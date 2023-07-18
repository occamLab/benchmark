from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
from anchor.third_party.ace.ace_network import Regressor
from anchor.backend.server.loaders import ModelLoader
import torch

from anchor.backend.data.firebase import FirebaseDownloader


# you can start the server by running: 
#   uvicorn anchor.backend.server.localizer:app --reload --host 10.26.26.130 --port 8000

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

@app.post("/localize/")
def localizeImage(req: LocalizeImageReq):
    model = modelLoader.load_ace_model_if_needed(req.modelName, modelLoader.download_model_if_needed(req.modelName))
    print(model)

    return {"status": "ok"}
