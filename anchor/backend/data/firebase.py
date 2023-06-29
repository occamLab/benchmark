from firebase_admin import credentials, storage, initialize_app
import anchor.backend.data.extracted
import anchor.backend.data.proto.pose_pb2 as Pose
import anchor.backend.data.proto.intrinsics_pb2 as Intrinsics
import anchor.backend.data.proto.video_pb2 as video_pb2

from pathlib import Path
import shutil
import tempfile
import av
import copy


class FirebaseDownloader:
    service_account_name: str = "stepnavigation-firebase-adminsdk-service-account.json"
    service_account_path: str = (Path(__file__).parent.parent.parent / service_account_name).as_posix()
    # do not prefix bucket name with gs:// https://github.com/firebase/firebase-admin-python/issues/280#issuecomment-484980833
    firebase_bucket_name: str = "stepnavigation.appspot.com"
    initialized: bool = False

    # the root of where we download
    root_download_dir: Path = Path(tempfile.gettempdir()) / "benchmark"

    def __init__(self, firebase_dir: str, tar_name: str):
        # initialize_app should be called only once globally
        if not FirebaseDownloader.initialized:
            cred = credentials.Certificate(FirebaseDownloader.service_account_path)
            initialize_app(cred)
            FirebaseDownloader.initialized = True

        self.firebase_dir = firebase_dir
        self.tar_name = tar_name

        self.local_tar_location = FirebaseDownloader.root_download_dir / self.tar_name
        self.local_extraction_location = FirebaseDownloader.root_download_dir / Path(self.tar_name).stem

        self.extracted_data = anchor.backend.data.extracted.Extracted(self.local_extraction_location)


    @staticmethod
    def proto_with_phase(given_proto: any, mapping_phase: bool):
        """
            Gets the phase message from the proto object. We encode all of our protos
            with the phase that the data was collected in.
        """
        return getattr(given_proto, "mappingPhase" if mapping_phase else "localizationPhase")

    def download_file(self, remote_location: str, local_location: str):
        bucket = storage.bucket(FirebaseDownloader.firebase_bucket_name)
        blob = bucket.blob(remote_location)
        blob.download_to_filename(filename=local_location)

    def extract_ios_logger_tar(self) -> Path:
        FirebaseDownloader.root_download_dir.mkdir(parents=True, exist_ok=True)
        if self.local_tar_location.exists():
            print(f'[INFO]: Skipping download tar {self.tar_name} as it already exists')
        else:
            self.download_file((Path(self.firebase_dir) / self.tar_name).as_posix(),
                               self.local_tar_location.as_posix())
            print(f'[INFO]: Downloaded tar {self.tar_name} as it has not been found locally')

        # unpack the tar itself and cleanup and previous extractions
        shutil.rmtree(self.local_extraction_location, ignore_errors=True)
        shutil.unpack_archive(self.local_tar_location, extract_dir=self.local_extraction_location)

        # extract the videos

        self.extract_ios_logger_video(self.local_extraction_location / "mapping-video.mp4", True)
        self.extract_ios_logger_video(self.local_extraction_location / "localization-video.mp4", False)


        self.extract_intrinsics(self.local_extraction_location, True)
        self.extract_intrinsics(self.local_extraction_location, False)

        self.extract_pose(self.local_extraction_location, True)
        self.extract_pose(self.local_extraction_location, False)

        # print(self.extracted_data.sensors_extracted)
        self.extracted_data.match_all_sensor()


        return self.local_extraction_location / "extracted"

    def extract_ios_logger_video(self, video_path: Path, mapping_phase: bool):
        print(f'[INFO]: Extracting video {video_path} to frames')
        metadata_path = video_path.parent / "video.proto"
        video_metadata = video_pb2.VideoData()

        with open(metadata_path, "rb") as fd:
            video_metadata.ParseFromString(fd.read())

        video_start = FirebaseDownloader.proto_with_phase(video_metadata, mapping_phase).videoAttributes.videoStartUnixTimestamp

        container = av.open(video_path.as_posix())
        container.streams.video[0].thread_type = "AUTO"

        video_folder_path = Path = video_path.parent / "extracted" / video_path.stem
        video_folder_path.mkdir(parents=True, exist_ok=True)

        for frame in container.decode():
            print(frame)
            image_timestamp = video_start + float(frame.pts * frame.time_base)
            frame_path: Path = video_folder_path/ f'{frame.index}.jpg'
            frame.to_image().save(frame_path.as_posix())
            self.extracted_data.append_video_timestamp(image_timestamp, frame_path, frame.index, mapping_phase)

    def extract_intrinsics(self, extract_path: Path, mapping_phase: bool):
        """
        Returns a list of dictionaries each containing a timestamp and the four
        intrinsics for each frame in the video's mapping phase.
        
        Args: 
            extract_path (str): the path to the folder containing the video 
            we are extracting and getting the intrinsics data from.
            mapping_phase (bool): determines which phase we are in (mapping/localization)
        
        Returns: (void)
            Appends data to the Extracted class
        """

        print(f'[INFO]: Reading intrinsics protobuf {extract_path}')
        intrinsics_path = extract_path / "intrinsics.proto"
        intrinsics_data = Intrinsics.IntrinsicsData()
        with open(intrinsics_path, "rb") as fd:
            intrinsics_data.ParseFromString(fd.read())
            for value in FirebaseDownloader.proto_with_phase(intrinsics_data, mapping_phase).measurements:
                t = value.timestamp
                k = value.cameraIntrinsics
                fx, fy, cx, cy = k[0], k[4], k[6], k[7]
                self.extracted_data.append_intrinsics_data(t, fx, fy, cx, cy, mapping_phase)

    def extract_pose(self, extract_path: Path, mapping_phase: bool):
        """
        Args: 
            extract_path (str): the path to the folder containing the video 
            we are extracting and getting the pose data from.
            mapping_phase (bool): determines which phase we are in (mapping/localization)

        
        Returns: (void)
            Appends data to the Extracted class with the following form:

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
            for value in FirebaseDownloader.proto_with_phase(pose_data, mapping_phase).measurements:
                t = value.timestamp
                translation = value.poseTranslation
                rotation_matrix = value.rotMatrix
                quat_imag = value.quatImag
                quat_real = value.quatReal
                pose = {
                    "timestamp": t,
                    "translation": translation,
                    "rotation_matrix": rotation_matrix,
                    "quat_imag": quat_imag,
                    "quat_real": quat_real
                }
                print(pose)
                self.extracted_data.append_pose_data(pose, mapping_phase)


# test the extractor here
if __name__ == '__main__':
    downloader_1 = FirebaseDownloader("iosLoggerDemo/Ljur5BYFXdhsGnAlEsmjqyNG5fJ2", "047F9850-20BB-4AC0-9650-C2558C9EFC03.tar")
    downloader_1.extract_ios_logger_tar()
