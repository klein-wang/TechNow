import SwiftUI

@main
struct ShuHaiNoteApp: App {
    let persistenceController = PersistenceController.shared
    @StateObject var viewModel = NotesViewModel(context: PersistenceController.shared.container.viewContext)

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\.managedObjectContext, persistenceController.container.viewContext)
                .environmentObject(viewModel)
        }
    }
}
import SwiftUI

@main
struct ShuHaiNoteApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}