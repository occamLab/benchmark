"""PULL ALL JSONS FROM FIREBASE"""
import firebase_admin
from firebase_admin import credentials, storage
import os

cred = credentials.Certificate("stepnavigation-firebase-adminsdk-service-account.json")
firebase_admin.initialize_app(cred, {"storageBucket": "stepnavigation.appspot.com"})

bucket = storage.bucket()
folder_path = "iosLoggerDemo/processedJsons"
local_directory = ".cache/"
os.makedirs(folder_path, exist_ok=True)
os.makedirs(local_directory, exist_ok=True)


# List all files in the specified folder
blobs = bucket.list_blobs(prefix=folder_path)

for blob in blobs:
    # Download the file to a local path
    destination_path = f"{blob.name}"

    # destination_path = os.path.join(local_directory, file)

    with open(f"{destination_path}", "w") as _:
        pass

    blob.download_to_filename(destination_path)
    print(f"File downloaded to: {destination_path}")
