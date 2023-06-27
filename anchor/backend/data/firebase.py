from firebase_admin import credentials, storage, initialize_app
import proto.intrinsics_pb2 as Intrinsics
import proto.pose_pb2 as Pose
from pathlib import Path
import cv2
import shutil
import tempfile


class FirebaseDownloader:
    service_account_name: str = "stepnavigation-firebase-adminsdk-service-account.json"
    service_account_path: str = (Path(__file__).parent.parent.parent / service_account_name).as_posix()
    # do not prefix bucket name with gs:// https://github.com/firebase/firebase-admin-python/issues/280#issuecomment-484980833
    firebase_bucket_name: str = "stepnavigation.appspot.com"
    initialized: bool = False

    # the root of where we download
    root_download_dir: Path = Path(tempfile.gettempdir()) / "benchmark"

    def __init__(self):
        # initialize_app should be called only once globally
        if not FirebaseDownloader.initialized:
            cred = credentials.Certificate(FirebaseDownloader.service_account_path)
            initialize_app(cred)
            FirebaseDownloader.initialized = True

    def download_file(self, remote_location: str, local_location: str):
        bucket = storage.bucket(FirebaseDownloader.firebase_bucket_name)
        blob = bucket.blob(remote_location)
        blob.download_to_filename(filename=local_location)

    def extract_ios_logger_tar(self, firebaseDir: str, tarName: str) -> Path:
        FirebaseDownloader.root_download_dir.mkdir(parents=True, exist_ok=True)
        if (FirebaseDownloader.root_download_dir / tarName).exists():
            print(f'[INFO]: Skipping download tar {tarName} as it already exists')
        else:
            self.download_file((Path(firebaseDir) / tarName).as_posix(), (FirebaseDownloader.root_download_dir / tarName).as_posix())
            print(f'[INFO]: Downloaded tar {tarName} as it has not been found locally')

        # unpack the tar itself and cleanup and previous extractions
        extract_path: Path = FirebaseDownloader.root_download_dir / Path(tarName).stem
        shutil.rmtree(extract_path, ignore_errors=True)
        shutil.unpack_archive(FirebaseDownloader.root_download_dir / tarName, extract_dir=extract_path)

        # extract the videos

        self.extract_ios_logger_video(extract_path / "mapping-video.mp4")
        self.extract_ios_logger_video(extract_path / "localization-video.mp4")
        self.extract_intrinsics(extract_path)
        self.extract_pose(extract_path)

        return extract_path / "extracted"

    def extract_ios_logger_video(self, video_path: Path):
        print(f'[INFO]: Extracting video {video_path} to frames')
        video = cv2.VideoCapture(video_path.as_posix())
        ret, frame = video.read()
        frame_num: int = 0
        while ret:
            frame_path: Path = video_path.parent / "extracted" / video_path.stem / f'{frame_num}.jpg'
            frame_path.parent.mkdir(parents=True, exist_ok=True)
            cv2.imwrite(frame_path.as_posix(), frame)
            ret, frame = video.read()
            frame_num += 1
        video.release()
    

    def extract_intrinsics(self, extract_path: Path):
        """
        Returns a list of dictionaries each containing a timestamp and the four
        intrinsics for each frame in the video's mapping phase.
        
        Args: 
            extract_path (str): the path to the folder containing the video 
            we are extracting and getting the intrinsics data from.
        
        Returns:
            A list of dictionaries; each dictionary has attributes timestamp,
            fx, fy, cx, and cy for a particular frame.
        """
        
        print(f'[INFO]: Reading intrinsics protobuf {extract_path}')
        intrinsics_path = extract_path / "intrinsics.proto"
        intrinsics_data = Intrinsics.IntrinsicsData()
        with open(intrinsics_path, "rb") as fd:
            intrinsics_data.ParseFromString(fd.read())
            intrinsics_list = []
            for value in intrinsics_data.mappingPhase.measurements:
                t = value.timestamp
                k = value.cameraIntrinsics
                fx, fy, cx, cy = k[0], k[4], k[6], k[7]
                intrinsics = {"timestamp": t, "fx": fx, "fy": fy, "cx": cx, "cy": cy}
                intrinsics_list.append(intrinsics)
            
            return(intrinsics_list)
        
    def extract_pose(self, extract_path: Path):
        """
        Returns a list of dictionaries each containing a timestamp, 
        translation, rotation matrix, and the real and imaginary parts of the 
        quaternion for each frame in the video's mapping phase.
        
        Args: 
            extract_path (str): the path to the folder containing the video 
            we are extracting and getting the pose data from.
        
        Returns:
            A list of dictionaries; each dictionary has the form: 
            {
                timestamp (float): timestamp from ARFrame
                translation ([float]): the translation values of [x, y, z] in 
                    that order
                rotationMatrix ([float]): 4x4 rotation matrix of the frame 
                    flattened into a single list by row
                quatImag ([float]): list of 3 imaginary values of the 
                    quaternion
                quatReal (float): real part of the quaternion
            }
        """
        
        print(f'[INFO]: Reading pose protobuf {extract_path}')
        pose_path = extract_path / "pose.proto"
        pose_data = Pose.PoseData()
        with open(pose_path, "rb") as fd:
            pose_data.ParseFromString(fd.read())
            pose_list = []
            for value in pose_data.mappingPhase.measurements:
                t = value.timestamp
                translation = value.poseTranslation
                rotationMatrix = value.rotMatrix
                quatImag = value.quatImag
                quatReal = value.quatReal
                pose = {"timestamp": t, "translation": translation, "rotationMatrix": rotationMatrix, "quatImag": quatImag, "quatReal": quatReal}
                pose_list.append(pose)
            
            return pose_list
        
# test the extractor here
if __name__ == '__main__':
    downloader_1 = FirebaseDownloader()
    downloader_1.extract_ios_logger_tar("iosLoggerDemo/Ljur5BYFXdhsGnAlEsmjqyNG5fJ2",
                                        "EE27F9BE-63AC-4343-B149-1816EC6EF2C7.tar")
