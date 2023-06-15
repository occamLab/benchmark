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

enum Phase {
    case mappingPhase
    case localizationPhase
}

protocol SensorProtocol {
    var currentPhase: Phase {get set}
        
    /* The sensor name is used in the filename of the bundled data */
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
    
    /* Any work that needs to be done before the data is uploaded */
    func additionalUpload() async -> Void
    
    /* Handle switching to localization mode if needed */
    func switchToLocalization() -> Void
}

protocol ourMessages {
    associatedtype MappingPhase
    associatedtype LocalizationPhase
    var mappingPhase: MappingPhase {get}
    var localizationPhase: LocalizationPhase {get}
}

extension SensorProtocol {
    /* Uses the UploadManager to queue uploads of the encoded protobuf messages to firebase storage*/
    func uploadProtobuf() {
        let data: Data? = try? series.serializedData()
        UploadManager.shared.putData(data!, contentType: "application/protobuf", fullPath: sensorName + ".proto")
    }
    
    /* Can be implemented by sensors such as video if needed */
    func additionalUpload() async -> Void {
    }
    
    /* Can be implemented if needed */
    func switchToLocalization() -> Void {
        
    }
    
    /* Process the timestamp from CMDeviceMotion/ARFrame and convert it to unix timestamp
     * The timestamps are technically undocumented and could break in the future
     */
    func getUnixTimestamp(moment: TimeInterval) -> Double {
        let refDate: Date = Date.now - ProcessInfo.processInfo.systemUptime
        let curTime: Date = Date(timeInterval: moment, since: refDate)
        return curTime.timeIntervalSince1970
    }
    
    /* Helper method for checking if we are in mapping phase */
    func isMappingPhase() -> Bool {
        if case currentPhase = Phase.mappingPhase {
            return true
        }
        return false
    }
    
    /* Helper method for checking if we are in localization phase */
    func isLocalizationPhase() -> Bool {
        if case currentPhase = Phase.localizationPhase {
            return true
        }
        return false
    }
    
}

/* We just use this to set default values on the sensor. Sensors should conform to both Sensor and SensorProtocol */
class Sensor {
    var currentPhase: Phase = Phase.mappingPhase
}
