
from anchor.third_party.ace.ace_network import Regressor
from anchor.backend.data.firebase import FirebaseDownloader
from pathlib import Path
import torch, tempfile


class ModelLoader: 
    def __init__(self) -> None:
        self.loaded_model_cache = {}
        self.downloaded_model_cache = {}

        self.downloader = FirebaseDownloader("none", "none")


    """
        Loads the scene-specific head and pretrained ACE model if it is not already loaded
    """
    def load_ace_model_if_needed(self, model_name: str, scene_specific_path: str):
        if(model_name not in self.loaded_model_cache.keys()):
            pretrained_path: Path = Path(__file__).parent.parent.parent / "third_party" / "ace" / "ace_encoder_pretrained.pt"
            encoder_state_dict = torch.load(pretrained_path, map_location="cpu")
            head_state_dict = torch.load(scene_specific_path, map_location="cpu")
            network = Regressor.create_from_split_state_dict(encoder_state_dict, head_state_dict)

            device = torch.device("cuda")
            network = network.to(device)
            network.eval()

            self.loaded_model_cache[model_name] = network

        return self.loaded_model_cache[model_name]

    """
        Downloads the scence-specific weights if they are not already downloaded
    """
    def download_model_if_needed(self, model_name: str): 
        if(model_name not in self.downloaded_model_cache.keys()):
            tmpFile: str = tempfile.NamedTemporaryFile().name
            self.downloader.download_file((Path("iosLoggerDemo") / "trainedModels" / model_name).as_posix(), tmpFile)
            self.downloaded_model_cache[model_name] = tmpFile
        return self.downloaded_model_cache[model_name]