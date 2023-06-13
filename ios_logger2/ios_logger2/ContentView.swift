//
//  ContentView.swift
//  ios_logger2
//
//  Created by Daniel Sudzilouski on 6/6/23.
//

import SwiftUI

struct ContentView: View {
    let motion = Motion.shared
    @State var isPresentingConfirm: Bool = false
    @State var hideButton: Bool = false
    
    var body: some View {
        ZStack {
            ARViewRepresentable(arDelegate: motion)
            VStack {
                Image(systemName: "globe")
                    .imageScale(.large)
                    .foregroundColor(.accentColor)
                
                if(!hideButton) {
                    Button("Upload Data", role: .destructive) {
                        isPresentingConfirm = true;
                    }
                    .confirmationDialog("Are you sure?",
                                        isPresented: $isPresentingConfirm) {
                        Button("Send Data? (data was recorded since app launch)", role: .destructive) {
                            Task {
                                await self.motion.export()
                                hideButton = true;
                            }
                        }
                    }
                }
            }
        }
        .padding()
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
