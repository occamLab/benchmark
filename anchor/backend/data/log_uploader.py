from anchor.backend.data.firebase import FirebaseDownloader
from pathlib import Path
import sys, tempfile

with tempfile.NamedTemporaryFile(mode="w") as tmp:
    model_name = None
    print(model_name)
    for line in map(str.rstrip, sys.stdin):
        if line == "[INFO]: No new videos in firebase iosLoggerDemo/tarQueue": 
            exit(0)
        if model_name == None:
            model_name = line
        else:
            tmp.write(line)
    tmp.flush()

    firebaseDownloader = FirebaseDownloader("", "")
    firebaseDownloader.upload_file(
        (Path("iosLoggerDemo") / "trainingLogs" / Path(model_name).stem).as_posix() + ".txt", tmp.name)
    