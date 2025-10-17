from pydantic import BaseModel
from typing import List, Dict
from pathlib import Path
import os
import numpy as np

CAB_BASE_DIR = Path(__file__).parent.parent / ".cache/firebase_data/CAB/sessions/query_phone"
CAB_SUBSESSION_LIST_FP = CAB_BASE_DIR / "proc/subsessions.txt"

class SameSceneAnchors(BaseModel):
    original_ca_name: str
    original_ace_id: str
    supplemental_ca_name: str
    supplemental_ace_id: str
    relative_transform: List[float]

    def get_model_name_scene_name_pairs(self):
        return [
            (self.original_ace_id, self.original_ace_id),
            (self.supplemental_ace_id, self.original_ace_id),
        ]

def get_anchor_maps_data() -> List[SameSceneAnchors]:
    with open(CAB_SUBSESSION_LIST_FP, "r") as txtfile:
        subsessions = txtfile.readlines()

    subsession_and_num_frames = []
    for subsession in subsessions:
        subsession_and_num_frames.append((subsession.strip(), len(os.listdir(CAB_BASE_DIR / f"raw_data/{subsession.strip()}/images"))))
    subsession_and_num_frames.sort(key=lambda x: -x[1])
    subsession_and_num_frames = [x for x in subsession_and_num_frames if x[1] >= 200]

    same_scene_anchors = []
    for i in range(len(subsession_and_num_frames)):
        for j in range(i + 1, len(subsession_and_num_frames)):
            if i != j:
                same_scene_anchors.append(SameSceneAnchors(
                    original_ca_name="",
                    original_ace_id=subsession_and_num_frames[i][0],
                    supplemental_ca_name="",
                    supplemental_ace_id=subsession_and_num_frames[j][0],
                    relative_transform=[0] * 16
                ))
    breakpoint()
    return same_scene_anchors