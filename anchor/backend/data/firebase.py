from firebase_admin import db
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import initialize_app
from uuid import uuid4


cred = credentials.Certificate('stepnavigation-firebase-adminsdk-service-account.json')
initialize_app(cred, {
    'databaseURL' : 'https:url.firebaseio.com/', 'storageBucket': 'gs://stepnavigation.appspot.com'
})
bucket = storage.bucket()
blob = bucket.blob("img-03721_VsLSX1xh.mp4")
new_token = uuid4()
metadata  = {"firebaseStorageDownloadTokens": new_token}
blob.metadata = metadata
blob.download_to_filename(filename="img-03721_VsLSX1xh.mp4")