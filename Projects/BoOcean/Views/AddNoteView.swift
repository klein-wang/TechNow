import SwiftUI

struct AddNoteView: View {
    @State private var bookTitle = ""
    @State private var content = ""
    @State private var quote = ""
    @State private var tagsText = ""
    @Environment(\.dismiss) private var dismiss
    @ObservedObject var viewModel: NotesViewModel

    var body: some View {
        Form {
            Section("书籍信息") {
                TextField("书名", text: $bookTitle)
            }
            Section("笔记内容") {
                TextEditor(text: $content)
                    .frame(minHeight: 100)
            }
            Section("金句摘抄") {
                TextEditor(text: $quote)
                    .frame(minHeight: 80)
            }
            Section("标签 (用逗号分隔)") {
                TextField("e.g. 励志,哲学", text: $tagsText)
            }
        }
        .navigationTitle("添加笔记")
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button("保存") {
                    let tags = tagsText.split(separator: ",").map { String($0.trimmingCharacters(in: .whitespaces)) }.filter { !$0.isEmpty }
                    if quote.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty { return }
                    let limitedTags = Array(tags.prefix(10))
                    viewModel.addNote(bookTitle: bookTitle, content: content, quote: quote, tags: limitedTags)
                    dismiss()
                }
            }
        }
    }
}
