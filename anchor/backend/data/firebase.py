from firebase_admin import db
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import initialize_app
import pathlib


class FirebaseDownloader:
    service_account_name: str = "stepnavigation-firebase-adminsdk-service-account.json"
    service_account_path: str = (pathlib.Path(__file__).parent.parent.parent / service_account_name).as_posix()
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


downloader_1 = FirebaseDownloader()
downloader_1.download_file("img-03721_VsLSX1xh.mp4", "test1.mp4")

downloader_2 = FirebaseDownloader()
downloader_2.download_file("img-03721_VsLSX1xh.mp4", "test2.mp4")
