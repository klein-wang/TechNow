import Foundation
import CoreData

class NotesViewModel: ObservableObject {
    @Published var notes: [Note] = []

    private let context: NSManagedObjectContext

    init(context: NSManagedObjectContext = PersistenceController.shared.container.viewContext) {
        self.context = context
        fetchNotes()
    }

    func fetchNotes() {
        let request = NSFetchRequest<Note>(entityName: "Note")
        request.sortDescriptors = [NSSortDescriptor(key: "date", ascending: false)]
        do {
            notes = try context.fetch(request)
        } catch {
            print("Failed to fetch notes: \(error.localizedDescription)")
            notes = []
        }
    }

    func loadNotes() { fetchNotes() }

    var uniqueTags: [String] {
        var set = Set<String>()
        for note in notes {
            if let tags = note.tags as? [String] {
                for t in tags { set.insert(t) }
            }
        }
        let sorted = Array(set).sorted()
        return ["全部"] + sorted
    }

    func addNote(bookTitle: String, content: String, quote: String, tags: [String]) {
        let entity = NSEntityDescription.entity(forEntityName: "Note", in: context)!
        let note = NSManagedObject(entity: entity, insertInto: context) as! Note
        note.setValue(UUID(), forKey: "id")
        note.bookTitle = bookTitle
        note.content = content
        note.quote = quote
        note.tags = tags
        note.date = Date()
        save()
    }

    func deleteNote(_ note: Note) {
        context.delete(note)
        save()
    }

    func deleteNote(at offsets: IndexSet) {
        offsets.map { notes[$0] }.forEach { context.delete($0) }
        save()
    }

    private func save() {
        do {
            try context.save()
            fetchNotes()
        } catch {
            print("Failed to save context: \(error.localizedDescription)")
        }
    }
}