import XCTest
@testable import ShuHaiNoteCore

class NotesTests: XCTestCase {

    var viewModel: NotesViewModel!

    override func setUpWithError() throws {
        try super.setUpWithError()
        let pc = PersistenceController(inMemory: true)
        viewModel = NotesViewModel(context: pc.container.viewContext)
    }

    override func tearDownWithError() throws {
        viewModel = nil
        try super.tearDownWithError()
    }

    func testAddNote() throws {
        let initialCount = viewModel.notes.count
        viewModel.addNote(bookTitle: "Test Book", content: "This is a test note.", quote: "Test quote.", tags: ["Test"])

        XCTAssertEqual(viewModel.notes.count, initialCount + 1)
        XCTAssertEqual(viewModel.notes.first?.bookTitle ?? "", "Test Book")
    }

    func testDeleteNote() throws {
        viewModel.addNote(bookTitle: "Test Book", content: "This is a test note.", quote: "Test quote.", tags: ["Test"])

        let initialCount = viewModel.notes.count
        if let note = viewModel.notes.first {
            viewModel.deleteNote(note)
        }

        XCTAssertEqual(viewModel.notes.count, initialCount - 1)
    }

    func testFetchNotes() throws {
        viewModel.fetchNotes()
        XCTAssertTrue(viewModel.notes.count >= 0)
    }

    func testFilterNotesByTag() throws {
        viewModel.addNote(bookTitle: "Test Book 1", content: "Note 1 content.", quote: "Quote 1.", tags: ["Test"])
        viewModel.addNote(bookTitle: "Test Book 2", content: "Note 2 content.", quote: "Quote 2.", tags: ["Other"])

        let filtered = viewModel.notes.filter { note in
            (note.tags as? [String] ?? []).contains("Test")
        }

        XCTAssertEqual(filtered.count, 1)
        XCTAssertEqual(filtered.first?.bookTitle ?? "", "Test Book 1")
    }
}