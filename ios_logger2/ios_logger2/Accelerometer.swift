//
//  Accelerometer.swift
//  ios_logger2
//

import Foundation


/*
 *  Implements data collection and encoding into a protobuf message for timeseries of accelerometer data
 */
class Accelerometer: Sensor {
    public var series = AccelerometerSeries()
    
    func collectData(motion: Motion) {
        if(motion.motionSensors.accelerometerData != nil) {
            let reading = motion.motionSensors.accelerometerData
            let timestamp: Double = reading!.timestamp.magnitude
            let acceleration_x: Double = reading!.acceleration.x
            let acceleration_y: Double = reading!.acceleration.y
            let acceleration_z: Double = reading!.acceleration.z
            
            
            var measurement = AccelerometerTimestamp()
            measurement.timestamp = timestamp
            measurement.xAcceleration = acceleration_x
            measurement.yAcceleration = acceleration_y
            measurement.zAcceleration = acceleration_z
            series.measurements.append(measurement)
            
        }
    }
}
