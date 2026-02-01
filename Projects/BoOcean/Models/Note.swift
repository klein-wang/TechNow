// filepath: /ShuHaiNote/ShuHaiNote/Models/Note.swift

import Foundation

struct NoteItem: Identifiable, Codable {
    let id: UUID
    var bookTitle: String
    var content: String
    var quote: String
    var tags: [String]
    var date: Date

    init(bookTitle: String, content: String, quote: String, tags: [String], date: Date = Date()) {
        self.id = UUID()
        self.bookTitle = bookTitle
        self.content = content
        self.quote = quote
        self.tags = tags
        self.date = date
    }
}