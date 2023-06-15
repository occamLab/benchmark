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
import SwiftUI

struct ARViewRepresentable: UIViewRepresentable {
    let arDelegate: Motion
    
    func makeUIView(context: Context) -> some UIView {
        let arView = ARSCNView(frame: .zero)
        arDelegate.setARView(arView)
        return arView
    }
    
    func updateUIView(_ uiView: UIViewType, context: Context) {
        
    }
}

class Motion: NSObject, ARSessionDelegate {
    public static var shared = Motion()
    public var motionSensors = CMMotionManager()
    public var arView: ARSCNView?
    public var arConfiguration = ARWorldTrackingConfiguration()
    
    func setARView(_ arView: ARSCNView) {
        self.arView = arView
        initArSession()
    }
    
    // all of our loggers go here
    private let sensors: [any SensorProtocol & Sensor] = [
        Accelerometer(),
        Video(),
        LiDAR(),
        Light(),
        Gyro(),
        PointCloud(),
        Pose(),
        Intrinsics(),
        GoogleCloudAnchor(),
        AprilTag()
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
        arView?.session.delegate = self
        arView?.debugOptions = [.showWorldOrigin]
        arConfiguration.worldAlignment = ARConfiguration.WorldAlignment.gravity
        arConfiguration.isAutoFocusEnabled = true
        arView?.session.run(arConfiguration, options: [ARSession.RunOptions.resetTracking, ARSession.RunOptions.resetSceneReconstruction])
    }
    
    private func stopArSession() {
        arView?.session.pause()
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
    
    // finished collecting mapping data, swith to collecting localization data
    func switchToLocalization() async {
        // stop feeds of data, I'm assuming this happens instantly right now
        stopArSession()
        stopMotionSensors()
        
        // queue data for upload
        for sensor in sensors {
            // some of our sensors like GoogleCloudAnchor/Video need to do async work before the protobuf data is availiable for packaging
            await sensor.additionalUpload()
            sensor.currentPhase = Phase.localizationPhase
            // some sensors such as video may need to hook on this action to reset state
            

        }
        

    }
    
    func finalExport() async {
        for sensor in sensors {
            // some of our sensors like GoogleCloudAnchor/Video need to do async work before the protobuf data is availiable for packaging
            await sensor.additionalUpload()
            // protobufs are now finalized and can be queued for uploading
            sensor.uploadProtobuf()
        }
        // batch upload the data
        UploadManager.shared.uploadLocalDataToCloud {(storageMetadata: StorageMetadata?, error: Error?)  in
            print("done uploading data")
        }
    }
    
    
    
    private override init() {
        super.init()
        initMotionSensors()
        initArSession()
    }
}
