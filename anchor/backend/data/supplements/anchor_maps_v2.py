from pydantic import BaseModel
from typing import List, Dict
from pathlib import Path
import json
import numpy as np

data_path = Path(__file__).parent / "anchor_maps-6.json"
# old_data_path = Path(__file__).parent / "anchor_maps-4.json"


class RawSupplementalAnchorEntry(BaseModel):
    originalCAName: str
    aceAnchorID: str
    supplementalAnchors: Dict[str, List[float]]
    supplementalAnchorsAnchorPose: Dict[str, List[float]]
    supplementalAnchorsSupplementalAnchorPose: Dict[str, List[float]]


class ProcessedSupplementalAnchorDatum(BaseModel):
    ca_name: str
    supplementalAnchors: List[float]
    supplementalAnchorsAnchorPose: List[float]
    supplementalAnchorsSupplementalAnchorPose: List[float]
    aceAnchorID: str

    @property
    def sa_homog(self) -> np.ndarray:
        return np.reshape(self.supplementalAnchors, [4, 4], order="F")

    @property
    def saap_homog(self) -> np.ndarray:
        return np.reshape(self.supplementalAnchorsAnchorPose, [4, 4], order="F")

    @property
    def sasap_homog(self) -> np.ndarray:
        return np.reshape(
            self.supplementalAnchorsSupplementalAnchorPose, [4, 4], order="F"
        )


class ProcessedSupplementalAnchors(BaseModel):
    originalCAName: str
    aceAnchorID: str
    supplemental_anchors: List[ProcessedSupplementalAnchorDatum]


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


def get_supplemental_anchors() -> List[ProcessedSupplementalAnchors]:
    with open(data_path, "r") as jsonfile:
        raw_data = json.load(jsonfile)

    # with open(old_data_path, "r") as jsonfile:
    #     old_data = json.load(jsonfile)

    rawSupplementalAnchorData = raw_data["supplementalAnchors"]
    cloudAnchorToACEID = raw_data["cloudAnchorToACEID"]

    raw_anchors = [
        RawSupplementalAnchorEntry(originalCAName=originalCAName, **entries)
        for originalCAName, entries in rawSupplementalAnchorData.items()
    ]

    processed_anchors = []
    for anchor in raw_anchors:
        if not anchor.aceAnchorID:
            continue

        supplemental_anchors = []
        for supplemental_ca_name in anchor.supplementalAnchors:
            # if supplemental_ca_name in old_data["cloudAnchorToACEID"]:
            #     continue
            supplementalAnchors = anchor.supplementalAnchors[supplemental_ca_name]
            supplementalAnchorsAnchorPose = anchor.supplementalAnchorsAnchorPose[
                supplemental_ca_name
            ]
            supplementalAnchorsSupplementalAnchorPose = (
                anchor.supplementalAnchorsSupplementalAnchorPose[supplemental_ca_name]
            )
            aceAnchorID = cloudAnchorToACEID[supplemental_ca_name]
            supplemental_anchors.append(
                ProcessedSupplementalAnchorDatum(
                    ca_name=supplemental_ca_name,
                    supplementalAnchors=supplementalAnchors,
                    supplementalAnchorsAnchorPose=supplementalAnchorsAnchorPose,
                    supplementalAnchorsSupplementalAnchorPose=supplementalAnchorsSupplementalAnchorPose,
                    aceAnchorID=aceAnchorID,
                )
            )
        processed_anchors.append(
            ProcessedSupplementalAnchors(
                originalCAName=anchor.originalCAName,
                aceAnchorID=anchor.aceAnchorID,
                supplemental_anchors=supplemental_anchors,
            )
        )

    return processed_anchors


def get_anchor_maps_data() -> List[SameSceneAnchors]:
    processed_anchors = get_supplemental_anchors()

    same_scene_anchors = []
    for anchor in processed_anchors:
        for supplement in anchor.supplemental_anchors:
            same_scene_anchors.append(
                SameSceneAnchors(
                    original_ca_name=anchor.originalCAName,
                    original_ace_id=anchor.aceAnchorID,
                    supplemental_ca_name=supplement.ca_name,
                    supplemental_ace_id=supplement.aceAnchorID,
                    relative_transform=[0] * 16,  # TODO
                )
            )

    return same_scene_anchors


if __name__ == "__main__":
    get_anchor_maps_data()


"""
6b1907504864f51f50832eb1855dddce
2ffb8a13d22332c62fb478a17f792d1e
5b4d0f7552c695c29c543749b24fbe29

4bf0a0f87ae1a73335d8138516a66b8f
d775c4d1ee17003b824085fa328cb120

3630d75f37afeba275d7abe4c266cfcd
c9ae6d57c5a39268b5ebf459765f7193
"""