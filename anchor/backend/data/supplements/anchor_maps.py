from pydantic import BaseModel
from pathlib import Path
import json
from typing import List

DATA_FILE = Path(__file__).parent / "anchor_maps.json"

class SupplementalAnchor(BaseModel):
    supplemental_ca_name: str
    supplemental_ca_transform: List[float]
    supplemental_ca_ace_id: str

class SameSceneAnchors(BaseModel):
    supplemental_cas: List[SupplementalAnchor]

    def get_model_name_scene_name_pairs(self):
        ace_names = [x.supplemental_ca_ace_id for x in self.supplemental_cas]

        pairs = []
        for model_name in ace_names:
            for scene_name in ace_names:
                pairs.append((model_name, scene_name))

        return pairs


def get_anchor_maps_data() -> List[SameSceneAnchors]:
    with open(DATA_FILE, "r") as json_file:
        data = json.load(json_file)

    ca_to_ace_mappings = data["cloudAnchorToACEID"]
    same_scene_anchors = []

    for _, supplemental_ca_data in data["supplementalAnchors"].items():
        if isinstance(supplemental_ca_data, dict):
            if len(supplemental_ca_data.keys()) < 2:
                continue

            supplemental_cas = []

            for (
                supplemental_ca_name,
                supplemental_ca_transform,
            ) in supplemental_ca_data.items():
                supplemental_cas.append(
                    SupplementalAnchor(
                        supplemental_ca_name=supplemental_ca_name,
                        supplemental_ca_transform=supplemental_ca_transform,
                        supplemental_ca_ace_id=ca_to_ace_mappings[supplemental_ca_name],
                    )
                )

            same_scene_anchors.append(SameSceneAnchors(supplemental_cas=supplemental_cas))
        else:
            if len(supplemental_ca_data) < 2:
                continue
            
            supplemental_cas = []

            for ca_data in supplemental_ca_data:
                supplemental_cas.append(SupplementalAnchor(
                    supplemental_ca_name=ca_data["toID"],
                    supplemental_ca_transform=ca_data["relativeTransform"],
                    supplemental_ca_ace_id=ca_to_ace_mappings[ca_data["toID"]]
                ))

            # Can't find the tar files for these, but there's just one instance
            # of a CA having two supplements, so throwing it out for now
            # same_scene_anchors.append(SameSceneAnchors(supplemental_cas=supplemental_cas))

    return same_scene_anchors


if __name__ == "__main__":
    get_anchor_maps_data()
