import Foundation
import CoreData
import Combine

class NotesViewModel: ObservableObject {
    @Published var notes: [Note] = []
    private var cancellables = Set<AnyCancellable>()
    
    private let context = PersistenceController.shared.container.viewContext
    
    init() {
        fetchNotes()
    }
    
    func fetchNotes() {
        let request: NSFetchRequest<Note> = Note.fetchRequest()
        do {
            notes = try context.fetch(request)
        } catch {
            print("Failed to fetch notes: \(error.localizedDescription)")
        }
    }
    
    func addNote(bookTitle: String, content: String, quote: String, tags: [String]) {
        let newNote = Note(context: context)
        newNote.bookTitle = bookTitle
        newNote.content = content
        newNote.quote = quote
        newNote.tags = tags
        newNote.date = Date()
        
        saveContext()
    }
    
    func deleteNote(at offsets: IndexSet) {
        offsets.map { notes[$0] }.forEach(context.delete)
        saveContext()
    }
    
    private func saveContext() {
        do {
            try context.save()
            fetchNotes()
        } catch {
            print("Failed to save context: \(error.localizedDescription)")
        }
    }
}