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

@main
struct ios_logger2App: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .onAppear() {
                    FirebaseApp.configure()
                    Auth.auth().signInAnonymously() {authResult,error in
                        print("Auth.auth().currentUID \(Auth.auth().currentUser?.uid)")
                    }
//                    DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
//                        if let data = "hello".data(using: .utf8) {
//                            Storage.storage().reference(withPath: "test/test.txt").putData(data) { status in
//                                print("test")
//                            }
//                        }
//                    }
                }
        }
    }
}
