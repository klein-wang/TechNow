import SwiftUI

struct NoteDetailView: View {
    var note: Note

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(note.bookTitle)
                .font(.largeTitle)
                .fontWeight(.bold)

            Text(note.quote)
                .font(.title2)
                .italic()
                .foregroundColor(.gray)

            Text("笔记内容")
                .font(.headline)

            Text(note.content)
                .font(.body)

            Text("标签: \(note.tags.joined(separator: ", "))")
                .font(.subheadline)
                .foregroundColor(.blue)

            Spacer()

            HStack {
                Button(action: {
                    // Edit action
                }) {
                    Text("编辑")
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(8)
                }

                Button(action: {
                    // Delete action
                }) {
                    Text("删除")
                        .padding()
                        .background(Color.red)
                        .foregroundColor(.white)
                        .cornerRadius(8)
                }
            }
        }
        .padding()
        .navigationTitle("笔记详情")
    }
}