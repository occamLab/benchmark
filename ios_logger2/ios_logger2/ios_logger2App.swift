//
//  ios_logger2App.swift
//  ios_logger2
//
//  Created by Daniel Sudzilouski on 6/6/23.
//

import SwiftUI
import Firebase
import FirebaseStorage
import FirebaseAuth

import ARCoreGARSession


@main
struct ios_logger2App: App {
    
    
    init() {
        FirebaseApp.configure()
    }
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .onAppear() {
                    Auth.auth().signInAnonymously() {authResult,error in
                        print("Auth.auth().currentUID \(Auth.auth().currentUser?.uid)")
                    }
                }
        }
    }
}
