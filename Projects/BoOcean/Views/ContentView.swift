import SwiftUI

struct ContentView: View {
    @StateObject private var viewModel = NotesViewModel()

    var body: some View {
        NavigationView {
            NotesListView(viewModel: viewModel)
                .navigationTitle("书海笔记")
                .toolbar {
                    NavigationLink(destination: AddNoteView(viewModel: viewModel)) {
                        Text("添加笔记")
                    }
                }
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}