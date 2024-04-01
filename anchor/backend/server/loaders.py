from anchor.third_party.ace.ace_network import Regressor, Encoder, Head
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
from typing import List, Dict
import re

TMP_FILE = tempfile.NamedTemporaryFile()
    

class ModelLoader:
    def __init__(self) -> None:
        self.loaded_model_cache = {}
        self.downloaded_model_cache = {}

        self.downloader = FirebaseDownloader("none", "none")

    """
        Loads the scene-specific head and pretrained ACE model if it is not already loaded
    """

    def load_ace_model_if_needed(
        self,
        model_name: str,
        scene_specific_path: str = "/home/powerhorse/Desktop/daniel_tmp/benchmark/anchor/backend/data/.cache/models/ua-f20318dcd0459d2f418b3fd4519bb8ab_ayush_nov28_1.pt",
    ):
        if model_name not in self.loaded_model_cache.keys():
            pretrained_path: Path = (
                Path(__file__).parent.parent.parent
                / "third_party"
                / "ace"
                / "ace_encoder_pretrained.pt"
            )
            encoder_state_dict = torch.load(pretrained_path, map_location="cpu")
            head_state_dict = torch.load(scene_specific_path, map_location="cpu")
            network = Regressor.create_from_split_state_dict(
                encoder_state_dict, head_state_dict
            )

            device = torch.device("cuda")
            network = network.to(device)
            network.eval()

            test = Encoder()
            test.load_state_dict(encoder_state_dict)
            self.test = test.to(device)
            self.test.eval()

            self.loaded_model_cache[model_name] = network

        return self.loaded_model_cache[model_name]

    """
        Downloads the scence-specific weights if they are not already downloaded
    """

    def download_model_if_needed(self, model_name: str):
        if model_name not in self.downloaded_model_cache.keys():
            tmpFile: str = tempfile.NamedTemporaryFile().name
            self.downloader.download_file(
                (Path("iosLoggerDemo") / "trainedModels" / model_name).as_posix(),
                tmpFile,
            )
            self.downloaded_model_cache[model_name] = tmpFile
        return self.downloaded_model_cache[model_name]

    """
        Runs localization against the input image given a specified model

        return: 
            pose: 4x4 tensor, inlier_count: int
            usually if inlier_count is below 100-200, this means that localization has failed

    """

    def localize_image(
        self,
        model_name: str,
        base64Jpg: str,
        focal_length: float,
        optical_x: float,
        optical_y: float,
        arkit_pose: List[float],
    ):
        with torch.no_grad():
            model = self.load_ace_model_if_needed(
                model_name,
                # self.download_model_if_needed(model_name),
            )

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
            tmp.close()

            image_transform = transforms.Compose(
                [
                    transforms.Grayscale(),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        mean=[
                            0.4
                        ],  # statistics calculated over 7scenes training set, should generalize fairly well
                        std=[0.25],
                    ),
                ]
            )
            tensor_image = image_transform(pil_image)
            tensor_image = tensor_image.half()
            tensor_image = tensor_image.unsqueeze(
                0
            )  # this fills the batch_size as 1 by adding a new dimension

            device = torch.device("cuda")
            tensor_image = tensor_image.to(device, non_blocking=True)

            with autocast(enabled=True):
                scene_coordinates = model(tensor_image).float().cpu()
                t = self.test(tensor_image).float().cpu()
            # Allocate output variable.
            out_pose = torch.zeros((4, 4))
            with nostdout():
                inlier_count: int = dsacstar.forward_rgb(
                    scene_coordinates,
                    out_pose,
                    64,  # ransack hypothesis
                    10,  # inlier threshold
                    focal_length * scale_factor,  # focal length
                    optical_x * scale_factor,  # ox
                    optical_y * scale_factor,  # oy
                    100,  # inlier alpha
                    100,  # max pixel error
                    model.OUTPUT_SUBSAMPLE,
                )

            # # save debug poses for visualization
            # if inlier_count > 600:
            #     timestamp = time.time()
            #     np.savetxt(
            #         f"/tmp/repro/{timestamp}.pose-anchor.txt",
            #         out_pose.numpy(),
            #         fmt="%f",
            #     )
            #     np.savetxt(
            #         f"/tmp/repro/{timestamp}.pose-arkit.txt",
            #         np.reshape(arkit_pose, (4, 4)).transpose(),
            #         fmt="%f",
            #     )
            return out_pose, inlier_count


