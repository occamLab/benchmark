//
//  PredictPose.swift
//  ios_logger2
//
//  Created by Daniel Sudzilouski on 7/14/23.
//

import Foundation

class PosePredictor {
    
    var currentModule: TorchModule
    
    init(filePath: String) {
        guard let model = TorchModule(fileAtPath: filePath) else {
            fatalError("Can't find the model file!")
        }
        currentModule = model
    }
    
}

class ModuleLoader {
    
    static func loadFromFirebase() async -> PosePredictor {
        let modelLocation = await UploadManager.shared.downloadFile(filePath: "danielTest/mobile.model.ptl")
        print(modelLocation!.path)
        return PosePredictor(filePath: modelLocation!.path)
    }
    
}
