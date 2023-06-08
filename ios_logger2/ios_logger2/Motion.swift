//
//  Motion.swift
//  ios_logger2
//
//  Created by Daniel Sudzilouski on 6/6/23.
//

import Foundation
import CoreMotion
import ARKit


class Motion: NSObject, ARSessionDelegate {
    public var motionSensors = CMMotionManager()
    public var arSession = ARSession()
    public var arConfiguration = ARWorldTrackingConfiguration()
    
    // all of our loggers go here
    private let accelerometerLogger = Accelerometer()
    private let videoLogger = Video()
    
    
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
        
        motionSensors.startDeviceMotionUpdates(to: OperationQueue(), withHandler: delegate_motion)
    }
    
    private func stopMotionSensors() {
        // stop collecting data
        motionSensors.stopGyroUpdates()
        motionSensors.stopAccelerometerUpdates()
        motionSensors.stopDeviceMotionUpdates()
    }
    
    private func initArSession() {
        arSession.delegate = self
        arConfiguration.worldAlignment = ARConfiguration.WorldAlignment.gravity
        arConfiguration.isAutoFocusEnabled = true
        arSession.run(arConfiguration)
    }
    
    // delegate ARFrame updates to video and other sensor loggers
    func session(_ session: ARSession, didUpdate frame: ARFrame) {
        videoLogger.collectData(motion: nil, frame: frame)
    }
    
    // delegate motion updates to accelerometer and other sensor loggers
    func delegate_motion(motion: CMDeviceMotion?, error: Error?) {
        accelerometerLogger.collectData(motion: motion, frame: nil)
    }
    
    
    override init() {
        super.init()
        initMotionSensors()
        initArSession()
    }
}
