//
//  Sensor.swift
//  ios_logger2
//
//  Created by Daniel Sudzilouski on 6/6/23.
//

import Foundation

protocol Sensor {
    /* Collect a snapshot of data */
    func collectData() -> Void
    
}
