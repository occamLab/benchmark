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
    @State var phaseText: String = "Currently in mapping phase!!"
    
    var body: some View {
        ZStack {
            ARViewRepresentable(arDelegate: motion)
            VStack {
                Image(systemName: "globe")
                    .imageScale(.large)
                    .foregroundColor(.accentColor)
                
                Text(phaseText)
                
                let mappingTimer = Timer.scheduledTimer(withTimeInterval: 10, repeats: false) { timer in
                    Task {
                        phaseText = "Transitioning between phases!!"
                        await Motion.shared.switchToLocalization()
                        phaseText = "Currently in localization phase!!"
                        
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
