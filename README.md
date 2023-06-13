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

# Note on https://github.com/google-ar/arcore-ios-sdk
1) Linker flag -ObjC must be turned on as per https://github.com/google-ar/arcore-ios-sdk/tree/master#installation
2) Otherwise you will get the most cryptic crash message that will waste way too much of your time. The error will be along the lines of: 
```swift
2023-06-12 15:25:58.395537-0400 ios_logger2[24686:2190906] +[GARDeviceProfile profileForIdentifier:osVersion:configurationManager:]: unrecognized selector sent to class 0x104ecf820
2023-06-12 15:25:58.396973-0400 ios_logger2[24686:2190906] *** Terminating app due to uncaught exception 'NSInvalidArgumentException', reason: '+[GARDeviceProfile profileForIdentifier:osVersion:configurationManager:]: unrecognized selector sent to class 0x104ecf820'
```
