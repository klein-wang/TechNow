import SwiftUI

struct ContentView: View {
    @EnvironmentObject var viewModel: NotesViewModel

    var body: some View {
        NavigationView {
            NotesListView(viewModel: viewModel)
                .navigationTitle("书海笔记")
        }
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        let vm = NotesViewModel(context: PersistenceController.shared.container.viewContext)
        ContentView().environmentObject(vm)
    }
}