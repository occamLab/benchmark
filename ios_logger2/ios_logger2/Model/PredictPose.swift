//
//  PredictPose.swift
//  ios_logger2
//
//  Created by Daniel Sudzilouski on 7/14/23.
//

import Foundation

class PredictPose {
    
    var currentModule: TorchModule
    
    init(filePath: String) {
        guard let model = TorchModule(fileAtPath: filePath) else {
            fatalError("Can't find the model file!")
        }
        currentModule = model
    }
    
}


