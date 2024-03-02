from functools import cached_property
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict
from functools import cached_property
from matplotlib.image import imread
import numpy as np
import json
from matplotlib.figure import Figure

DATA_DIR = Path(__file__).parent.parent.parent / "data/.cache/firebase_data"


@dataclass
class FrameData:
    frame_num: int
    timestamp: float
    ACE: List[float]
    ACE_INLIER_COUNT: str
    ARKIT: List[float]
    CLOUD_ANCHOR: List[float]

    @property
    def homogeneous_ace_pose(self) -> np.ndarray:
        return np.reshape(self.ACE, [4, 4], order="F")

    @property
    def translation_ace(self) -> np.ndarray:
        return self.homogeneous_ace_pose[0:3, 3]

    @property
    def homogeneous_arkit_pose(self) -> np.ndarray:
        return np.reshape(self.ARKIT, [4, 4], order="F")

    @property
    def translation_arkit(self) -> np.ndarray:
        return self.homogeneous_arkit_pose[0:3, 3]

    @property
    def homogeneous_cloud_anchor_pose(self) -> np.ndarray:
        if not self.CLOUD_ANCHOR:
            return None
        return np.reshape(self.CLOUD_ANCHOR, [4, 4], order="F")

    @property
    def translation_cloud_anchor(self) -> np.ndarray:
        if not self.CLOUD_ANCHOR:
            return None
        return self.homogeneous_cloud_anchor_pose[0:3, 3]

    @property
    def image_file_name(self) -> str:
        ret = str(self.frame_num)
        while len(ret) < 5:
            ret = "0" + ret
        return f"{ret}.color.jpg"

    @property
    def annotated_image_file_name(self) -> str:
        return f"annotated_{self.frame_num}.png"


@dataclass
class VizDatum:
    frame_num: int
    t_err: float
    inlier_count: int
    img_rgb: np.ndarray


