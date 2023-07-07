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
    
    func collectData(motion: CMDeviceMotion?, frame: ARFrame?, arView: ARSCNView) {
        if(frame != nil) {
            let timestamp: Double = getUnixTimestamp(moment: frame!.timestamp)
            let transform = frame!.camera.transform
            let cameraConventions = transform * simd_float4x4(diagonal: simd_float4(1, -1, -1, 1))
            let translation: [Float] = cameraConventions.translationValues()
            let rot_matrix: [Float] = cameraConventions.rotationMatrix()
            let quat_imag: [Float] = simd_quatf(cameraConventions).imagToArray()
            let quat_real: Float = simd_quatf(cameraConventions).real
            
            var measurement = PoseTimestamp()
            measurement.timestamp = timestamp
            measurement.poseTranslation = translation
            measurement.rotMatrix = rot_matrix
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
    public func rotationMatrix()->[Float] {
        return [self[0,0], self[0,1], self[0,2], self[0,3], self[1,0], self[1,1], self[1,2], self[1,3], self[2,0], self[2,1], self[2,2], self[2,3], self[3,0], self[3,1], self[3,2], self[3,3]]
    }
}

extension simd_quatf {
    public func imagToArray()->[Float] {
        return [self.imag[0], self.imag[1], self.imag[2]]
    }
}
