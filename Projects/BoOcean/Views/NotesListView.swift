import SwiftUI

struct NotesListView: View {
    @StateObject private var viewModel = NotesViewModel()
    @State private var selectedTag: String = "全部"
    @State private var searchText = ""
    
    var filteredNotes: [Note] {
        viewModel.notes.filter { note in
            if selectedTag == "全部" { return true }
            return note.tags.contains(selectedTag)
        }.filter { note in
            if searchText.isEmpty { return true }
            return note.bookTitle.localizedCaseInsensitiveContains(searchText) ||
                   note.content.localizedCaseInsensitiveContains(searchText) ||
                   note.quote.localizedCaseInsensitiveContains(searchText)
        }
    }

    var body: some View {
        NavigationView {
            List(filteredNotes) { note in
                NavigationLink(destination: NoteDetailView(note: note)) {
                    VStack(alignment: .leading) {
                        Text(note.bookTitle).font(.headline)
                        Text(note.quote).font(.subheadline).italic()
                        HStack {
                            ForEach(note.tags, id: \.self) { tag in
                                Text(tag).font(.caption).padding(4).background(Color.blue.opacity(0.2)).cornerRadius(8)
                            }
                        }
                    }
                }
            }
            .searchable(text: $searchText)
            .navigationTitle("我的笔记")
            .toolbar {
                NavigationLink("添加") {
                    AddNoteView()
                }
            }
            .picker("标签", selection: $selectedTag) {
                ForEach(viewModel.uniqueTags, id: \.self) { tag in
                    Text(tag).tag(tag)
                }
            }
            .pickerStyle(SegmentedPickerStyle())
        }
        .onAppear {
            viewModel.loadNotes()  // 从Core Data加载
        }
    }
}