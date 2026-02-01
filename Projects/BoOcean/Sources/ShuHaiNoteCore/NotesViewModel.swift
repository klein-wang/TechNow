import Foundation
import CoreData

public class NotesViewModel: ObservableObject {
    @Published public private(set) var notes: [Note] = []

    private let context: NSManagedObjectContext

    public init(context: NSManagedObjectContext = PersistenceController.shared.container.viewContext) {
        self.context = context
        fetchNotes()
    }

    public func fetchNotes() {
        let request = NSFetchRequest<Note>(entityName: "Note")
        request.sortDescriptors = [NSSortDescriptor(key: "date", ascending: false)]
        do {
            notes = try context.fetch(request)
        } catch {
            print("Failed to fetch notes: \(error.localizedDescription)")
            notes = []
        }
    }

    public func loadNotes() { fetchNotes() }

    public var uniqueTags: [String] {
        var set = Set<String>()
        for note in notes {
            if let tags = note.tags as? [String] {
                for t in tags { set.insert(t) }
            }
        }
        let sorted = Array(set).sorted()
        return ["全部"] + sorted
    }

    public func addNote(bookTitle: String, content: String, quote: String, tags: [String]) {
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

    public func deleteNote(_ note: Note) {
        context.delete(note)
        save()
    }

    public func deleteNote(at offsets: IndexSet) {
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
