//
//  light.swift
//  ios_logger2
//
//  Created by Zoe McGinnis on 6/9/23.
//

import Foundation

import ARKit
import CoreMotion

/*
 *  Implements data collection and encoding into a protobuf message for timeseries of ambient light data
 */
class Light: Sensor, SensorProtocol {
    var sensorName: String = "ambient_light"
    public var series = LightData()
    
    func collectData(motion: CMDeviceMotion?, frame: ARFrame?, arView: ARSCNView) {
        if(frame != nil) {
            let lightEstimate = frame!.lightEstimate
            let timestamp: Double = getUnixTimestamp(moment: frame!.timestamp)
            let light_intensity: Double = lightEstimate!.ambientIntensity
            
            var measurement = LightTimestamp()
            measurement.timestamp = timestamp
            measurement.lightIntensity = light_intensity
            
            if case currentPhase = Phase.mappingPhase {
                series.mappingPhase.measurements.append(measurement)
            }
            else {
                series.localizationPhase.measurements.append(measurement)
            }
        }
    }
}
