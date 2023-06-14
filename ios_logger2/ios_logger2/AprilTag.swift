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

extension UIImage {
    public convenience init?(pixelBuffer: CVPixelBuffer) {
        var cgImage: CGImage?
        Motion.shared.arView?.debugOptions = [.showWorldOrigin]
        VTCreateCGImageFromCVPixelBuffer(pixelBuffer, options: nil, imageOut: &cgImage)

        guard let cgImage = cgImage else {
            return nil
        }
        self.init(cgImage: cgImage)
    }
}

/// A class that uses OpenCV's support for Aruco detection to detect April tags
class AprilTagDetector {
    /// The underlying OpenCV detector
    let detector: ArucoDetector

    /// The init method creates the detector with the April tag corner refinement method and the 36h11 tag family
    init() {
        let parameters = DetectorParameters()
        parameters.cornerRefinementMethod = .CORNER_REFINE_APRILTAG
        let refineParams = RefineParameters()
        detector = ArucoDetector(dictionary: parameters, refineParams: refineParams)
        // April tag 36h11
        detector.setDictionary(dictionary: Objdetect.getPredefinedDictionary(dict: 20))
    }
    
    /// Detect the markers in the specified image
    /// - Parameter image: the image taken from, e.g., an `ARFrame`
    func detectMarkers(inImage image: CVPixelBuffer, phoneToWorld: simd_float4x4, K: simd_float3x3) {
        do {
            // Show source image
            if let image = UIImage(pixelBuffer: image) {
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
                
                // TODO: Add ID to April tag AR
                var id = 0
                self.detector.detectMarkers(image: gray, corners: corners, ids: ids)
                for row in 0..<ids.rows() {
                    for col in 0..<ids.cols() {
                        // Make this store id flatly
                        let id = ids.get(row: row, col: col)[0]
                        print("ids", ids.get(row: row, col: col))
                    }
                }

                guard ids.rows() * ids.cols() != 0 else {
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
                    
                    // Print translation values for debugging
                    print("tvec \(tvec.get(row: 0, col: 0)), \(tvec.get(row: 1, col: 0)), \(tvec.get(row: 2, col: 0))")
                    print("rvec \(rvec.get(row:0, col: 0)), \(rvec.get(row: 1, col: 0)), \(rvec.get(row: 2, col: 0))")
                    
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
                    
                    // Show cyan square over April tag
                    let tagNode: SCNNode
                    // Update existing April tag's position
                    if let existingTagNode = Motion.shared.arView?.scene.rootNode.childNode(withName: "Tag_\(String(id))", recursively: false)  {
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
                        Motion.shared.arView?.scene.rootNode.addChildNode(tagNode)
                    }
                }
            }
        } catch {
            // For debugging purposes
            print("catch")
        }
    }
}
