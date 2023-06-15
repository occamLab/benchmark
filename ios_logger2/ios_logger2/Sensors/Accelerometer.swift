//
//  Accelerometer.swift
//  ios_logger2
//

import Foundation
import ARKit
import CoreMotion
import SwiftProtobuf

/*
 *  Implements data collection and encoding into a protobuf message for timeseries of accelerometer data
 */
class Accelerometer: Sensor, SensorProtocol {
    var sensorName: String = "accelerometer"
    var series: AccelerometerData = AccelerometerData()
    
    func collectData(motion: CMDeviceMotion?, frame: ARFrame?) {
        if(motion != nil) {
            let timestamp: Double = getUnixTimestamp(moment: motion!.timestamp)
            let acceleration_x: Double = motion!.userAcceleration.x
            let acceleration_y: Double =  motion!.userAcceleration.y
            let acceleration_z: Double =  motion!.userAcceleration.z
            
            
            var measurement = AccelerometerTimestamp()
            measurement.timestamp = timestamp
            measurement.xAcceleration = acceleration_x
            measurement.yAcceleration = acceleration_y
            measurement.zAcceleration = acceleration_z

            if case currentPhase = Phase.mappingPhase {
                series.mappingPhase.measurements.append(measurement)
            }
            else {
                series.localizationPhase.measurements.append(measurement)
            }
        }
    }
}
