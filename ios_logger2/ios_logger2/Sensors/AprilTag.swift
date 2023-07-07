//
//  cv_testing.swift
//  STEP Navigation
//
//  Created by Zoe McGinnis on 6/13/23.
//

import Foundation
import opencv2
import VideoToolbox
import ARKit
import CoreMotion

extension UIImage {
    public convenience init?(pixelBuffer: CVPixelBuffer) {
        var cgImage: CGImage?
        VTCreateCGImageFromCVPixelBuffer(pixelBuffer, options: nil, imageOut: &cgImage)

        guard let cgImage = cgImage else {
            return nil
        }
        self.init(cgImage: cgImage)
    }
}

/// A class that uses OpenCV's support for Aruco detection to detect April tags
class AprilTag: Sensor, SensorProtocol {
    private var isDetectingAprilTags = false
    var sensorName: String = "april_tag"
    public var series = AprilTagData()
    
    /// The underlying OpenCV detector
    let detector: ArucoDetector

    /// The init method creates the detector with the April tag corner refinement method and the 36h11 tag family
    override init() {
        let parameters = DetectorParameters()
        parameters.cornerRefinementMethod = .CORNER_REFINE_APRILTAG
        let refineParams = RefineParameters()
        detector = ArucoDetector(dictionary: parameters, refineParams: refineParams)
        // April tag 36h11
        detector.setDictionary(dictionary: Objdetect.getPredefinedDictionary(dict: 20))
    }
    
    // Starts up whenever last April tag finished being detected
    public func getAprilTags(frame: ARFrame, arView: ARSCNView) {
        isDetectingAprilTags = true
        DispatchQueue.global(qos: .userInteractive).async {
            let phoneToWorld = frame.camera.transform
            let K = frame.camera.intrinsics
            
            do {
                // Show source image
                if let image = UIImage(pixelBuffer: frame.capturedImage) {
                    let src = Mat(uiImage: image)
                    let gray = Mat()
                    Imgproc.cvtColor(src: src, dst: gray, code: .COLOR_BGRA2GRAY)
                    let corners = NSMutableArray()
                    let ids: Mat = Mat()
                    
                    // Add camera intrinsics to matrix
                    let dist = MatOfDouble()
                    let intrinsics = Mat.eye(rows: 3, cols: 3, type: CvType.CV_64F)
                    try intrinsics.put(row: 0, col: 0, data: [Double(K[0,0])])
                    try intrinsics.put(row: 1, col: 1, data: [Double(K[1,1])])
                    try intrinsics.put(row: 0, col: 2, data: [Double(K[2,0])])
                    try intrinsics.put(row: 1, col: 2, data: [Double(K[2,1])])
                    
                    // Get April tag's ID (the one we're using is 305)
                    let id = 0
                    self.detector.detectMarkers(image: gray, corners: corners, ids: ids)
                    for row in 0..<ids.rows() {
                        for col in 0..<ids.cols() {
                            // Make this store id flatly
                            let id = ids.get(row: row, col: col)[0]
                            print("[INFO]: April tag ID: \(id)")
                        }
                    }
                    
                    // Set boolean back to false when not detecting April tags to trigger next detection
                    guard ids.rows() * ids.cols() != 0 else {
                        self.isDetectingAprilTags = false
                        return
                    }
                    // Set width to half the length of the black and white squares of April tags
                    let halfMarkerWidth: Float = 0.15875/2
                    for c in corners {
                        guard let c = c as? Mat else {
                            continue
                        }
                        
                        // Create empty rvec and tvec arrays as CV type Mat
                        let rvec = Mat()
                        let tvec = Mat()
                        
                        // Create empty 3D and 2D point arrays as CV type MatOfPoints3f and MatOfPoints2f, respectively
                        let points3d = MatOfPoint3f()
                        let points2d = MatOfPoint2f()
                        points3d.alloc(4)
                        points2d.alloc(4)
                        
                        // Populate 3D points array with corner data with the center of April tag as 0,0
                        try points3d.put(row: 0, col: 0, data: [-halfMarkerWidth, halfMarkerWidth, 0.0]) // was row 2
                        try points3d.put(row: 1, col: 0, data: [halfMarkerWidth, halfMarkerWidth, 0.0]) // was row 3
                        try points3d.put(row: 2, col: 0, data: [halfMarkerWidth, -halfMarkerWidth, 0.0]) // was row 0
                        try points3d.put(row: 3, col: 0, data: [-halfMarkerWidth, -halfMarkerWidth, 0.0]) // was row 1
                        
                        // Create 2D points with center of April tag as 0,0
                        try points2d.put(row: 0, col: 0, data: [c.get(row: 0, col: 2)[0], c.get(row: 0, col: 2)[1]]) // was row 2
                        try points2d.put(row: 1, col: 0, data: [c.get(row: 0, col: 3)[0], c.get(row: 0, col: 3)[1]]) // was row 3
                        try points2d.put(row: 2, col: 0, data: [c.get(row: 0, col: 0)[0], c.get(row: 0, col: 0)[1]]) // was row 0
                        try points2d.put(row: 3, col: 0, data: [c.get(row: 0, col: 1)[0], c.get(row: 0, col: 1)[1]]) // was row 1
                        
                        // Calculate pose, output the rotation vector rvec and translation vector tvec
                        Calib3d.solvePnP(objectPoints: points3d, imagePoints: points2d, cameraMatrix: intrinsics, distCoeffs: dist, rvec: rvec, tvec: tvec, useExtrinsicGuess: false, flags: 7)
                        
                        // Convert to simd_float3 so it's usable
                        let rvecSimd = simd_float3(x: Float(rvec.get(row: 0, col: 0)[0]),
                                                   y: Float(rvec.get(row: 1, col: 0)[0]),
                                                   z: Float(rvec.get(row: 2, col: 0)[0]))
                        let orientation = simd_quatf(angle: simd_length(rvecSimd), axis: simd_normalize(rvecSimd))
                        let position = simd_float3(x: Float(tvec.get(row: 0, col: 0)[0]),
                                                   y: Float(tvec.get(row: 1, col: 0)[0]),
                                                   z: Float(tvec.get(row: 2, col: 0)[0]))
                        // Orientation
                        var tagToImage = simd_float4x4(orientation)
                        // Position + orientation
                        tagToImage.columns.3 = simd_float4(position, 1)
                        let imageToPhone = simd_float4x4(diagonal: [1.0, -1.0, -1.0, 1.0])
                        // Position + orientation
                        let tagToPhone = imageToPhone * tagToImage
                        // Position + orientation
                        let tagToWorld = phoneToWorld * tagToPhone
                        
                        // Use lidar to align with planar geometry
                        guard let tagToWorld = self.raycastTag(tagPoseWorld: tagToWorld, cameraPoseWorld: phoneToWorld, arSession: arView.session) else {
                            self.isDetectingAprilTags = false
                            return
                        }
                        
                        // Show cyan square over April tag
                        let tagNode: SCNNode
                        // Update existing April tag's position
                        if let existingTagNode = arView.scene.rootNode.childNode(withName: "Tag_\(String(id))", recursively: false)  {
                            tagNode = existingTagNode
                            tagNode.simdTransform = tagToWorld
                            // Initialize April tag position + cyan box
                        } else {
                            tagNode = SCNNode()
                            tagNode.simdTransform = tagToWorld
                            tagNode.geometry = SCNBox(width: 0.15875, height: 0.15875, length: 0.05, chamferRadius: 0)
                            tagNode.name = "Tag_\(String(id))"
                            tagNode.geometry?.firstMaterial?.diffuse.contents = UIColor.cyan
                            
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
                            tagNode.addChildNode(xAxis)
                            tagNode.addChildNode(yAxis)
                            tagNode.addChildNode(zAxis)
                            arView.scene.rootNode.addChildNode(tagNode)
                        }
                        self.saveAprilTag(frame: frame, worldAprilTag: tagToWorld)
                    }
                }
            } catch {
                // For debugging purposes
                print("catch")
            }
            self.isDetectingAprilTags = false
        }
    }
    
