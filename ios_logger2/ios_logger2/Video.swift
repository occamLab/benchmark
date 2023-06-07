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
    private var frameNum = 0
    private var frameRate = 60
    
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
        
        encoder.startWriting()
        encoder.startSession(atSourceTime: CMTime.zero)
    }
    
    
    
    func collectData(motion: CMDeviceMotion?, frame: ARFrame?) {
        if(encoderInput.isReadyForMoreMediaData) {
            
            frameNum += 1
        }
    }
}
