//
//  Motion.swift
//  ios_logger2
//
//  Created by Daniel Sudzilouski on 6/6/23.
//

import Foundation
import CoreMotion


class Motion {
    public var motionSensors = CMMotionManager()
    
    
    private func initMotionSensors() {
        // Set the update frequencies for gyro, accelerometer, and motion
        let imuUpdateFreqMillis: Double = 10
        let imuUpdateFreqSeconds: Double = imuUpdateFreqMillis /  1000
        motionSensors.gyroUpdateInterval = imuUpdateFreqSeconds
        motionSensors.accelerometerUpdateInterval = imuUpdateFreqSeconds
        motionSensors.deviceMotionUpdateInterval = imuUpdateFreqSeconds
        
        // start collecting data
        motionSensors.startGyroUpdates()
        motionSensors.startAccelerometerUpdates()
        motionSensors.startDeviceMotionUpdates()
    }
    
    private func stopMotionSensors() {
        // stop collecting data
        motionSensors.stopGyroUpdates()
        motionSensors.stopAccelerometerUpdates()
        motionSensors.stopDeviceMotionUpdates()
    }
    
    private init() {
        initMotionSensors()
    }
}
