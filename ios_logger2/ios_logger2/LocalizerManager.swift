import Foundation
import ARCore

/*
 *  Client API for sending images to localizer server.
 */

class LocalizerManager {
    var server_url: URL = URL(string: "http://10.26.26.130:8000/localize")!
    var pendingReq: Bool = false
    var inlierThreshold: Int = 200
    
    /* Retrieves image from ARFrame as a base64 jpg string */
    private func getBase64Jpg(frame: ARFrame) -> String {
        let imageBuffer: CVPixelBuffer = frame.capturedImage
        let ciImage: CIImage = CIImage(cvPixelBuffer: imageBuffer)
        let context = CIContext()
        let cgImageColor = context.createCGImage(ciImage, from: ciImage.extent)!
        let uiImageColor = UIImage(cgImage: cgImageColor, scale: 1, orientation: UIImage.Orientation.up)
        let jpgImage: Data = uiImageColor.jpegData(compressionQuality: 0.0)!
        let base64JpgImage: String = jpgImage.base64EncodedString()
        
        return base64JpgImage
    }
    
    /* Sends a localization request to the server if one is not already pending */
    public func sendLocaliztionRequest(frame: ARFrame, modelName: String, resolveCallBack: @escaping ((simd_float4x4) -> Void)) {
        if(pendingReq) {
            return
        }
        pendingReq = true
        arkitPose = frame.camera.transform.rotationMatrix()
            
        // req params that we send to the server
        let parameters: [String : Any] = [
            "base64Jpg": getBase64Jpg(frame: frame),
            "modelName": modelName,
            "focal_length": frame.camera.intrinsics[0, 0],
            "optical_x": frame.camera.intrinsics[2, 0],
            "optical_y": frame.camera.intrinsics[2, 1],
            "arkit_pose": arkitPose
        ]
        
        // set req headers
        let session = URLSession.shared
        var request = URLRequest(url: server_url)
        request.httpMethod = "POST"
        request.httpBody = try! JSONSerialization.data(withJSONObject: parameters, options: .prettyPrinted)
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.addValue("application/json", forHTTPHeaderField: "Accept")
        
        let task = session.dataTask(with: request, completionHandler: { (data, response, error) in
            self.pendingReq = false
            guard error == nil else {return}
            guard let data = data else {return}
            let json = try! JSONSerialization.jsonObject(with: data) as? [String: Any]
            if(json?["status"] as! String == "ok") {
                let inlierCount = (json?["inlier_count"] as! NSNumber).intValue
                let poseList: [Float] = (json?["pose"] as! [NSNumber]).map { $0.floatValue }
                let poseTransform: simd_float4x4 = poseList.row_list_to_simd_float4x4()
                //print(inlierCount)
                if(inlierCount >= self.inlierThreshold) {
                    resolveCallBack(poseTransform)
                }
            }
        })
        task.resume()
    }
}
