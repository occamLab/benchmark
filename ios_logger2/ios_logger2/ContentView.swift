//
//  ContentView.swift
//  ios_logger2
//
//  Created by Daniel Sudzilouski on 6/6/23.
//

import SwiftUI

class MotionManager: ObservableObject {
    var motion = Motion.shared
    @Published var phaseText: String = "Currently in mapping phase!!"
    @Published var isPresentingUploadConfirmation: Bool = false

    
    init() {
        // note that UI updates must happen on the main thread which is why DispatchQueue.main.sync is used
        Task {
            try! await Task.sleep(for: .seconds(10)) // allow time for mapping phase
            DispatchQueue.main.sync {
                self.phaseText = "Transitioning between phases!!"
            }
            await Motion.shared.switchToLocalization()
            DispatchQueue.main.sync {
                self.phaseText = "Currently in localization phase!!"
            }
            try! await Task.sleep(for: .seconds(10)) // allow time for localization phase
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
            if(!motionManager.isPresentingUploadConfirmation) {
                ARViewRepresentable(arDelegate: motionManager.motion)
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
                            motionManager.motion.stopDataCollection()
                            motionManager.phaseText = "Cancelled uploading data"
                            motionManager.isPresentingUploadConfirmation = false
                        }
                    })
                    Button("Upload Data?", role: .destructive, action: {
                        Task {
                            await motionManager.motion.finalExport()
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
