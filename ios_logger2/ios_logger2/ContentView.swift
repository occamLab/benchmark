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
    }
    func setUpMotion() {
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
        }
    }
}

enum AppPhase {
    case alignmentPhase
    case resetPosePhase
    case mappingPhase
    case mappingComplete
    case resetPosePhase2
    case localizationPhase
    case localizationComplete
    case uploadData
}

struct ContentView: View {
    @StateObject var motionManager = MotionManager()
    @State var appPhase = AppPhase.alignmentPhase
    @State var showButton = true
    var body: some View {
        ZStack {
            if(!motionManager.isPresentingUploadConfirmation && motionManager.motion != nil) {
                ARViewRepresentable(arDelegate: motionManager.motion!)
            }
            VStack {
                
                switch appPhase {
                case .alignmentPhase:
                    Text("Align phone to starting position! Hold vertically against table edge (camera straight on).")
                    Button("Phone is aligned") {
                        print("Phone aligned")
                        motionManager.setUpMotion()
                        self.appPhase = .resetPosePhase
                    }
                case .resetPosePhase:
                    Text("Walk to a random place to reset the pose.")
                    Button("Okay, I did") {
                        self.appPhase = .mappingPhase
                    }
                case .mappingPhase:
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
                        self.appPhase = .resetPosePhase2
                    }
                case .resetPosePhase2:
                    Text("Walk to a random place to reset the pose.")
                    Button("Okay, I did") {
                        self.appPhase = .localizationPhase
                    }
                case .localizationPhase:
                    Text("Localization phase (10 seconds).")
                    if (showButton) {
                        Button("Begin localization phase") {
                            showButton = false
                            motionManager.localizationPhase()
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
            if newValue && appPhase == .mappingPhase {
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
