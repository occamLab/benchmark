# Benchmark
Tools for benchmarking alternatives to cloud anchors

# Install
We use protobuf for serializing data. You can install swift-protobuf (https://github.com/apple/swift-protobuf#alternatively-install-via-homebrew) from brew: 
```
brew install swift-protobuf
```

# Protobuf Instructions
First you need to compile the protobuf files: 
```
cd ios_logger2
protoc --swift_opt=FileNaming=DropPath --swift_out=protos/codegen protos/*.proto
```
Then to get swift to recognize them: 
  1) Right click on the "protos" folder 
  2) Press "Add files to ios_logger2" 
  3) Select the generated files (or the whole folder)

# Swift Dependencies 
1) https://github.com/tsolomko/SWCompression (used in UploadManager.swift)
2) https://github.com/firebase/firebase-ios-sdk (used to upload data to firebase)
3) https://github.com/apple/swift-protobuf (used to encode swift types to binary) 
4) https://github.com/google-ar/arcore-ios-sdk (ArCore for CloudAnchors)