class MultiHeadedModelLoader:
    def __init__(self) -> None:
        self.encoder: Encoder = None
        self.model_head_cache: Dict[str, Head] = {}
        self.model_cache_dir = Path(__file__).parent.parent / "data/.cache/models"

        self.downloader = FirebaseDownloader("none", "none")
        self.encoder_weights_path = (
            Path(__file__).parent.parent.parent
            / "third_party/ace/ace_encoder_pretrained.pt"
        )
        self.device = torch.device("cuda")

    def load_ace_models_if_needed(self, model_names: List[str]):
        if not self.encoder:
            encoder_state_dict = torch.load(
                self.encoder_weights_path, map_location="cpu"
            )
            encoder = Encoder()
            encoder.load_state_dict(encoder_state_dict)
            self.encoder = encoder.to(self.device)
            self.encoder.eval()

        for model_name in model_names:
            if model_name not in self.model_head_cache:
                if not (target_loc := self.model_cache_dir / model_name).exists():
                    self.downloader.download_file(
                        remote_location=f"iosLoggerDemo/trainedModels/{model_name}.pt",
                        local_location=target_loc,
                    )

                head_state_dict = torch.load(target_loc, map_location="cpu")
                mean = torch.zeros((3,))
                pattern = re.compile(r"res_blocks\.\d+\.0\.weight$")
                num_head_blocks = sum(
                    1 for k in head_state_dict.keys() if pattern.match(k)
                )
                use_homogeneous = head_state_dict["fc3.weight"].shape[0] == 4
                model = Head(mean, num_head_blocks, use_homogeneous)
                model.load_state_dict(head_state_dict)
                self.model_head_cache[model_name] = model.to(self.device)
                self.model_head_cache[model_name].eval()

    def localize_image(
        self,
        model_names: List[str],
        base64Jpg: str,
        focal_length: float,
        optical_x: float,
        optical_y: float,
    ):
        if not isinstance(model_names, List):
            model_names = [model_names]
        model_names = [
            m.split("training_")[-1].split("test_")[-1].split(".tar")[0]
            for m in model_names
        ]
        with torch.no_grad():
            self.load_ace_models_if_needed(model_names)

            img_bytes: bytes = base64.b64decode(base64Jpg)
            train_resolution: int = 480

            pil_image: Image
            scale_factor: int

            TMP_FILE.write(img_bytes)
            sk_image = io.imread(TMP_FILE.name)
            scale_factor = train_resolution / sk_image.shape[0]
            pil_image = TF.to_pil_image(sk_image)
            pil_image = TF.resize(pil_image, train_resolution)

            image_transform = transforms.Compose(
                [
                    transforms.Grayscale(),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        mean=[
                            0.4
                        ],  # statistics calculated over 7scenes training set, should generalize fairly well
                        std=[0.25],
                    ),
                ]
            )
            tensor_image = image_transform(pil_image)
            tensor_image = tensor_image.half()
            tensor_image = tensor_image.unsqueeze(
                0
            )  # this fills the batch_size as 1 by adding a new dimension

            device = torch.device("cuda")
            tensor_image = tensor_image.to(device, non_blocking=True)

            with autocast(enabled=True):
                features = self.encoder(tensor_image)

            max_inlier_count = 0
            best_pose = torch.zeros((4, 4))
            best_model = ""

            for model_name in model_names:
                model = self.model_head_cache[model_name]
                with autocast(enabled=True):
                    scene_coordinates = model(features).float().cpu()

                # Allocate output variable.
                out_pose = torch.zeros((4, 4))
                inlier_map = torch.zeros(scene_coordinates.size()[2:])

                inlier_count: int = dsacstar.forward_rgb(
                    scene_coordinates,
                    out_pose,
                    64,  # ransack hypothesis
                    10,  # inlier threshold
                    focal_length * scale_factor,  # focal length
                    optical_x * scale_factor,  # ox
                    optical_y * scale_factor,  # oy
                    100,  # inlier alpha
                    100,  # max pixel error
                    8,  # OUTPUT_SUBSAMPLE copied from Regressor Class in ace_network.py
                    inlier_map,
                )
                if inlier_count > max_inlier_count:
                    max_inlier_count = inlier_count
                    best_pose = out_pose
                    best_model = model_name

            # # save debug poses for visualization
            # if inlier_count > 600:
            #     timestamp = time.time()
            #     np.savetxt(
            #         f"/tmp/repro/{timestamp}.pose-anchor.txt",
            #         out_pose.numpy(),
            #         fmt="%f",
            #     )
            #     np.savetxt(
            #         f"/tmp/repro/{timestamp}.pose-arkit.txt",
            #         np.reshape(arkit_pose, (4, 4)).transpose(),
            #         fmt="%f",
            #     )

            return best_pose, inlier_count, best_model
