# Anchor Backend

# Install

Init the third_party submodule hloc with: 
```
git submodule update --init --recursive
```

To install python deps make sure that you have conda (https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html) installed. The niantic/ace dep uses conda to manage their install so we are forced to use it as well. 
```
source ./install.sh
```

To install the protobuf compiler on ubuntu with apt run:
```
sudo apt-get install -y protobuf-compiler
```

To compile the protobuf definitions into ```anchor.backend.data.proto``` run the following from the root of the repo:
```
protoc --proto_path=ios_logger2/ios_logger2/protos --python_out=anchor/backend/data/proto ios_logger2/ios_logger2/protos/*.proto
```

# Credentials
Download a firebase admin service account and place in this folder with the following name: 
```
stepnavigation-firebase-adminsdk-service-account.json
```