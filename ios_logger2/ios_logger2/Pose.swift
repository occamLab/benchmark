//
//  Pose.swift
//  ios_logger2
//
//  Created by Zoe McGinnis on 6/9/23.
//

import Foundation
import ARKit
import CoreMotion

/*
 *  Implements data collection and encoding into a protobuf message for timeseries of camera pose data
 */
class Pose: Sensor {
    var sensorName: String = "pose"
    public var series = PoseSeries()
    
    func collectData(motion: CMDeviceMotion?, frame: ARFrame?) {
        if(frame != nil) {
            let timestamp: Double = frame!.timestamp
            let transform: [Float] = frame!.camera.transform.toRowMajor()
            
            var measurement = PoseTimestamp()
            measurement.timestamp = timestamp
            measurement.cameraPose = transform
            series.measurements.append(measurement)
        }
    }
}

extension simd_float4x4 {
    public func toRowMajor()->[Float] {
        return [self[0,0], self[0,1], self[0,2], self[0,3], self[1,0], self[1,1], self[1,2], self[1,3], self[2,0], self[2,1], self[2,2], self[2,3], self[3,0], self[3,1], self[3,2], self[3,3]]
    }
}