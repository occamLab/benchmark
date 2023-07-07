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

/*
 * Lifts the arView out of Motion and wraps it into an UIViewRepresentable so that we can render it on screen
 */
struct ARViewRepresentable: UIViewRepresentable {
    let arDelegate: Motion
    
    func makeUIView(context: Context) -> some UIView {
        return arDelegate.arView
    }
    func updateUIView(_ uiView: UIViewType, context: Context) {
    }
}


class Motion: NSObject, ARSessionDelegate {
    
    public static var arConfiguration = ARWorldTrackingConfiguration()
    public var motionSensors = CMMotionManager()
    public var arView: ARSCNView = ARSCNView(frame: .zero)
    public var motionUpdateQueue = OperationQueue()
    

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
    
    
    public func initMotionSensors() {
        // Set the update frequencies for gyro, accelerometer, and motion
        let imuUpdateFreqMillis: Double = 10
        let imuUpdateFreqSeconds: Double = imuUpdateFreqMillis /  1000
        motionSensors.gyroUpdateInterval = imuUpdateFreqSeconds
        motionSensors.accelerometerUpdateInterval = imuUpdateFreqSeconds
        motionSensors.deviceMotionUpdateInterval = imuUpdateFreqSeconds
        // start collecting data
        // NOTE: maxConcurrentOperationCount MUST be 1 because appending to a protobuf array is NOT thread safe
        motionUpdateQueue.maxConcurrentOperationCount = 1
        motionSensors.startDeviceMotionUpdates(to: motionUpdateQueue, withHandler: delegate_motion)
    }
    
    public func stopDataCollection() {
        // stop collecting data
        motionSensors.stopDeviceMotionUpdates()
        arView.session.pause()

    }
    
    public func initArSession() {
        while let n = arView.scene.rootNode.childNodes.first { n.removeFromParentNode() }
        arView.session.delegate = self
        arView.debugOptions = [.showWorldOrigin]
        Motion.arConfiguration.worldAlignment = ARConfiguration.WorldAlignment.gravity
        Motion.arConfiguration.isAutoFocusEnabled = true
        Motion.arConfiguration.videoFormat = ARWorldTrackingConfiguration.recommendedVideoFormatForHighResolutionFrameCapturing!
        Motion.arConfiguration.planeDetection = [.horizontal, .vertical]
        arView.session.run(Motion.arConfiguration, options: [
            ARSession.RunOptions.resetTracking,
            ARSession.RunOptions.resetSceneReconstruction,
            ARSession.RunOptions.removeExistingAnchors,
        ])
    }
    
    
    // delegate ARFrame updates to video and other sensor loggers
    func session(_ session: ARSession, didUpdate frame: ARFrame) {
        for sensor in sensors {
            sensor.collectData(motion: nil, frame: frame, arView: arView)
        }
    }
    
    // delegate motion updates to accelerometer and other sensor loggers
    func delegate_motion(motion: CMDeviceMotion?, error: Error?) {
        for sensor in sensors {
            sensor.collectData(motion: motion, frame: nil, arView: arView)
        }
    }
    
    // finished collecting mapping data, swith to collecting localization data
    func switchToLocalization() async {
        // stop feeds of data, I'm assuming this happens instantly right now
        stopDataCollection()
        
        // queue data for upload
        for sensor in sensors {
            // some of our sensors like GoogleCloudAnchor/Video need to do async work before the protobuf data is availiable for packaging
            await sensor.additionalUpload()
            sensor.currentPhase = Phase.localizationPhase
            // some sensors such as video may need to hook on this action to reset state
            sensor.switchToLocalization()
        }
    }
    
    func finalExport() async {
        stopDataCollection()
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
    
    
    override init() {
        super.init()
        initMotionSensors()
        initArSession()
    }
}
