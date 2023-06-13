//
//  Motion.swift
//  ios_logger2
//
//  Created by Daniel Sudzilouski on 6/6/23.
//

import Foundation
import CoreMotion
import ARKit
import FirebaseStorage

class Motion: NSObject, ARSessionDelegate {
    public var motionSensors = CMMotionManager()
    public var arSession = ARSession()
    public var arConfiguration = ARWorldTrackingConfiguration()
    
    // all of our loggers go here
    private let sensors: [any Sensor] = [
        Accelerometer(),
        Video(),
        LiDAR(),
        Light(),
        Gyro(),
        PointCloud(),
        Pose(),
        Intrinsics(),
        GoogleCloudAnchor(),
    ]
    
    
    private func initMotionSensors() {
        // Set the update frequencies for gyro, accelerometer, and motion
        let imuUpdateFreqMillis: Double = 10
        let imuUpdateFreqSeconds: Double = imuUpdateFreqMillis /  1000
        motionSensors.gyroUpdateInterval = imuUpdateFreqSeconds
        motionSensors.accelerometerUpdateInterval = imuUpdateFreqSeconds
        motionSensors.deviceMotionUpdateInterval = imuUpdateFreqSeconds
        // start collecting data
        motionSensors.startDeviceMotionUpdates(to: OperationQueue(), withHandler: delegate_motion)
    }
    
    private func stopMotionSensors() {
        // stop collecting data
        motionSensors.stopDeviceMotionUpdates()
    }
    
    private func initArSession() {
        arSession.delegate = self
        arConfiguration.worldAlignment = ARConfiguration.WorldAlignment.gravity
        arConfiguration.isAutoFocusEnabled = true
        arSession.run(arConfiguration, options: [ARSession.RunOptions.resetTracking, ARSession.RunOptions.resetSceneReconstruction])
    }
    
    private func stopArSession() {
        arSession.pause()
    }
    
    // delegate ARFrame updates to video and other sensor loggers
    func session(_ session: ARSession, didUpdate frame: ARFrame) {
        for sensor in sensors {
            sensor.collectData(motion: nil, frame: frame)
        }
    }
    
    // delegate motion updates to accelerometer and other sensor loggers
    func delegate_motion(motion: CMDeviceMotion?, error: Error?) {
        for sensor in sensors {
            sensor.collectData(motion: motion, frame: nil)
        }
    }
    
    // finished collecting data, export the results
    func export() async {
        // cleanup
        stopArSession()
        stopMotionSensors()
        
        // queue data for upload
        for sensor in sensors {
            // some of our sensors like GoogleCloudAnchor/Video need to do async work before the protobuf data is availiable for packaging
            await sensor.additionalUpload()
            sensor.uploadProtobuf()
        }
        
        // batch upload the data
        UploadManager.shared.uploadLocalDataToCloud {(storageMetadata: StorageMetadata?, error: Error?)  in
            print("done uploading data")
        }
    }
    
    
    override init() {
        super.init()
        initMotionSensors()
        initArSession()
    }
}
