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
    var selectedAnchor: String? = nil
    
    
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
    
    func visualizeTransformAxis(_ transformName: String, _ visTransform: simd_float4x4) {
        let nodeName: String = "Tag_" + transformName
        var tranformNoTranslation = visTransform
        tranformNoTranslation.columns.3.x = 0
        tranformNoTranslation.columns.3.y = 0
        tranformNoTranslation.columns.3.z = 0
        
        if let existingNode = arView.scene.rootNode.childNode(withName: nodeName, recursively: false)  {
            existingNode.simdTransform = tranformNoTranslation
        }
        else {
            let visNode = SCNNode()
            visNode.simdTransform = tranformNoTranslation
            visNode.geometry = SCNBox(width: 0.15875, height: 0.15875, length: 0.05, chamferRadius: 0)
            visNode.name = nodeName
            visNode.geometry?.firstMaterial?.diffuse.contents = UIColor.cyan
            
            /// Add axes to the tag to aid in the visualization
            let xAxis = SCNNode(geometry: SCNBox(width: 1.0, height: 0.05, length: 0.05, chamferRadius: 0))
            xAxis.position = SCNVector3.init(0.75, 0, 0)
            xAxis.geometry?.firstMaterial?.diffuse.contents = UIColor.red
            let yAxis = SCNNode(geometry: SCNBox(width: 0.05, height: 1.0, length: 0.05, chamferRadius: 0))
            yAxis.position = SCNVector3.init(0, 0.75, 0)
            yAxis.geometry?.firstMaterial?.diffuse.contents = UIColor.green
            let zAxis = SCNNode(geometry: SCNBox(width: 0.05, height: 0.05, length: 1.0, chamferRadius: 0))
            zAxis.position = SCNVector3.init(0, 0, 0.75)
            zAxis.geometry?.firstMaterial?.diffuse.contents = UIColor.blue
            visNode.addChildNode(xAxis)
            visNode.addChildNode(yAxis)
            visNode.addChildNode(zAxis)
            arView.scene.rootNode.addChildNode(visNode)
        }
    }
    
    func renderDemo(renderLocationInAnchorFrame: simd_float4x4, cameraInAnchorWorldFrame: simd_float4x4, cameraInCurrentWorldFrame: simd_float4x4, arView: ARSCNView) {
        
        let device_opencv_to_arkit_mapping = cameraInAnchorWorldFrame
        let device_arkit_to_device_opencv = simd_float4x4(diagonal: simd_float4(1, -1, -1, 1))
        let arlocalization_to_device_arkit = cameraInCurrentWorldFrame.inverse
        
        let arlocalization_to_ar_mapping = device_opencv_to_arkit_mapping * device_arkit_to_device_opencv * arlocalization_to_device_arkit
        
        let renderLocationInCurrentFrame = arlocalization_to_ar_mapping

           
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
        visualizeTransformAxis("origin", matrix_identity_float4x4)
        guard let selectedAnchor = selectedAnchor else {return}
        localizerManager.sendLocaliztionRequest(frame: frame, modelName: selectedAnchor + ".pt", resolveCallBack: {(resolvedTransform: simd_float4x4) in
            self.renderDemo(renderLocationInAnchorFrame: matrix_identity_float4x4, cameraInAnchorWorldFrame: resolvedTransform, cameraInCurrentWorldFrame: frame.camera.transform, arView: self.arView)
          })
    }
    
    
    init(_arSCNView: ARSCNView) {
        arSCNView = _arSCNView
        super.init()
    }
    
}
