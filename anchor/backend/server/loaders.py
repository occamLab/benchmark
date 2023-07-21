
from anchor.third_party.ace.ace_network import Regressor
from anchor.backend.data.firebase import FirebaseDownloader
from anchor.backend.server.logs import nostdout, nostderr
from torchvision import transforms
from torch.cuda.amp import autocast
from pathlib import Path
from io import BytesIO
from PIL import Image
from skimage import io
import torchvision.transforms.functional as TF
import torch, tempfile, base64, dsacstar, time, numpy as np


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

        return: 
            pose: 4x4 tensor, inlier_count: int
            usually if inlier_count is below 100-200, this means that localization has failed

    """
    def localize_image(self, model_name: str, base64Jpg: str, focal_length: float, optical_x: float, optical_y: float):
        with torch.no_grad():
            model = self.load_ace_model_if_needed(model_name, self.download_model_if_needed(model_name))

            img_bytes: bytes = base64.b64decode(base64Jpg) 
            train_resolution: int = 480

            pil_image: Image
            scale_factor: int
            
            with tempfile.NamedTemporaryFile() as tmp:
                tmp.write(img_bytes)
                sk_image = io.imread(tmp.name)
                scale_factor = train_resolution / sk_image.shape[0]
                pil_image = TF.to_pil_image(sk_image)
                pil_image = TF.resize(pil_image, train_resolution)

            image_transform = transforms.Compose([
                    transforms.Grayscale(),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        mean=[0.4],  # statistics calculated over 7scenes training set, should generalize fairly well
                        std=[0.25]
                    ),
            ])
            tensor_image = image_transform(pil_image)
            tensor_image = tensor_image.half()
            tensor_image = tensor_image.unsqueeze(0) # this fills the batch_size as 1 by adding a new dimension
            
            device = torch.device("cuda")
            tensor_image = tensor_image.to(device, non_blocking=True)

            with autocast(enabled=True):
                scene_coordinates = model(tensor_image).float().cpu()
            
            # Allocate output variable.
            out_pose = torch.zeros((4, 4))
            print(scene_coordinates.size())
            with nostdout():
                inlier_count: int = dsacstar.forward_rgb(
                    scene_coordinates,
                    out_pose,
                    64, # ransack hypothesis
                    10, # inlier threshold
                    focal_length * scale_factor, # focal length
                    optical_x * scale_factor, # ox
                    optical_y * scale_factor, # oy
                    100, # inlier alpha
                    100, # max pixel error
                    model.OUTPUT_SUBSAMPLE,
                )

            # save debug information
            
            timestamp = "0001" #int(time.time())
            save_path: Path = Path("/tmp") / "repro" / "batch1" / "test"
            pose_path = save_path / "poses"
            image_path = save_path / "rgb"
            calibration_path = save_path / "calibration"
            inlier_count_path = save_path / "inlier_count"
            pose_path.mkdir(parents=True, exist_ok=True)
            image_path.mkdir(parents=True, exist_ok=True)
            calibration_path.mkdir(parents=True, exist_ok=True)
            inlier_count_path.mkdir(parents=True, exist_ok=True)

            if(inlier_count > 400):
                with open((pose_path / (str(timestamp) + ".pose.txt")).as_posix(), 'w') as file:
                    np.savetxt(file, out_pose.numpy(), fmt='%f')
                with open((calibration_path / (str(timestamp) + ".calibration.txt")).as_posix(), "w") as file:
                    intrinsics = np.eye(3, 3)
                    intrinsics[0,0] = focal_length
                    intrinsics[1,1] = focal_length
                    intrinsics[0,2] = optical_x
                    intrinsics[1,2] = optical_y
                    np.savetxt(file, intrinsics, fmt='%f')
                with open((image_path / (str(timestamp) + ".color.jpg")).as_posix(), "wb") as file:
                    file.write(img_bytes)
                with open((inlier_count_path / (str(timestamp) + ".count.txt")).as_posix(), "w") as file:
                    file.write(f'inliers: {inlier_count}, focal: {focal_length * scale_factor}, ox: {optical_x * scale_factor}, oy: {optical_y * scale_factor}\n')
                
            
            print(inlier_count)
            return out_pose, inlier_count