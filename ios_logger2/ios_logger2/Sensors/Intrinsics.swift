//
//  Intrinsics.swift
//  ios_logger2
//
//  Created by Zoe McGinnis on 6/9/23.
//

import Foundation
import ARKit
import CoreMotion

/*
 *  Implements data collection and encoding into a protobuf message for timeseries of camera intrinsics data
 */
class Intrinsics: Sensor {
    var sensorName: String = "intrinsics"
    public var series = IntrinsicsSeries()
    
    func collectData(motion: CMDeviceMotion?, frame: ARFrame?) {
        if(frame != nil) {
            let timestamp: Double = getUnixTimestamp(moment: frame!.timestamp)
            let intrinsics: [Float] = frame!.camera.intrinsics.toRowMajor()
            
            var measurement = IntrinsicsTimestamp()
            measurement.timestamp = timestamp
            measurement.cameraIntrinsics = intrinsics
            series.measurements.append(measurement)
        }
    }
}


extension simd_float3x3 {
    public func toRowMajor()->[Float] {
        return [self[0,0], self[0,1], self[0,2], self[1,0], self[1,1], self[1,2], self[2,0], self[2,1], self[2,2]]
    }
}