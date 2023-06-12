//
//  GoogleCloudAnchor.swift
//  ios_logger2
//
//  Created by Daniel Sudzilouski on 6/12/23.
//

import Foundation
import CoreMotion
import ARCore
import ARCoreGARSession

class GoogleCloudAnchor: Sensor {
    var sensorName: String = "google_cloud_anchor"
    var series: GoogleCloudAnchorMetadata = GoogleCloudAnchorMetadata()
    var garSession: GARSession?

     init() {
        var error: NSError?
        let configuration = GARSessionConfiguration()
        configuration.cloudAnchorMode = .enabled
        garSession = try? GARSession(apiKey: Secrets.garAPIKey, bundleIdentifier: nil)
        garSession?.setConfiguration(configuration, error: &error)
    }
    
    func collectData(motion: CMDeviceMotion?, frame: ARFrame?) {
        guard let frame = frame else {return}
        let _: GARFrame? = try? garSession?.update(frame)
    }
    
    func additionalUpload() async {
        let newAnchor = ARAnchor(transform: simd_float4x4())
        
        // there does not appear to be an async/await version of hostCloudAnchor so we wrap the callback into a promise using the withCheckedContinuation Swift API
        let anchorHostResult: (anchorName: String?, anchorState: GARCloudAnchorState)? = await withCheckedContinuation { continuation in
            do {
                try garSession?.hostCloudAnchor(newAnchor, ttlDays: 365, completionHandler: { (anchorName: String?, anchorState: GARCloudAnchorState) in
                    continuation.resume(returning: (anchorName, anchorState))
                })
            }
            catch  {
                print("[ERROR]: Failed to host cloud anchor", error)
                continuation.resume(returning: nil)
            }
        }
        guard let anchorHostResult = anchorHostResult else {return}
        print("[INFO]: Hosted cloud anchor with name]", anchorHostResult.anchorName!)
    }
    
}


