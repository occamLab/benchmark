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
    
    func collectData(motion: CMDeviceMotion?, frame: ARFrame?) {
        print("0")
        return
        guard let frame = frame else {
            return
        }
        print("1")
        guard let garFrame = try? garSession?.update(frame) else {
            return
        }
        print("2")
        // Make sure the rest happens only if we're in the localization phase
        guard isLocalizationPhase() else {
            return
        }
        print("3")
        // Make sure we are only trying to resolve one anchor at a time
        guard self.isResolvingAnchors else {
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
                    self.isResolvingAnchors = false
                }
            } catch {
                // print("error \(error.localizedDescription)")
            }
            sendLocalizationData(frame: frame, cloudAnchors: garFrame)
            return
        }
    }
    
    func sendLocalizationData(frame: ARFrame, cloudAnchors: GARFrame) {
        guard let cloudAnchor = cloudAnchors.updatedAnchors.first(where: { $0.identifier == resolvedAnchorIdentifier }) else {
            return
        }
        let timestamp: Double = getUnixTimestamp(moment: frame.timestamp)
        let anchor_translation: [Float] = cloudAnchor.transform.translationValues()
        let anchor_rot_matrix: [Float] = cloudAnchor.transform.rotationMatrix()
        let arkit_transform = frame.camera.transform
        let arkit_translation: [Float] = arkit_transform.translationValues()
        let arkit_rot_matrix: [Float] = arkit_transform.rotationMatrix()
        print("updated position! \(arkit_translation)")
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
//extension matrix_float4x4 {
//    // Original matrix has form:
//    //    [ a x x 0 ]
//    //    [ x x x 0 ]
//    //    [ x x x 0 ]
//    //    [ x y z 1 ]
//    // Change from matrix_float4x4 to arrays of floats
//
//    public func translationValuesCA()->[Float] {
//        return [self[3,0], self[3,1], self[3,2]]
//    }
//    public func rotationMatrixCA()->[Float] {
//        return [
//            self[0,0], self[0,1], self[0,2], self[0,3],
//            self[1,0], self[1,1], self[1,2], self[1,3],
//            self[2,0], self[2,1], self[2,2], self[2,3],
//            self[3,0], self[3,1], self[3,2], self[3,3]
//        ]
//    }
//}
