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
        
        encoder.startWriting()
        encoder.startSession(atSourceTime: CMTime.zero)
    }
    
    
    
    func collectData(motion: CMDeviceMotion?, frame: ARFrame?) {
        print("test")
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
        }

    }
}
