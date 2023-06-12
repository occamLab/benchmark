//
//  Points.swift
//  ios_logger2
//
//  Created by Zoe McGinnis on 6/9/23.
//

import Foundation
import ARKit
import CoreMotion

/*
 *  Implements data collection and encoding into a protobuf message for timeseries of point cloud data, specifically the number of points in the point cloud
 */
class PointCloud: Sensor {
    var sensorName: String = "point_cloud"
    public var series = PointCloudSeries()
    
    func collectData(motion: CMDeviceMotion?, frame: ARFrame?) {
        if(frame != nil) {
            let timestamp: Double = frame!.timestamp
            if(frame!.rawFeaturePoints?.points.count != nil) {
                let points_in_cloud: UInt32 = UInt32(frame!.rawFeaturePoints!.points.count)
                var measurement = PointCloudTimestamp()
                measurement.timestamp = getUnixTimestamp(moment: timestamp)
                measurement.pointsInCloud = points_in_cloud
                series.measurements.append(measurement)
            }
        }
    }
}
