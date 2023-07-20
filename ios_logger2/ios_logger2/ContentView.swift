//
//  ContentView.swift
//  ios_logger2
//
//  Created by Daniel Sudzilouski on 6/6/23.
//

import ARCore
import SwiftUI
import Firebase
import FirebaseStorage
import FirebaseAuth

class MotionManager: ObservableObject {
    public var arView: ARSCNView = ARSCNView(frame: .zero)
    @Published var interactiveLocalize: InteractiveLocalizer
    @Published var motion: Motion?
    @Published var isPresentingUploadConfirmation: Bool = false
    @Published var mappingComplete = false
    @Published var localizationComplete = false
    
    init() {
        interactiveLocalize = InteractiveLocalizer(_arSCNView: arView)
    }
    func setUpMotion() {
        motion = Motion(_arView: arView)
    }
    func setupInteractiveLocalizer() {
        interactiveLocalize.initArSession()
    }
    func stopInteractiveLocalizer() {
        interactiveLocalize.stop()
    }
    func setAnchorName(anchorName: String) {
        interactiveLocalize.selectedAnchor = anchorName
    }
    func mappingPhase() {
        motion!.disabledCollection = false
        DispatchQueue.main.asyncAfter(deadline: .now() + 20) {
            self.motion!.disabledCollection = true
            self.mappingComplete = true
        }
    }
    func transitionPhase() async {
        await motion!.switchToLocalization()
        motion!.initMotionSensors()
        motion!.initArSession()
        self.motion!.disabledCollection = false
    }
    func localizationPhase() {
        motion!.disabledCollection = false
        DispatchQueue.main.asyncAfter(deadline: .now() + 10) {
            self.motion!.disabledCollection = true
            self.localizationComplete = true
        }
    }
    func resetRecordNewAnchors() {
        self.isPresentingUploadConfirmation = false
        self.mappingComplete = false
        self.localizationComplete = false
    }

    func listFromFirebase(completionHandler: @escaping ([[String]])->()) {
        var filesList: [[String]] = []
        let storageReference = Storage.storage().reference().child("iosLoggerDemo/trainedModels")
        storageReference.listAll { (result, error) in
            if let error = error {
                print(error)
            }
            var fullNamesList: [String] = []
            var fileNamesList: [String] = ["Select anchor"]
            for item in result!.items {
                let fullName: String = "\(item)"
                let fileNameWithPrefixArray: [String] = fullName.components(separatedBy: "/")
                let fileNameWithPrefix: String  = fileNameWithPrefixArray.last!
                let fileName: String = fileNameWithPrefix.components(separatedBy: ".")[0]
                fullNamesList.append(fullName)
                fileNamesList.append(fileName)
            }
            filesList.append(fileNamesList)
            filesList.append(fullNamesList)
            return completionHandler(filesList)
        }
    }
}

enum AppPhase {
    case beginning
    case anchorSelection
    case showAnchor
    case alignmentPhase
    case resetPosePhase
    case mappingPhase
    case mappingComplete
    case resetPosePhase2
    case localizationPhase
    case localizationComplete
    case enterAnchorName
    case uploadData
    case dataNotUploaded
    case finishedUpload
}

struct ContentView: View {
    @StateObject var motionManager = MotionManager()
    @State var appPhase = AppPhase.beginning
    @State var showButton = true
    @State private var anchorCreationName = "default_anchor_name"
    @State private var selection = "Select anchor"
    @State private var selectionLocation = "Select anchor"
    @State var anchorNames: [String] = ["Select anchor"]
    @State var anchors: [[String]] = []
    
