# downloads all the cab files (with depth data) from the ethz remote server


import os
import requests
from tqdm import tqdm
import zipfile
from typing import List
from pydantic import BaseModel
from pathlib import Path
import json

BASE_CAB_REMOTE_URL = "https://cvg-data.inf.ethz.ch/lamar/raw/CAB/"


def download_file(remote_url: str, dest_fp: str):
    os.makedirs(os.path.dirname(dest_fp), exist_ok=True)

    # Skip if file already exists and is non-empty
    if os.path.exists(dest_fp) and os.path.getsize(dest_fp) > 0:
        print(f"✅ {dest_fp} already exists, skipping download.")
        return

    print(f"⬇️  Downloading {remote_url} to {dest_fp}...")
    with requests.get(remote_url, stream=True) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        with open(dest_fp, "wb") as f, tqdm(
            total=total, unit="B", unit_scale=True, desc=os.path.basename(dest_fp)
        ) as bar:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    bar.update(len(chunk))

    print(f"✅ Downloaded {dest_fp}")


def download_zip(remote_url: str, local_zip_fp: str, dest_folder, extract: bool = False):
    download_file(remote_url, local_zip_fp)

    # Optionally extract
    if extract:
        print(f"📦 Extracting to {dest_folder}...")
        with zipfile.ZipFile(local_zip_fp, "r") as zip_ref:
            zip_ref.extractall(dest_folder)
        print(f"✅ Extracted to {dest_folder}")


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
    "https://cvg-data.inf.ethz.ch/lamar/raw/CAB/metadata_phone.json"
    phone_metadata_remote_url = BASE_CAB_REMOTE_URL + "metadata_phone.json"
    phone_metadata_local_fp = (
        Path(__file__).parent.parent
        / ".cache/firebase_data/CAB_remote/metadata_phone.json"
    )
    download_file(phone_metadata_remote_url, phone_metadata_local_fp)

    with open(phone_metadata_local_fp, "r") as jsonfile:
        metadata = json.load(jsonfile)

    sessions_with_depth = [
        session_name
        for session_name, session_metadata in metadata.items()
        if session_metadata.get("has_depth", False)
    ]
    sessions_with_depth.sort(
        key=lambda x: metadata[x]["duration_seconds"],
        # reverse=True,
    )

    same_scene_anchors = []
    for i in range(len(sessions_with_depth)):
        for j in range(i+1, len(sessions_with_depth)):
            same_scene_anchors.append(
                SameSceneAnchors(
                    original_ca_name="",
                    original_ace_id=BASE_CAB_REMOTE_URL + "sessions/" + sessions_with_depth[i],
                    supplemental_ca_name="",
                    supplemental_ace_id=BASE_CAB_REMOTE_URL + "sessions/" + sessions_with_depth[j],
                    relative_transform=[0] * 16,
                )
            )

    return same_scene_anchors


if __name__ == "__main__":
    get_anchor_maps_data()
