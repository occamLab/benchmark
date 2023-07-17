//
//  PredictPose.swift
//  ios_logger2
//
//  Created by Daniel Sudzilouski on 7/14/23.
//

import Foundation


func loadModule(filePath: String) -> TorchModule {
    if let filePath = Bundle.main.path(forResource: "model", ofType: "pt"),
        let module = TorchModule(fileAtPath: filePath) {
        return module
    } else {
        fatalError("Can't find the model file!")
    }
}

