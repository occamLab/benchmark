//
//  ContentView.swift
//  online_ace
//
//  Created by occamlab on 1/18/24.
//

import SwiftUI

struct ContentView: View {
    var body: some View {
        VStack {
            Image(systemName: "globe")
                .imageScale(.large)
                .foregroundStyle(.tint)
            Text("Hello, world!")
        }
        .padding()
    }
    let model = ace_encoder_pretrained()
    let pred = model.prediction(x_1: [])
}

#Preview {
    ContentView()
}
