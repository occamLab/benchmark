from firebase_admin import credentials, storage, initialize_app
import anchor.backend.data.proto.intrinsics_pb2 as Intrinsics
import anchor.backend.data.proto.video_pb2 as video_pb2

from pathlib import Path
import cv2
import shutil
import tempfile
import av


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

        self.extract_ios_logger_video(extract_path / "mapping-video.mp4", True)
        self.extract_ios_logger_video(extract_path / "localization-video.mp4", False)
        self.extract_protobuf(extract_path)

        return extract_path / "extracted"

    def extract_ios_logger_video(self, video_path: Path, mapping_phase: bool):
        print(f'[INFO]: Extracting video {video_path} to frames')
        metadata_path = video_path.parent / "video.proto"
        video_metadata = video_pb2.VideoData()

        with open(metadata_path, "rb") as fd:
            video_metadata.ParseFromString(fd.read())

        if mapping_phase:
            video_start = video_metadata.mappingPhase.videoAttributes.videoStartUnixTimestamp
        else:
            video_start = video_metadata.localizationPhase.videoAttributes.videoStartUnixTimestamp

        container = av.open(video_path.as_posix())


        for frame in container.decode():

            image_timestamp = video_start + float(frame.pts * frame.time_base)
            frame_path: Path = video_path.parent / "extracted" / video_path.stem / f'{frame.index}.jpg'
            frame_path.parent.mkdir(parents=True, exist_ok=True)
            frame.to_image().save(frame_path.as_posix())
            print(image_timestamp)


    def extract_protobuf(self, extract_path: Path):
        """
        Returns a list of dictionaries each containing a timestamp and the four
        intrinsics for each frame in the video's mapping phase.
        
        Args: 
            extract_path (str): the path to the video being extracted that we are
            getting the camera intrinsics from.
        
        Returns:
            A list of dictionaries; each dictionary has attributes timestamp,
            fx, fy, cx, and cy for a particular frame.
        """
        
        print(f'[INFO]: Reading protobuf {extract_path}')
        intrinsics_path = extract_path / "intrinsics.proto"
        intrinsics_data = Intrinsics.IntrinsicsData()
        with open(intrinsics_path, "rb") as fd:
            intrinsics_data.ParseFromString(fd.read())
            intrinsics_list = []
            for value in intrinsics_data.localizationPhase.measurements:
                k = value.cameraIntrinsics
                fx, fy, cx, cy = k[0], k[4], k[6], k[7]
                t = value.timestamp
                intrinsics = {"timestamp": t, "fx": fx, "fy": fy, "cx": cx, "cy": cy}
                intrinsics_list.append(intrinsics)
                print("timestamp ", t)
            print(len(intrinsics_list))
            return(intrinsics_list)
        
# test the extractor here
if __name__ == '__main__':
    downloader_1 = FirebaseDownloader()
    downloader_1.extract_ios_logger_tar("iosLoggerDemo/Ljur5BYFXdhsGnAlEsmjqyNG5fJ2",
                                        "047F9850-20BB-4AC0-9650-C2558C9EFC03.tar")
