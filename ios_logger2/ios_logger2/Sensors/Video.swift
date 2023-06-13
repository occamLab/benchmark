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
    var series: VideoAttributes = VideoAttributes()
    
    private let fileType: AVFileType = AVFileType.mp4
    private let fileLocation: URL
    private var encoder: AVAssetWriter
    private let encoderInput: AVAssetWriterInput
    private let bufferInput: AVAssetWriterInputPixelBufferAdaptor
    private var frameRate: Int32 = 60
    private var initialTimestamp: Double? = nil
    
    init() {
        fileLocation = NSURL.fileURL(withPathComponents: [NSTemporaryDirectory(), NSUUID().uuidString])!
        encoder = try! AVAssetWriter(outputURL: fileLocation, fileType: fileType) // this should not fail because a temp file should always exist
        
        let outputSettings: [String: Any] = [
            AVVideoCodecKey: AVVideoCodecType.hevc,
            AVVideoWidthKey:  1920, // CVPixelBufferGetWidthOfPlane(pixelBuffer,0),
            AVVideoHeightKey: 1080, // CVPixelBufferGetHeightOfPlane(pixelBuffer, 0)],
            AVVideoCompressionPropertiesKey: [
                AVVideoAverageBitRateKey: 1024 * 100, // 100 Kib/seconds,
                AVVideoQualityKey: 0.7, // between 0 and 1.0, some people say it does not do anything, some people say it does...
            ] as [String : Any],
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
            initialTimestamp = initialTimestamp ?? frame!.timestamp // set the first frame time as reference if needed
            series.videoStartUnixTimestamp = getUnixTimestamp(moment: (initialTimestamp ?? frame!.timestamp))
            
            let timeSinceStart = frame!.timestamp - initialTimestamp! // absolute time since first frame
            
            if(encoderInput.isReadyForMoreMediaData) {
                // the bufferTimestamp should conform to value/timescale = seconds since atSourceTime (CMTime.zero)
                let imageBuffer: CVPixelBuffer = frame!.capturedImage
                let bufferTimestamp: CMTime = CMTimeMake(value: Int64(timeSinceStart * Double(frameRate) * 1000.0), timescale: frameRate * 1000)
                if(!bufferInput.append(imageBuffer, withPresentationTime: bufferTimestamp)) {
                    print("[WARN]: Failed to add ARFrame to video buffer")
                }
                else {
                   // print("[INFO]: Appended ARFrame to video buffer")
                }
            }
            else {
            }
        }
        else {
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