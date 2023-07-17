from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel


# you can start the server by running: 
#   uvicorn anchor.backend.server.localizer:app --reload --host 10.26.26.130 --port 8000

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

class LocalizeImageReq(BaseModel):
    base64Jpg: str
    modelName: str

@app.post("/localize/")
def localizeImage(req: LocalizeImageReq):
    return {"status": "ok"}
