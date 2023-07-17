from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
import tempfile

from anchor.backend.data.firebase import FirebaseDownloader


# you can start the server by running: 
#   uvicorn anchor.backend.server.localizer:app --reload --host 10.26.26.130 --port 8000


app = FastAPI()
downloader = FirebaseDownloader("none", "none")
models = {}

@app.get("/")
def read_root():
    return {"Hello": "World"}

class LocalizeImageReq(BaseModel):
    base64Jpg: str
    modelName: str

@app.post("/localize/")
def localizeImage(req: LocalizeImageReq):
    if(req.modelName in models.keys()): 
        print("[INFO]: Model already loaded, running inference")
    else: 
        tmpFile = tempfile.NamedTemporaryFile().name
        downloader.download_file((Path("iosLoggerDemo") / "trainedModels" / req.modelName).as_posix(), tmpFile)
        print(f"[INFO]: Downloaded model {req.modelName}")
        
    

    return {"status": "ok"}
