//
//  Accelerometer.swift
//  ios_logger2
//

import Foundation
import AVFoundation
import ARKit
import CoreMotion


class CurrentVideo {
    let fileType: AVFileType = AVFileType.mp4
    let fileLocation: URL
    let encoder: AVAssetWriter
    let encoderInput: AVAssetWriterInput
    let bufferInput: AVAssetWriterInputPixelBufferAdaptor
    let frameRate: Int32 = 60
    
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
        // see https://stackoverflow.com/a/43337235 on why this is important
        bufferInput.assetWriterInput.mediaTimeScale = 600000000 // something really high to avoid rounding errors
        
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
}

/*
 *  Implements data collection and encoding of image frames from ARKit
 */
class Video: Sensor, SensorProtocol {
    var sensorName: String = "video"
    var series: VideoData = VideoData()
    
    var currentVideo: CurrentVideo = CurrentVideo()
    private var initialTimestamp: Double? = nil
    
    
    func collectData(motion: CMDeviceMotion?, frame: ARFrame?) {
        if(frame != nil) {
            initialTimestamp = initialTimestamp ?? frame!.timestamp // set the first frame time as reference if needed
            // save the absolute time when the video started into metadata attributes if needed
            if case currentPhase = Phase.mappingPhase {
                series.mappingPhase.videoAttributes.videoStartUnixTimestamp = getUnixTimestamp(moment: (initialTimestamp ?? frame!.timestamp))
            }
            else {
                series.localizationPhase.videoAttributes.videoStartUnixTimestamp = getUnixTimestamp(moment: (initialTimestamp ?? frame!.timestamp))
            }
            
            let timeSinceStart = frame!.timestamp - initialTimestamp! // absolute time since first frame
            
            if(currentVideo.encoderInput.isReadyForMoreMediaData) {
                // the bufferTimestamp should conform to value/timescale = seconds since atSourceTime (CMTime.zero)
                let imageBuffer: CVPixelBuffer = frame!.capturedImage
                let bufferTimestamp: CMTime = CMTimeMake(value: Int64(timeSinceStart * Double(currentVideo.frameRate) * 1000.0), timescale: currentVideo.frameRate * 1000)
                if(!currentVideo.bufferInput.append(imageBuffer, withPresentationTime: bufferTimestamp)) {
                   // print("[WARN]: Failed to add ARFrame to video buffer")
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
        currentVideo.encoderInput.markAsFinished()
        if(currentVideo.encoder.status == .writing) {
            await currentVideo.encoder.finishWriting()
        }
        print("[INFO]: Video encoder finished writing file to disk")
        
        let videoData: Data? = try? Data(contentsOf: currentVideo.fileLocation)
        if(videoData != nil) {
            uploadDataWithPhase(data: videoData!, fileExtension: ".mp4", contentType: "video/mp4")
        }
        else {
            print("[EROR]: Reading video file from disk")
        }
    }
    
    func switchToLocalization() {
        // reset to a new video
        currentVideo = CurrentVideo()
        // initial frame timestamp needs to be set
        initialTimestamp = nil
    }
}