    var body: some View {
        ZStack {
            if(!motionManager.isPresentingUploadConfirmation && motionManager.motion != nil) {
                ARViewRepresentable(arDelegate: motionManager.motion!)
            }
            VStack {
        
                switch appPhase {
                // Choose which route to go down: localization demo or record new anchor
                case .beginning:
                    Button("Localization demo") {
                        motionManager.listFromFirebase() { fileNamesList in
                            self.anchorNames = fileNamesList[0]
                            self.anchors = fileNamesList
                            self.appPhase = .anchorSelection
                        }
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                    Button("Record new anchor") {
                        self.appPhase = .alignmentPhase
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                
                // Localization demo route
                case .anchorSelection: //user selects cloud anchor, render something at the origin
                    Text("Choose an anchor from the dropdown")
                    Picker("Select an anchor", selection: $selection) {
                        ForEach(anchors[0], id: \.self) {
                            Text($0)
                        }
                    }
                    .controlSize(.large)
                    .pickerStyle(.menu)
                    if (selection != "Select anchor") {
                        Button("Continue") {
                            let selectionIndex: Int = anchors[0].firstIndex(of: selection)!
                            self.selectionLocation = anchors[1][selectionIndex-1]
                            self.appPhase = .showAnchor
                            self.selection = selection
                            motionManager.setAnchorName(anchorName: selection)
                            motionManager.setupInteractiveLocalizer()
                            print(self.selectionLocation)
                        }
                        .buttonStyle(.borderedProminent)
                        .controlSize(.large)
                    }
                case .showAnchor:
                    // localization demo goes here
                    let translations = motionManager.interactiveLocalize.resolvedTranslationValues
                    Text("\(translations[0]) \(translations[1]) \(translations[2])")
                    InteractiveLocalizerARViewRepresentable(arDelegate: motionManager.interactiveLocalize.arView)
                    Button("Return to start menu") {
                        print(self.selection)
                        print(self.selectionLocation)
                        self.selection = "Select anchor"
                        self.selectionLocation = "Select anchor"
                        self.anchorNames = ["Select anchor"]
                        self.anchors = []
                        self.appPhase = .beginning
                        motionManager.stopInteractiveLocalizer()
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                    
                // Record new anchor route
                case .alignmentPhase:
                    Text("Align phone to starting position! Hold vertically against table edge (camera straight on).")
                    Button("Phone is aligned") {
                        motionManager.setUpMotion()
                        self.appPhase = .resetPosePhase
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                case .resetPosePhase:
                    Text("Walk to a random place to reset the pose.")
                    Button("Okay, I did") {
                        self.appPhase = .mappingPhase
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                case .mappingPhase:
                    Text("Mapping phase (20 seconds).")
                    if (showButton) {
                        Button("Begin mapping phase") {
                            showButton = false
                            motionManager.mappingPhase()
                        }
                        .buttonStyle(.borderedProminent)
                        .controlSize(.large)
                    }
                case .mappingComplete:
                    Text("Mapping phase complete! Align phone to starting position! Hold vertically against table edge (camera straight on).")
                    Button("Phone aligned") {
                        showButton = true
                        Task {
                            await motionManager.transitionPhase()
                            self.appPhase = .resetPosePhase2
                        }
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                case .resetPosePhase2:
                    Text("Walk to a random place to reset the pose.")
                    Button("Okay, I did") {
                        self.appPhase = .localizationPhase
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                case .localizationPhase:
                    Text("Localization phase (10 seconds).")
                    if (showButton) {
                        Button("Begin localization phase") {
                            showButton = false
                            motionManager.localizationPhase()
                        }
                        .buttonStyle(.borderedProminent)
                        .controlSize(.large)
                    }
                case .localizationComplete:
                    Text("Localization phase complete!")
                    Button("Next") {
                        showButton = true
                        self.appPhase = .enterAnchorName
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                case .enterAnchorName:
                    Text("").alert("Name your new anchor", isPresented: .constant(true)) {
                        TextField("Anchor name goes here", text: $anchorCreationName)
                        Button("OK", action: {
                            self.appPhase = .uploadData
                        })
                    }
                case .uploadData:
                    Button("Cancel Upload Data", role: .cancel, action: {
                        Task {
                            motionManager.motion!.stopDataCollection()
                            motionManager.isPresentingUploadConfirmation = false
                        }
                        self.appPhase = .dataNotUploaded
                    })
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                    Button("Upload Data?", role: .destructive, action: {
                        Task {
                            await motionManager.motion!.finalExport(tarName: anchorCreationName)
                            motionManager.isPresentingUploadConfirmation = false
                        }
                        self.appPhase = .finishedUpload
                    })
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)

                case .dataNotUploaded:
                    Text("Not so great success! Data not uploaded.")
                    Button("Back to start") {
                        motionManager.resetRecordNewAnchors()
                        self.appPhase = .beginning
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                case .finishedUpload:
                    Text("Great success! Anchor created.")
                    Button("Back to start") {
                        motionManager.resetRecordNewAnchors()
                        self.appPhase = .beginning
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
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
