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
    @Published var clipDuration: Int = 30
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
    func startRecordingVideo() {
        motion?.videoSensor?.startRecording()
    }
    func resetGARSession() {
        motion?.googleCloudAnchor?.resetGARSession()
    }
    
    func mappingPhase() {
        motion!.disabledCollection = false
        DispatchQueue.main.asyncAfter(deadline: .now() + Double(clipDuration)) {
            self.motion!.disabledCollection = true
            self.mappingComplete = true
        }
    }
    func finalizeMapping() async {
        await motion!.finalizeMapping()
    }
    
    func transitionPhase() async {
        motion!.initMotionSensors()
        motion!.initArSession()
    }
    
    func localizationPhase() {
        motion!.disabledCollection = false
        DispatchQueue.main.asyncAfter(deadline: .now() + Double(clipDuration)) {
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
    case anchorSelection(isRealtimeLocalization: Bool)
    case showAnchor
    case alignmentPhase
    case resetPosePhase
    case mappingPhase
    case mappingComplete
    case resetPosePhase2
    case restartingGARSession
    case localizationPhase
    case localizationComplete
    case enterAnchorName
    case uploadData(isTestDataOnly: Bool)
    case dataNotUploaded
    case finishedUpload
    
    func isMappingPhase()->Bool {
        if case .mappingPhase = self {
            return true
        }
        return false
    }
    
    func isLocalizationPhase()->Bool {
        if case .localizationPhase = self {
            return true
        }
        return false
    }
}

struct ContentView: View {
    @StateObject var motionManager = MotionManager()
    @State var appPhase = AppPhase.beginning
    @State var showButton = true
    @State var hostedCloudAnchorID = ""
    @State private var anchorCreationName = ""
    @State private var selection = "Select anchor"
    @State private var selectionLocation = "Select anchor"
    @State var anchors: [[String]] = []
    let cloudIDLength = 35
    
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
                            self.anchors = fileNamesList
                            for (i, name) in self.anchors[0].enumerated() {
                                if name.starts(with: "ua-") {
                                    let end = name.index(name.startIndex, offsetBy: cloudIDLength + 1)
                                    self.anchors[0][i] = String(name[end...])
                                }
                            }
                            self.appPhase = .anchorSelection(isRealtimeLocalization: true)
                        }
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                    Button("Record new anchor") {
                        self.appPhase = .alignmentPhase
                        self.anchorCreationName = ""
                        self.hostedCloudAnchorID = ""
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                    
                    Button("Test anchor") {
                        self.anchorCreationName = ""
                        motionManager.listFromFirebase() { fileNamesList in
                            self.anchors = fileNamesList
                            for (i, name) in self.anchors[0].enumerated() {
                                print("name \(name)")
                                if name.starts(with: "ua-") {
                                    let end = name.index(name.startIndex, offsetBy: cloudIDLength + 1)
                                    self.anchors[0][i] = String(name[end...])
                                }
                            }
                            self.appPhase = .anchorSelection(isRealtimeLocalization: false)
                        }
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                    
                    // Localization demo route
                case .anchorSelection(let isRealtimeLocalization): //user selects cloud anchor, render something at the origin
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
                            motionManager.setAnchorName(anchorName: selection)
                            print("selection \(selection)")
                            self.selection = selection
                            if let cloudAnchorIndexRange = selectionLocation.range(of: "ua-") {
                                let start = selectionLocation.index(cloudAnchorIndexRange.lowerBound, offsetBy: 0)
                                let end = selectionLocation.index(cloudAnchorIndexRange.lowerBound, offsetBy: cloudIDLength)
                                hostedCloudAnchorID = String(selectionLocation[start..<end])
                            } else {
                                hostedCloudAnchorID = ""
                            }
                            
                            if isRealtimeLocalization {
                                self.appPhase = .showAnchor
                                motionManager.setupInteractiveLocalizer()
                            } else {
                                self.appPhase = .mappingComplete
                                anchorCreationName = self.selection
                                motionManager.setUpMotion()
                                if !hostedCloudAnchorID.isEmpty {
                                    motionManager.motion?.setHostedCloudAnchorID(anchorID: hostedCloudAnchorID)
                                }
                                
                                Task {
                                    print("switching to localization!")
                                    await self.motionManager.motion?.switchToLocalization()
                                }
                            }
                        }
                        .buttonStyle(.borderedProminent)
                        .controlSize(.large)
                    }
                case .showAnchor:
                    // localization demo goes here
                    InteractiveLocalizerARViewRepresentable(arDelegate: motionManager.interactiveLocalize.arView)
                    Button("Return to start menu") {
                        print(self.selection)
                        print(self.selectionLocation)
                        self.selection = "Select anchor"
                        self.selectionLocation = "Select anchor"
                        self.anchors = []
                        self.appPhase = .beginning
                        motionManager.stopInteractiveLocalizer()
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                    
                    // Record new anchor route
                case .alignmentPhase:
                    Text("Align phone to starting position! Hold vertically against table edge (camera straight on).")
                    TextField("Clip Duration", value: $motionManager.clipDuration, formatter: NumberFormatter()).padding(4)
                        .overlay(
                            RoundedRectangle(cornerRadius: 14)
                                .stroke(Color.green, lineWidth: 2)
                        )
                        .padding()
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
                    Text("Mapping phase (\(motionManager.clipDuration) seconds).")
                    if (showButton) {
                        Button("Begin mapping phase") {
                            showButton = false
                            motionManager.mappingPhase()
                            motionManager.startRecordingVideo()
                            AnnouncementManager.shared.announce(announcement: "recording video")
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
                            await motionManager.motion?.switchToLocalization()
                            self.appPhase = .resetPosePhase2
                        }
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                case .restartingGARSession:
                    Text("Waiting for GARSession to restart")
                case .resetPosePhase2:
                    Text("Walk to a random place to reset the pose.")
                    Button("Okay, I did") {                        motionManager.resetGARSession()
                        DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
                            self.appPhase = .localizationPhase
                        }
                        self.appPhase = .restartingGARSession
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                case .localizationPhase:
                    Text("Localization phase (\(motionManager.clipDuration) seconds).")
                    if (showButton) {
                        Button("Begin localization phase") {
                            showButton = false
                            motionManager.localizationPhase()
                            motionManager.startRecordingVideo()
                            AnnouncementManager.shared.announce(announcement: "recording video")
                        }
                        .buttonStyle(.borderedProminent)
                        .controlSize(.large)
                    }
                case .localizationComplete:
                    Text("Localization phase complete!")
                    Button("Next") {
                        showButton = true
                        if anchorCreationName.isEmpty {
                            self.appPhase = .enterAnchorName
                        } else {
                            self.appPhase = .uploadData(isTestDataOnly: true)
                        }
                    }
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                case .enterAnchorName:
                    Text("Name your new anchor")
                    VStack {
                        TextField("Anchor name goes here", text: $anchorCreationName)
                        Button("OK", action: {
                            print(anchorCreationName.count, anchorCreationName.isEmpty)
                            self.appPhase = .uploadData(isTestDataOnly: false)
                        }).disabled(anchorCreationName.isEmpty)
                    }
                case .uploadData(let isTestDataOnly):
                    Button("Cancel Upload Data", role: .cancel, action: {
                        Task {
                            UploadManager.shared.files = []
                            motionManager.motion!.stopDataCollection()
                            motionManager.isPresentingUploadConfirmation = false
                        }
                        self.appPhase = .dataNotUploaded
                    })
                    .buttonStyle(.borderedProminent)
                    .controlSize(.large)
                    Button("Upload Data?", role: .destructive, action: {
                        Task {
                            let tarName: String
                            if isTestDataOnly {
                                tarName = "testing_\(UUID().uuidString)_\(anchorCreationName.trimmingCharacters(in: .whitespaces))"
                            } else {
                                tarName = "training_\(motionManager.motion?.getHostedCloudAnchorID() ?? "nil")_\(anchorCreationName.trimmingCharacters(in: .whitespaces))"
                            }
                            await motionManager.motion!.finalExport(tarName: tarName)
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
            if newValue && appPhase.isMappingPhase() {
                appPhase = .mappingComplete
                Task {
                    await motionManager.finalizeMapping()
                }
            }
        }
        .onChange(of: motionManager.localizationComplete) { newValue in
            if newValue && appPhase.isLocalizationPhase() {
                appPhase = .localizationComplete
            }
        }
    }
}
