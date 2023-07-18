//
//  ContentView.swift
//  ios_logger2
//
//  Created by Daniel Sudzilouski on 6/6/23.
//

import SwiftUI

class MotionManager: ObservableObject {
    @Published var motion: Motion?
    @Published var phaseText: String = "Currently in mapping phase!"
    @Published var isPresentingUploadConfirmation: Bool = false
    @Published var mappingComplete = false
    @Published var localizationComplete = false
    

    
    init() {
        print("Init")
//        // note that UI updates must happen on the main thread which is why DispatchQueue.main.sync is used
//        Task {
//            // allow time for alignment of phone
//            DispatchQueue.main.sync {
//                self.phaseText = "Align phone to starting position (10 seconds)! HOLD VERTICALLY AGAINST TABLE EDGE (camera staight on). For some reason the Arkit initial pose is absolute garbage if you hold the camera face down."
//            }
//             try! await Task.sleep(for: .seconds(10))
//
//            DispatchQueue.main.sync {
//                // initialize
//                // we don't want to collect data for the first few seconds so that the mapping
//                // data does not exactly start in the same visual place as the localization data
//                // that could help the cloud anchor model cheat
//                self.phaseText = "Walk to a random place to reset the pose."
//            }
//            try! await Task.sleep(for: .seconds(10))
//
//            // start collecting data
//            DispatchQueue.main.sync {
//                self.phaseText = "Currently in mapping phase (20 seconds)."
//                motion!.disabledCollection = false
//            }
//
//            // allow time for mapping phase
//            try! await Task.sleep(for: .seconds(20))
//            DispatchQueue.main.sync {
//                self.phaseText = "Transitioning between phases!"
//                motion!.disabledCollection = true
//            }
//
//            // allow time for alignment of phone
//            await motion!.switchToLocalization()
//            DispatchQueue.main.sync {
//                self.phaseText = "Align phone to starting position (10 seconds)! HOLD VERTICALLY AGAINST TABLE EDGE (camera staight on). For some reason the Arkit initial pose is absolute garbage if you hold the camera face down."
//            }
//
//            try! await Task.sleep(for: .seconds(10))
//            // reset our knowledge of our position
//            motion!.initMotionSensors()
//            motion!.initArSession()
//
//            // we don't want to collect data for the first few seconds so that the mapping
//            // data does not exactly start in the same visual place as the localization data
//            // that could help the cloud anchor model cheat
//            DispatchQueue.main.sync {
//                self.phaseText = "Walk to a random place to reset the pose"
//            }
//            try! await Task.sleep(for: .seconds(10))
//
//
//            // allow time for localization phase
//            DispatchQueue.main.sync {
//                self.phaseText = "Currently in localization phase!!"
//                motion!.disabledCollection = false
//            }
//
//            try! await Task.sleep(for: .seconds(20)) // allow time for localization phase
//            DispatchQueue.main.sync {
//                self.phaseText = "Finished localization phase!!"
//                self.isPresentingUploadConfirmation = true
//                motion!.disabledCollection = true
//            }
//        }
    }
    func setUpMotion() {
        print("setUpMotion")
        motion = Motion()
    }
    func mappingPhase() {
        motion!.disabledCollection = false
        DispatchQueue.main.asyncAfter(deadline: .now() + 20) {
            self.motion!.disabledCollection = true
            self.mappingComplete = true
        }
    }
    func transitionPhase() {
        motion!.initMotionSensors()
        motion!.initArSession()
    }
    func localizationPhase() {
        motion!.disabledCollection = false
        DispatchQueue.main.asyncAfter(deadline: .now() + 10) {
            self.motion!.disabledCollection = true
            self.localizationComplete = true
        }
    }
    func localizationPhaseComplete() {
        DispatchQueue.main.asyncAfter(deadline: .now() + 10) {
            self.isPresentingUploadConfirmation = true
            print("Great")
        }
    }
}

enum AppPhase {
    case phaseOne
    case phaseTwo
    case phaseThree
    case mappingComplete
    case localizationPhase
    case localizationComplete
    case uploadData
}

struct ContentView: View {
    @StateObject var motionManager = MotionManager()
    @State var appPhase = AppPhase.phaseOne
    @State var showButton = true
    var body: some View {
        ZStack {
            if(!motionManager.isPresentingUploadConfirmation && motionManager.motion != nil) {
                ARViewRepresentable(arDelegate: motionManager.motion!)
            }
            VStack {
                
                switch appPhase {
                case .phaseOne:
                    Text("Align phone to starting position! Hold vertically against table edge (camera straight on).")
                    Button("Phone is aligned") {
                        print("Phone aligned")
                        motionManager.setUpMotion()
                        self.appPhase = .phaseTwo
                    }
                case .phaseTwo:
                    Text("Walk to a random place to reset the pose.")
                    Button("Okay, I did") {
                        self.appPhase = .phaseThree
                    }
                case .phaseThree:
                    Text("Mapping phase (20 seconds).")
                    if (showButton) {
                        Button("Begin mapping phase") {
                            showButton = false
                            motionManager.mappingPhase()
                        }
                    }
                case .mappingComplete:
                    Text("Mapping phase complete! Align phone to starting position! Hold vertically against table edge (camera straight on).")
                    Button("Phone aligned") {
                        showButton = true
                        motionManager.transitionPhase()
                        self.appPhase = .localizationPhase
                    }
                case .localizationPhase:
                    Text("Localization phase (10 seconds).")
                    if (showButton) {
                        Button("Begin localization phase") {
                            showButton = false
                            motionManager.localizationPhase()
//                            self.appPhase = .localizationComplete
                        }
                    }
                case .localizationComplete:
                    Text("Localization phase complete!")
                    Button("Next") {
                        self.appPhase = .uploadData
                    }
                case .uploadData:
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
        }
        .onChange(of: motionManager.mappingComplete) { newValue in
            if newValue && appPhase == .phaseThree {
                appPhase = .mappingComplete
            }
        }
        .onChange(of: motionManager.localizationComplete) { newValue in
            if newValue && appPhase == .localizationPhase {
                appPhase = .localizationComplete
            }
        }
    }
}

//struct ContentView_Previews: PreviewProvider {
//    static var previews: some View {
//        ContentView()
//    }
//}
