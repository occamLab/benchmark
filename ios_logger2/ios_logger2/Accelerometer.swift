//
//  Accelerometer.swift
//  ios_logger2
//

import Foundation
import ARKit
import CoreMotion

/*
 *  Implements data collection and encoding into a protobuf message for timeseries of accelerometer data
 */
class Accelerometer: Sensor {
    public var series = AccelerometerSeries()
    
    func collectData(motion: CMDeviceMotion?, frame: ARFrame?) {
        if(motion != nil) {
            let timestamp: Double = motion!.timestamp
            let acceleration_x: Double = motion!.userAcceleration.x
            let acceleration_y: Double =  motion!.userAcceleration.y
            let acceleration_z: Double =  motion!.userAcceleration.z
            
            
            var measurement = AccelerometerTimestamp()
            measurement.timestamp = timestamp
            measurement.xAcceleration = acceleration_x
            measurement.yAcceleration = acceleration_y
            measurement.zAcceleration = acceleration_z
            series.measurements.append(measurement)
            
            // print(acceleration_x, acceleration_y)
            
            // frame!.camera.
            // frame!.sceneDepth.
            
        }
    }
}
