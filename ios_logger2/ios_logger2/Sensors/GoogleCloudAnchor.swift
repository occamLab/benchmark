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
import ARCoreCloudAnchors

class GoogleCloudAnchor: Sensor, SensorProtocol {
    var isResolvingAnchors = false
    var resolvedAnchors = false
    var sensorName: String = "google_cloud_anchor"
    var series: GoogleCloudAnchorData = GoogleCloudAnchorData()
    var garSession: GARSession?
    var resolvedAnchorIdentifier: UUID?

     override init() {
         var error: NSError?
         let configuration = GARSessionConfiguration()
         configuration.cloudAnchorMode = .enabled
         garSession = try? GARSession(apiKey: Secrets.garAPIKey, bundleIdentifier: nil)
         garSession?.setConfiguration(configuration, error: &error)
    }

    func collectData(motion: CMDeviceMotion?, frame: ARFrame?, arView: ARSCNView) {
        guard let frame = frame else {
            return
        }
        guard let garFrame = try? garSession?.update(frame) else {
            return
        }
        if self.resolvedAnchors == false {
            if isLocalizationPhase() {
                if self.isResolvingAnchors == false {
                    self.isResolvingAnchors = true
                    print("Localization phase")
                    do {
                        try garSession?.resolveCloudAnchor(series.mappingPhase.cloudAnchorMetadata.cloudAnchorName) { garAnchor, cloudState in
                            guard let garAnchor = garAnchor else {
                                print("Unable to resolve anchor")
                                return
                            }
                            print("Resolved anchor \(garAnchor.identifier)")
                            self.resolvedAnchorIdentifier = garAnchor.identifier
                            self.resolvedAnchors = true
                        }
                    } catch {
                        // print("error \(error.localizedDescription)")
                    }
                }
            }
        } else {
            if let cloudAnchor = garFrame.anchors.first(where: { $0.identifier == resolvedAnchorIdentifier }) {
                let timestamp: Double = getUnixTimestamp(moment: frame.timestamp)
                let anchor_translation: [Float] = cloudAnchor.transform.translationValuesCA()
                let anchor_rot_matrix: [Float] = cloudAnchor.transform.rotationMatrixCA()
                let arkit_transform = frame.camera.transform
                let arkit_translation: [Float] = arkit_transform.translationValues()
                let arkit_rot_matrix: [Float] = arkit_transform.rotationMatrix()
                var cloudAnchorMetadata = CloudAnchorMetadata()
                cloudAnchorMetadata.timestamp = timestamp
                cloudAnchorMetadata.cloudAnchorName = series.mappingPhase.cloudAnchorMetadata.cloudAnchorName
                cloudAnchorMetadata.resolvedCloudAnchorName = resolvedAnchorIdentifier!.uuidString
                cloudAnchorMetadata.anchorTranslation = anchor_translation
                cloudAnchorMetadata.anchorRotMatrix = anchor_rot_matrix
                cloudAnchorMetadata.arkitTranslation = arkit_translation
                cloudAnchorMetadata.arkitRotMatrix = arkit_rot_matrix
                series.localizationPhase.cloudAnchorMetadata.append(cloudAnchorMetadata)
            }
        }
    }
    
    func additionalUpload() async {
        if isMappingPhase() {
            let newAnchor = ARAnchor(transform: simd_float4x4())
            
            // there does not appear to be an async/await version of hostCloudAnchor so we wrap the callback into a promise using the withCheckedContinuation Swift API
            let anchorHostResult: (anchorName: String?, anchorState: GARCloudAnchorState)? = await withCheckedContinuation { continuation in
                guard let garSession = garSession else {
                    continuation.resume(returning: nil)
                    print("[ERROR]: Failed to host cloud anchor because garSession failed to initialize")
                    return
                }
                do {
                    // you can't set the ttlDays to more than one day when using just an apiKey aparrently
                    // there is a backend process that modified the ttlDays up to the max (365)
                    try garSession.hostCloudAnchor(newAnchor, ttlDays: 1, completionHandler: { (anchorName: String?, anchorState: GARCloudAnchorState) in
                        continuation.resume(returning: (anchorName, anchorState))
                    })
                }
                catch  {
                    print("[ERROR]: Failed to host cloud anchor: ", error)
                    continuation.resume(returning: nil)
                }
            }
            guard let anchorHostResult = anchorHostResult else {return}
            guard let anchorName = anchorHostResult.anchorName else {
                print("[ERROR]: Failed to host cloud anchor: ", anchorHostResult.anchorState)
                return
            }
            print("[INFO]: Hosted cloud anchor with name]", anchorName)
            series.mappingPhase.cloudAnchorMetadata.cloudAnchorName = anchorName
        }
    }
    
}
extension matrix_float4x4 {
    // Original matrix has form:
    //    [ a x x 0 ]
    //    [ x x x 0 ]
    //    [ x x x 0 ]
    //    [ x y z 1 ]
    // Change from matrix_float4x4 to arrays of floats
    
    public func translationValuesCA()->[Float] {
        return [self[3,0], self[3,1], self[3,2]]
    }
    public func rotationMatrixCA()->[Float] {
        return [
            self[0,0], self[0,1], self[0,2], self[0,3],
            self[1,0], self[1,1], self[1,2], self[1,3],
            self[2,0], self[2,1], self[2,2], self[2,3],
            self[3,0], self[3,1], self[3,2], self[3,3]
        ]
    }
}