    func saveAprilTag(frame: ARFrame, worldAprilTag: simd_float4x4) {
        var measurement = AprilTagTimestamp()
        measurement.timestamp = self.getUnixTimestamp(moment: frame.timestamp)
        measurement.tagCenterPose = worldAprilTag.rotationMatrix()
        if case currentPhase = Phase.mappingPhase {
            series.mappingPhase.measurements.append(measurement)
        }
        else {
            series.localizationPhase.measurements.append(measurement)
        }
    }
    
    
    /// Raycasts from camera to tag and places tag on the nearest mesh if the device supports LiDAR
    /// originally implemented in https://github.com/occamLab/InvisibleMap/blob/bfa5e7c1a51328702a8a117a74fa87ed3488174f/InvisibleMapCreator2/Views/ARView.swift#L180
    func raycastTag(tagPoseWorld: simd_float4x4, cameraPoseWorld: simd_float4x4, arSession: ARSession) -> simd_float4x4? {
        let tagPosWorldTranslation = simd_float3(tagPoseWorld.columns.3.x, tagPoseWorld.columns.3.y, tagPoseWorld.columns.3.z)
        let cameraPosTranslation = simd_float3(cameraPoseWorld.columns.3.x, cameraPoseWorld.columns.3.y, cameraPoseWorld.columns.3.z)
        
        let raycastQuery = ARRaycastQuery(origin: cameraPosTranslation, direction: tagPosWorldTranslation - cameraPosTranslation, allowing: .existingPlaneGeometry, alignment: .any)
        let raycastResult = arSession.raycast(raycastQuery)
        
        if raycastResult.count == 0 {
            print("[WARNING]: Failing to find raycast april tag")
            return nil
        } else {
            // for some reason the raycast result re-order the axis so we move the z-axis back to be out of the april tag for visualization purposes only basically
            let meshTransform = raycastResult[0].worldTransform
            let raycastTagTransform: simd_float4x4 = meshTransform * float4x4(simd_quatf(angle: -.pi / 2, axis: SIMD3<Float>(1, 0, 0)))
            
            print("[INFO]: Raycasted april tag result: ", raycastTagTransform)
            
            return raycastTagTransform
        }
    }
    
    /// Detect the markers in the specified image
    /// - Parameter image: the image taken from, e.g., an `ARFrame`
    func collectData(motion: CMDeviceMotion?, frame: ARFrame?, arView: ARSCNView) {
        if(frame != nil) {
            if !isDetectingAprilTags {
                getAprilTags(frame: frame!, arView: arView)
            }
        }
    }
}
