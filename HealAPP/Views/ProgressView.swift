//
//  ProgressView.swift
//  Heal
//

import SwiftUI

struct ProgressTabView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    Text("Weekly trends and insights coming soon!")
                        .foregroundColor(.secondary)
                        .padding()
                }
                .padding()
            }
            .navigationTitle("Progress")
        }
    }
}

