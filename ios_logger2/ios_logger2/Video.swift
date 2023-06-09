//
//  Accelerometer.swift
//  ios_logger2
//

import Foundation
import AVFoundation
import ARKit
import CoreMotion


/*
 *  Implements data collection and encoding of image frames from ARKit
 */
class Video: Sensor {
    var sensorName: String = "video"
    var series: AccelerometerSeries = AccelerometerSeries() // placeholder for now does not do anything
    
    private let fileType: AVFileType = AVFileType.mp4
    private let fileLocation: URL
    private var encoder: AVAssetWriter
    private let encoderInput: AVAssetWriterInput
    private let bufferInput: AVAssetWriterInputPixelBufferAdaptor
    private var frameNum: Int64 = 0
    private var frameRate: Int32 = 60
    
    init() {
        fileLocation = NSURL.fileURL(withPathComponents: [NSTemporaryDirectory(), NSUUID().uuidString])!
        encoder = try! AVAssetWriter(outputURL: fileLocation, fileType: fileType) // this should not fail because a temp file should always exist
        
        let outputSettings: [String: Any] = [
            AVVideoCodecKey: AVVideoCodecType.hevc,
            // todo figure this out
            AVVideoWidthKey:  1920, // CVPixelBufferGetWidthOfPlane(pixelBuffer,0),
            AVVideoHeightKey: 1080 // CVPixelBufferGetHeightOfPlane(pixelBuffer, 0)],
        ]
        encoderInput = AVAssetWriterInput(mediaType: AVMediaType.video, outputSettings: outputSettings)
        bufferInput = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: encoderInput, sourcePixelBufferAttributes: nil)
        bufferInput.assetWriterInput.expectsMediaDataInRealTime = true
        
        if(encoder.canAdd(encoderInput)) {
            encoder.add(encoderInput)
        }
        else {
            print("[ERROR] While starting video encoder")
        }
        
        if(!encoder.startWriting()) {
            print("[ERROR] While starting video encoder")
        }
        encoder.startSession(atSourceTime: CMTime.zero)
    }
    
    
    
    func collectData(motion: CMDeviceMotion?, frame: ARFrame?) {
        if(frame != nil) {
            if(encoderInput.isReadyForMoreMediaData) {
                let imageBuffer: CVPixelBuffer = frame!.capturedImage
                let bufferTimestamp: CMTime = CMTimeMake(value: frameNum, timescale: frameRate) // this seems very wrong but this is the way ios_logger had it written
                if(!bufferInput.append(imageBuffer, withPresentationTime: bufferTimestamp)) {
                    print("[WARN]: Failed to add ARFrame to video buffer")
                }
                else {
                    print("[INFO]: Appended ARFrame to video buffer")
                }
                frameNum += 1
            }
            else {
                //print("not ready")
            }
        }
        else {
            //print("empty frame")
        }

    }
    
    func additionalUpload() async {
        encoderInput.markAsFinished()
        await encoder.finishWriting()
        print("[INFO]: Video encoder finished writing file to disk")
        
        let videoData: Data? = try? Data(contentsOf: fileLocation)
        if(videoData != nil) {
            UploadManager.shared.putData(videoData!, contentType: "application/protobuf", fullPath: sensorName + ".mp4")
        }
        else {
            print("[EROR]: Reading video file from disk")
        }
    }
}
