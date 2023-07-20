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
    var resolvedTranslationValues: [Float] = [0,0,0]
    
    
    public func initArSession() {
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
    
    func renderDemo(renderLocationInAnchorFrame: simd_float4x4, cameraInAnchorWorldFrame: simd_float4x4, cameraInCurrentWorldFrame: simd_float4x4, arView: ARSCNView) {
           let renderLocationInCurrentFrame = cameraInCurrentWorldFrame * (renderLocationInAnchorFrame * cameraInAnchorWorldFrame.inverse)
            resolvedTranslationValues = renderLocationInCurrentFrame.translationValues()

           
           let anchorName = "demo_render_anchor"
           if let existingTagNode = arView.scene.rootNode.childNode(withName: anchorName, recursively: false)  {
               existingTagNode.simdTransform = renderLocationInCurrentFrame
           } else {
               let anchorNode = SCNNode()
               anchorNode.simdTransform = renderLocationInCurrentFrame
               anchorNode.geometry = SCNSphere(radius: 0.2)
               anchorNode.name = anchorName
               anchorNode.geometry?.firstMaterial?.diffuse.contents = UIColor.cyan
               arView.scene.rootNode.addChildNode(anchorNode)
           }
       }
    
    
    func session(_ session: ARSession, didUpdate frame: ARFrame) {
        localizerManager.sendLocaliztionRequest(frame: frame, modelName: "dup2.pt", resolveCallBack: {(resolvedTransform: simd_float4x4) in
            self.renderDemo(renderLocationInAnchorFrame: matrix_identity_float4x4, cameraInAnchorWorldFrame: resolvedTransform, cameraInCurrentWorldFrame: frame.camera.transform, arView: self.arView)
          })
    }
    
    
    init(_arSCNView: ARSCNView) {
        arSCNView = _arSCNView
        super.init()
    }
    
}
