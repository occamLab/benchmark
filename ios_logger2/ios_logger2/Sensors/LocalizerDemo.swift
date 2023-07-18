import Foundation
import ARKit
import CoreMotion

/*
 *  Demo class for sending images to localizer server. Don't acually use this apart from testing
 */

class LocalizerDemo: Sensor, SensorProtocol {
    var sensorName: String = "_localizer_ignore"
    public var series = GyroData()
    
    
    func sendLocalizationReq(base64Jpg: String, modelName: String) {
        let parameters = [
            "base64Jpg": base64Jpg,
            "modelName": modelName
        ]
        let url = URL(string: "http://10.26.26.130:8000/localize")!
        let session = URLSession.shared
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.httpBody = try! JSONSerialization.data(withJSONObject: parameters, options: .prettyPrinted)
        request.addValue("application/json", forHTTPHeaderField: "Content-Type")
        request.addValue("application/json", forHTTPHeaderField: "Accept")
        
        //create dataTask using the session object to send data to the server
         let task = session.dataTask(with: request, completionHandler: { (data, response, error) in
             do {
                 guard error == nil else {
                     return
                 }
                 guard let data = data else {
                     return
                 }
                 guard let json = try JSONSerialization.jsonObject(with: data, options: .mutableContainers) as? [String: Any] else {
                     return
                 }
                 print(json)
             }
             catch {
                 print(error.localizedDescription)
             }
         })

         task.resume()
    }
    
    func collectData(motion: CMDeviceMotion?, frame: ARFrame?, arView: ARSCNView) {
        guard let frame = frame else {return}
        let imageBuffer: CVPixelBuffer = frame.capturedImage
        
        let ciImage: CIImage = CIImage(cvPixelBuffer: imageBuffer)
        let context = CIContext()
        let cgImageColor = context.createCGImage(ciImage, from: ciImage.extent)!
        let uiImageColor = UIImage(cgImage: cgImageColor, scale: 1, orientation: UIImage.Orientation.up)
        let jpgImage: Data = uiImageColor.jpegData(compressionQuality: 0.0)!
        let base64JpgImage: String = jpgImage.base64EncodedString()
        
        sendLocalizationReq(base64Jpg: base64JpgImage, modelName: "dup2.pt")
        
    }
}
