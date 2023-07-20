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
struct InteractiveLocalizerARViewRepresentable: UIViewRepresentable {
    let arDelegate: ARSCNView
    
    
    func makeUIView(context: Context) -> some UIView {
        return arDelegate
    }
    func updateUIView(_ uiView: UIViewType, context: Context) {
    }
}

class InteractiveLocalizer: NSObject, ARSessionDelegate {
    public static var arConfiguration = ARWorldTrackingConfiguration()
    var arSCNView: ARSCNView
    public var arView: ARSCNView = ARSCNView(frame: .zero)
    var localizerManager = LocalizerManager()
    
    
    public func initArSession() {
        print("init localizer")
        while let n = arView.scene.rootNode.childNodes.first { n.removeFromParentNode() }
        arView.session.delegate = self
        arView.debugOptions = [.showWorldOrigin]
        Motion.arConfiguration.worldAlignment = ARConfiguration.WorldAlignment.gravity
        Motion.arConfiguration.isAutoFocusEnabled = true
        Motion.arConfiguration.videoFormat = ARWorldTrackingConfiguration.recommendedVideoFormatForHighResolutionFrameCapturing!
        Motion.arConfiguration.planeDetection = [.horizontal, .vertical]
        arView.session.pause()
        arView.session.run(Motion.arConfiguration, options: [
            ARSession.RunOptions.resetTracking,
            ARSession.RunOptions.resetSceneReconstruction,
            ARSession.RunOptions.removeExistingAnchors,
        ])
    }
    
    public func stop() {
        arView.session.pause()
    }
    
    
    func session(_ session: ARSession, didUpdate frame: ARFrame) {
        localizerManager.sendLocaliztionRequest(frame: frame, modelName: "dup2.pt")
    }
    
    
    init(_arSCNView: ARSCNView) {
        arSCNView = _arSCNView
        super.init()
    }
    
}
