//
//  LiDAR.swift
//  ios_logger2
//
//  Created by Zoe McGinnis on 6/8/23.
//

import Foundation
import ARKit
import CoreMotion

class LiDAR : Sensor, SensorProtocol {
    var sensorName: String = "lidar"
    public var series = LidarData()
    
    func collectData(motion: CMDeviceMotion?, frame: ARFrame?, arView: ARSCNView) {
        if(frame != nil) {
            guard let sceneDepth = frame!.sceneDepth, let confidenceMap = sceneDepth.confidenceMap else {
                return
            }
            saveSceneDepth(depthMapBuffer: sceneDepth.depthMap, confMapBuffer: confidenceMap, frame: frame!)
        }
    }

    // - MARK: Creating point cloud
    func saveSceneDepth(depthMapBuffer: CVPixelBuffer, confMapBuffer: CVPixelBuffer, frame: ARFrame) {
        let width = CVPixelBufferGetWidth(depthMapBuffer)
        let height = CVPixelBufferGetHeight(depthMapBuffer)
        // does this line do anything?
        CVPixelBufferLockBaseAddress(depthMapBuffer, CVPixelBufferLockFlags(rawValue: 0))
        // what is to? is it an argument?
        let depthBuffer = unsafeBitCast(CVPixelBufferGetBaseAddress(depthMapBuffer), to: UnsafeMutablePointer<Float32>.self)
        var depthCopy = [Float32](repeating: 0.0, count: width*height)
        memcpy(&depthCopy, depthBuffer, width*height*MemoryLayout<Float32>.size)
        CVPixelBufferUnlockBaseAddress(depthMapBuffer, CVPixelBufferLockFlags(rawValue: 0))
        var confCopy = [ARConfidenceLevel](repeating: .high, count: width*height)
        CVPixelBufferLockBaseAddress(confMapBuffer, CVPixelBufferLockFlags(rawValue: 0))
        let confBuffer = unsafeBitCast(CVPixelBufferGetBaseAddress(confMapBuffer), to: UnsafeMutablePointer<UInt8>.self)
        for i in 0..<width*height {
            confCopy[i] = ARConfidenceLevel(rawValue: Int(confBuffer[i])) ?? .low
        }
        
        let confInts = confCopy.map { (ARConfidenceLevel) -> UInt32 in
            UInt32(ARConfidenceLevel.rawValue)
        }
        
        var measurement = LidarTimestamp()
        measurement.timestamp = getUnixTimestamp(moment: frame.capturedDepthDataTimestamp)
        measurement.lidar = depthCopy
        measurement.conf = confInts
        
        if case currentPhase = Phase.mappingPhase {
            series.mappingPhase.measurements.append(measurement)
        }
        else {
            series.localizationPhase.measurements.append(measurement)
        }
        
    }
}