@dataclass
class TestDatum:
    frames: List[FrameData]
    root_dir: Path
    RECORDING_FPS: int = 60

    @cached_property
    def ace_poses(self) -> List[np.ndarray]:
        return np.array([frame.homogeneous_ace_pose for frame in self.frames])

    @cached_property
    def ace_translations(self) -> List[np.ndarray]:
        return np.array([frame.translation_ace for frame in self.frames])

    @cached_property
    def arkit_poses(self) -> List[np.ndarray]:
        return np.array([frame.homogeneous_arkit_pose for frame in self.frames])

    @cached_property
    def arkit_translations(self) -> List[np.ndarray]:
        return np.array([frame.translation_arkit for frame in self.frames])

    @cached_property
    def cloud_anchor_start_idx(self) -> int:
        for idx, frame in enumerate(self.frames):
            if frame.CLOUD_ANCHOR:
                return idx

    @cached_property
    def cloud_anchor_poses(self) -> List[np.ndarray]:
        return np.array(
            [
                frame.homogeneous_cloud_anchor_pose
                for frame in self.frames[self.cloud_anchor_start_idx :]
            ]
        )

    @cached_property
    def cloud_anchor_translations(self) -> List[np.ndarray]:
        return np.array(
            [
                frame.translation_cloud_anchor
                for frame in self.frames[self.cloud_anchor_start_idx :]
            ]
        )

    @cached_property
    def ace_translational_errors(self) -> List[np.ndarray]:
        diff = self.ace_translations - self.arkit_translations
        return np.linalg.norm(diff, axis=1)

    @cached_property
    def cloud_anchor_translational_errors(self) -> List[np.ndarray]:
        diff = (
            self.cloud_anchor_translations
            - self.arkit_translations[self.cloud_anchor_start_idx :]
        )
        return np.linalg.norm(diff, axis=1)

    @property
    def inliers(self) -> List[int]:
        return np.array([int(frame.ACE_INLIER_COUNT) for frame in self.frames])

    def get_ace_translational_err_at_idx(self, frame_idx: int):
        return self.ace_translational_errors[frame_idx]

    def get_ace_translations_with_inlier_thresh(self, inlier_threshold: int):
        return self.ace_translations[self.inliers > inlier_threshold]

    def get_viz_frames(self, step_fps: int, annotated_frames: bool) -> List[VizDatum]:
        idx_step = int(self.RECORDING_FPS // step_fps)
        if annotated_frames:
            img_dir = self.root_dir.parent / "annotated_rgb"
        else:
            img_dir = self.root_dir.parent / "rgb"
        return [
            VizDatum(
                frame_num=frame.frame_num,
                t_err=self.get_ace_translational_err_at_idx(idx * idx_step),
                inlier_count=frame.ACE_INLIER_COUNT,
                img_rgb=np.rot90(
                    imread(
                        img_dir
                        / f"{frame.annotated_image_file_name if annotated_frames else frame.image_file_name}"
                    ),
                    3,
                ),
            )
            for (idx, frame) in enumerate(self.frames[0 : len(self.frames) : idx_step])
        ]

    def get_ace_avg_translation_err_for_inlier_count(self, inlier_count: int) -> float:
        return np.mean(self.ace_translational_errors[self.inliers > inlier_count])

    def get_cloud_anchor_avg_translation_err(self) -> float:
        return np.mean(self.cloud_anchor_translational_errors)

    def get_ace_avg_translation_errs(self) -> Dict[int, float]:
        inliers = [0, 100, 200, 500, 1000]
        return {
            inlier: self.get_ace_avg_translation_err_for_inlier_count(inlier)
            for inlier in inliers
        }

    def plot_data(self, fig: Figure) -> None:
        ax = fig.add_subplot(2, 3, 1, projection="3d")

        ax.scatter(
            self.arkit_translations[:, 0],
            self.arkit_translations[:, 1],
            self.arkit_translations[:, 2],
            label="ARKIT",
            marker="o",
        )

        ax.scatter(
            self.cloud_anchor_translations[:, 0],
            self.cloud_anchor_translations[:, 1],
            self.cloud_anchor_translations[:, 2],
            label=f"CLOUD ANCHOR",
            marker="x",
        )

        ax.set_ylim([-0.5, 0.5])
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title(
            f"CA (Avg Trans. Err: {self.get_cloud_anchor_avg_translation_err():.4f}, {len(self.cloud_anchor_translations)}/{len(self.arkit_translations)} Frames)"
        )
        ax.legend()

        for idx, (num_inlier, trans_err) in enumerate(
            self.get_ace_avg_translation_errs().items()
        ):
            ace_poses_filt = self.get_ace_translations_with_inlier_thresh(num_inlier)

            ax = fig.add_subplot(2, 3, idx + 2, projection="3d")
            ax.scatter(
                self.arkit_translations[:, 0],
                self.arkit_translations[:, 1],
                self.arkit_translations[:, 2],
                label="ARKIT",
                marker="o",
            )

            ax.scatter(
                ace_poses_filt[:, 0],
                ace_poses_filt[:, 1],
                ace_poses_filt[:, 2],
                label=f"ACE ({num_inlier} Inliers)",
                marker="x",
            )

            ax.set_ylim([-0.5, 0.5])
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_zlabel("Z")

            ax.set_title(
                f"ACE (Avg Trans. Err: {trans_err:.4f}, {len(ace_poses_filt)}/{len(self.arkit_translations)} Frames)"
            )
            ax.legend()


@dataclass
class TestInfo:
    tar_name: str
    time: str
    data: TestDatum

    @property
    def tar_path(self) -> Path:
        return DATA_DIR / self.tar_name.rstrip(".tar")

    @cached_property
    def test_data_dir(self) -> Path:
        base_dir = self.tar_path / "ace/test"
        subdirs = [
            x
            for x in [y for y in os.walk(base_dir)][0][1]
            if x not in ["annotated_rgb", "calibration", "poses", "rgb"]
        ]
        if len(subdirs) > 1:
            raise RuntimeError(f"Too many directories in {base_dir}")

        if len(subdirs) == 0:
            raise RuntimeError(f"No ACE benchmark data in {base_dir}")

        return base_dir / subdirs[0]

    @property
    def pose_json_path(self) -> Path:
        if not (path := self.test_data_dir / "mapped_poses.json"):
            raise RuntimeError(f"Re-run ACE, Poses file was not generated")
        return path

    def load_data(self) -> None:
        with open(self.pose_json_path, "r") as file:
            data = json.load(file)["data"]

        frames = [FrameData(**frame) for frame in data]
        self.data = TestDatum(frames=frames, root_dir=self.pose_json_path)

    def __repr__(self) -> str:
        return f"{self.tar_name} @ {self.time}"


@dataclass
class MapTestInfo:
    name: str
    mapping_time: str
    metadata: str
    tests: List[TestInfo]

    def load_all_data(self) -> None:
        for test in self.tests:
            test.load_data()
