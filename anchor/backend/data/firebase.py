from firebase_admin import db
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import initialize_app
from uuid import uuid4
import pathlib

service_account_name: str = "stepnavigation-firebase-adminsdk-service-account.json"
service_account_path: str = (pathlib.Path(__file__).parent.parent.parent / service_account_name).as_posix()
# do not prefix bucket name with gs:// https://github.com/firebase/firebase-admin-python/issues/280#issuecomment-484980833
firebase_bucket_name: str = "stepnavigation.appspot.com"

cred = credentials.Certificate(service_account_path)
initialize_app(cred)

bucket = storage.bucket(firebase_bucket_name)
blob = bucket.blob("img-03721_VsLSX1xh.mp4")
blob.download_to_filename(filename="img-03721_VsLSX1xh.mp4")
