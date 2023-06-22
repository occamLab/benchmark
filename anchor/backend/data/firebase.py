from firebase_admin import credentials, storage, initialize_app
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

    def extract_ios_logger_tar(self, firebaseDir: str, tarName: str) -> str:
        tmp: Path = Path(tempfile.gettempdir()) / "benchmark"
        tmp.mkdir(parents=True, exist_ok=True)
        if (tmp / tarName).exists():
            print(f'[INFO]: Skipping download tar {tarName} as it already exists')
        else:
            self.download_file((Path(firebaseDir) / tarName).as_posix(), (tmp / tarName).as_posix())
            print(f'[INFO]: Downloaded tar {tarName} as it has not been found locally')

        # unpack the tar itself and cleanup and previous extractions
        extract_path: Path = tmp / Path(tarName).stem
        shutil.rmtree(extract_path)
        shutil.unpack_archive(tmp / tarName, extract_dir=extract_path)

        # extract the videos
        self.extract_ios_logger_video(extract_path / "mapping-video.mp4")
        self.extract_ios_logger_video(extract_path / "localization-video.mp4")

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

# test the extractor here
if __name__ == '__main__':
    downloader_1 = FirebaseDownloader()
    downloader_1.extract_ios_logger_tar("iosLoggerDemo/DQP1QbWk6WVZOFN6OpZiQXsfpsB3",
                                        "27FB2D9E-5898-4DC9-97AB-7D08F231E649.tar")
