import SwiftUI

struct NotesListView: View {
    @ObservedObject var viewModel: NotesViewModel
    @State private var selectedTag: String = "全部"
    @State private var searchText = ""

    var filteredNotes: [Note] {
        viewModel.notes.filter { note in
            if selectedTag == "全部" { return true }
            if let tags = note.tags as? [String] {
                return tags.contains(selectedTag)
            }
            return false
        }.filter { note in
            if searchText.isEmpty { return true }
            let book = note.bookTitle ?? ""
            let content = note.content ?? ""
            let quote = note.quote ?? ""
            return book.localizedCaseInsensitiveContains(searchText) ||
                   content.localizedCaseInsensitiveContains(searchText) ||
                   quote.localizedCaseInsensitiveContains(searchText)
        }
    }

    var body: some View {
        List {
            ForEach(filteredNotes, id: \ .objectID) { note in
                NavigationLink(destination: NoteDetailView(note: note)) {
                    VStack(alignment: .leading) {
                        Text(note.bookTitle ?? "未知书名").font(.headline)
                        Text(note.quote ?? "").font(.subheadline).italic()
                        HStack {
                            if let tags = note.tags as? [String] {
                                ForEach(tags, id: \ .self) { tag in
                                    Text(tag).font(.caption).padding(4).background(Color.blue.opacity(0.2)).cornerRadius(8)
                                }
                            }
                        }
                    }
                }
            }
            .onDelete { idx in
                viewModel.deleteNote(at: idx)
            }
        }
        .searchable(text: $searchText)
        .navigationTitle("我的笔记")
        .toolbar {
            NavigationLink(destination: AddNoteView(viewModel: viewModel)) {
                Text("添加")
            }
        }
        .picker("标签", selection: $selectedTag) {
            ForEach(viewModel.uniqueTags, id: \ .self) { tag in
                Text(tag).tag(tag)
            }
        }
        .pickerStyle(SegmentedPickerStyle())
        .onAppear {
            viewModel.loadNotes()
        }
    }
}