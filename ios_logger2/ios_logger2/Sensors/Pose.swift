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
class Pose: Sensor, SensorProtocol {
    var sensorName: String = "pose"
    public var series = PoseData()
    
    func collectData(motion: CMDeviceMotion?, frame: ARFrame?) {
        if(frame != nil) {
            let timestamp: Double = getUnixTimestamp(moment: frame!.timestamp)
            let transform = frame!.camera.transform
            let translation: [Float] = transform.translationValues()
            let quat_imag: [Float] = simd_quatf(transform).imagToArray()
            let quat_real: Float = simd_quatf(transform).real
            
            var measurement = PoseTimestamp()
            measurement.timestamp = timestamp
            measurement.poseTranslation = translation
            measurement.quatImag = quat_imag
            measurement.quatReal = quat_real
            
            if case currentPhase = Phase.mappingPhase {
                series.mappingPhase.measurements.append(measurement)
            }
            else {
                series.localizationPhase.measurements.append(measurement)
            }
        }
    }
}

extension simd_float4x4 {
    public func translationValues()->[Float] {
        return [self[3,0], self[3,1], self[3,2]]
    }
}

extension simd_quatf {
    public func imagToArray()->[Float] {
        return [self.imag[0], self.imag[1], self.imag[2]]
    }
}
