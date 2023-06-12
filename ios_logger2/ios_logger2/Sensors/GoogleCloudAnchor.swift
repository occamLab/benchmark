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
    let garSession: GARSession?

    init() {
        garSession = try? GARSession(apiKey: Secrets.garAPIKey, bundleIdentifier: nil)
    }
    
    func collectData(motion: CMDeviceMotion?, frame: ARFrame?) {

    }
    

    
    
}


