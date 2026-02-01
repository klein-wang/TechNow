import XCTest
@testable import ShuHaiNote

class NotesTests: XCTestCase {

    var viewModel: NotesViewModel!

    override func setUpWithError() throws {
        super.setUp()
        viewModel = NotesViewModel()
    }

    override func tearDownWithError() throws {
        viewModel = nil
        super.tearDown()
    }

    func testAddNote() throws {
        let initialCount = viewModel.notes.count
        let note = Note(bookTitle: "Test Book", content: "This is a test note.", quote: "Test quote.", tags: ["Test"])
        
        viewModel.add(note: note)
        
        XCTAssertEqual(viewModel.notes.count, initialCount + 1)
        XCTAssertEqual(viewModel.notes.last?.bookTitle, "Test Book")
    }

    func testDeleteNote() throws {
        let note = Note(bookTitle: "Test Book", content: "This is a test note.", quote: "Test quote.", tags: ["Test"])
        viewModel.add(note: note)
        
        let initialCount = viewModel.notes.count
        viewModel.delete(note: note)
        
        XCTAssertEqual(viewModel.notes.count, initialCount - 1)
    }

    func testFetchNotes() throws {
        let notes = viewModel.fetchNotes()
        XCTAssertNotNil(notes)
        XCTAssertTrue(notes.count >= 0)
    }

    func testFilterNotesByTag() throws {
        let note1 = Note(bookTitle: "Test Book 1", content: "Note 1 content.", quote: "Quote 1.", tags: ["Test"])
        let note2 = Note(bookTitle: "Test Book 2", content: "Note 2 content.", quote: "Quote 2.", tags: ["Other"])
        viewModel.add(note: note1)
        viewModel.add(note: note2)

        let filteredNotes = viewModel.filterNotes(by: "Test")
        XCTAssertEqual(filteredNotes.count, 1)
        XCTAssertEqual(filteredNotes.first?.bookTitle, "Test Book 1")
    }
}