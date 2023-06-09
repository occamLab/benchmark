//
//  Gyro.swift
//  ios_logger2
//
//  Created by Zoe McGinnis on 6/8/23.
//

import Foundation
import ARKit
import CoreMotion

/*
 *  Implements data collection and encoding into a protobuf message for timeseries of gyroscope data
 */

class Gyro: Sensor {
    public var series = GyroSeries()
    
    func collectData(motion: CMDeviceMotion?, frame: ARFrame?) {
        if(motion != nil) {
            let timestamp: Double = motion!.timestamp
            let rotation_rate_x: Double = motion!.rotationRate.x
            let rotation_rate_y: Double =  motion!.rotationRate.y
            let rotation_rate_z: Double =  motion!.rotationRate.z
            
            
            var measurement = GyroTimestamp()
            measurement.timestamp = timestamp
            measurement.xRotationRate = rotation_rate_x
            measurement.yRotationRate = rotation_rate_y
            measurement.zRotationRate = rotation_rate_z
            series.measurements.append(measurement)
            
        }
    }
}
