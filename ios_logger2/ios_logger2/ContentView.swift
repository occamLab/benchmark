//
//  ContentView.swift
//  ios_logger2
//
//  Created by Daniel Sudzilouski on 6/6/23.
//

import SwiftUI

class MotionManager: ObservableObject {
    @Published var motion: Motion?
    @Published var phaseText: String = "Currently in mapping phase!!"
    @Published var isPresentingUploadConfirmation: Bool = false

    
    init() {
        // note that UI updates must happen on the main thread which is why DispatchQueue.main.sync is used
        Task {
            // allow time for alignment of phone
            DispatchQueue.main.sync {
                self.phaseText = "Align phone to starting position (10 seconds)!!. HOLD VERTICALLY AGINST TABLE EDGE (camera staight on). For some reason the Arkit initial pose is absolute garbage if you hold the camera face down."
            }
            try! await Task.sleep(for: .seconds(10))
            // start collecting data
            DispatchQueue.main.sync {
                motion = Motion() // initialize
                self.phaseText = "Currently in mapping phase (20 seconds)"
            }
            
            // allow time for mapping phase
            try! await Task.sleep(for: .seconds(20))
            DispatchQueue.main.sync {
                self.phaseText = "Transitioning between phases!!"
            }
            
            // allow time for alignment of phone
            await motion!.switchToLocalization()
            DispatchQueue.main.sync {
                self.phaseText = "Align phone to starting position (10 seconds)!!. HOLD VERTICALLY AGINST TABLE EDGE (camera staight on). For some reason the Arkit initial pose is absolute garbage if you hold the camera face down."
            }

            try! await Task.sleep(for: .seconds(10))
            // reset our knowledge of our position
            motion!.initMotionSensors()
            motion!.initArSession()
            
            
            // allow time for localization phase
            DispatchQueue.main.sync {
                self.phaseText = "Currently in localization phase!!"
            }
            
            try! await Task.sleep(for: .seconds(20)) // allow time for localization phase
            DispatchQueue.main.sync {
                self.phaseText = "Finished localization phase!!"
                self.isPresentingUploadConfirmation = true
            }
            
        }
    }
}


struct ContentView: View {
    @ObservedObject var motionManager = MotionManager()
    
    var body: some View {
        ZStack {
            if(!motionManager.isPresentingUploadConfirmation && motionManager.motion != nil) {
                ARViewRepresentable(arDelegate: motionManager.motion!)
            }
            VStack {
                Image(systemName: "globe")
                    .imageScale(.large)
                    .foregroundColor(.accentColor)
                
                Text(motionManager.phaseText)
                
                .confirmationDialog("Upload Data",
                                    isPresented: $motionManager.isPresentingUploadConfirmation) {
                    Button("Cancel Upload Data", role: .cancel, action: {
                        Task {
                            motionManager.motion!.stopDataCollection()
                            motionManager.phaseText = "Cancelled uploading data"
                            motionManager.isPresentingUploadConfirmation = false
                        }
                    })
                    Button("Upload Data?", role: .destructive, action: {
                        Task {
                            await motionManager.motion!.finalExport()
                            motionManager.phaseText = "Uploaded data"
                            motionManager.isPresentingUploadConfirmation = false
                        }
                    })
                }
            
            }
            .padding()
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
