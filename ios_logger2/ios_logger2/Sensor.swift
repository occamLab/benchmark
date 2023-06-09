//
//  Sensor.swift
//  ios_logger2
//
//  Created by Daniel Sudzilouski on 6/6/23.
//

import Foundation
import ARKit
import CoreMotion
import SwiftProtobuf

protocol Sensor {
    var sensorName: String {get}
    /*
     * It seems like in Swift if you just make this series: SwiftProtobuf.Message
     * it will require all implementations of Sensors to have exactly type SwiftProtobuf.Message for Sensors.series
     * This syntax appears to create a generic conforming to SwiftProtobuf.Message and allow Sensor.series to subclass SwiftProtobuf.Message as well
     */
     associatedtype AnyMessage : Message
     var series: AnyMessage {get set}
    
    /* Collect a snapshot of data */
    func collectData(motion: CMDeviceMotion?, frame: ARFrame?) -> Void
    
    func additionalUpload() async -> Void
}

extension Sensor {
    
    /* Uses the UploadManager to queue uploads of the encoded protobuf messages to firebase storage*/
    func uploadProtobuf() {
        let data: Data? = try? series.serializedData()
        UploadManager.shared.putData(data!, contentType: "application/protobuf", fullPath: sensorName + ".proto")
    }
    
    /* Can be implemented by sensors such as video if needed */
    func additionalUpload() async -> Void {
        
    }
    
}
