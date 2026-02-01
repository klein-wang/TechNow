import Foundation
import CoreData

extension Note {
    @nonobjc public class func fetchRequest() -> NSFetchRequest<Note> {
        return NSFetchRequest<Note>(entityName: "Note")
    }

    @NSManaged public var bookTitle: String?
    @NSManaged public var content: String?
    @NSManaged public var quote: String?
    @NSManaged public var tags: [String]?
    @NSManaged public var date: Date?
}
