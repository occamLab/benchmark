
from anchor.third_party.ace.ace_network import Regressor
from anchor.backend.data.firebase import FirebaseDownloader
import dsacstar
import torchvision.transforms.functional as TF
from torchvision import transforms
from torch.cuda.amp import autocast
from pathlib import Path
from io import BytesIO
from PIL import Image
import torch, tempfile, base64


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
    
    """
        Runs localization against the input image given a specified model
    """
    def localize_image(self, model_name: str, base64Jpg: str):
        train_resolution = 480
        model = self.load_ace_model_if_needed(model_name, self.download_model_if_needed(model_name))

        img_bytes: bytes = base64.b64decode(base64Jpg) 
        img_file: BytesIO = BytesIO(img_bytes)
        pil_img: Image = Image.open(img_file)   

        image_transform = transforms.Compose([
                transforms.Resize(train_resolution),
                transforms.Grayscale(),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.4],  # statistics calculated over 7scenes training set, should generalize fairly well
                    std=[0.25]
                ),
        ])
        tensor_image = image_transform(pil_img)
        tensor_image = tensor_image.unsqueeze(0) # this fills the batch_size as 1 by adding a new dimension
        
        device = torch.device("cuda")
        tensor_image = tensor_image.to(device, non_blocking=True)

        with autocast(enabled=True):
            scene_coordinates = model(tensor_image).float().cpu()
        
        # Allocate output variable.
        out_pose = torch.zeros((4, 4))

        inlier_count = dsacstar.forward_rgb(
            scene_coordinates,
            out_pose,
            64, # ransack hypothesis
            10, # inlier threshold
            10, # focal length
            10, # ox
            10, # oy
            100, # inlier alpha
            100, # max pixel error
            model.OUTPUT_SUBSAMPLE,
        )

        print(inlier_count)
     

        # torch.Size([1, 1, 480, 640])
        
        #print(model)
