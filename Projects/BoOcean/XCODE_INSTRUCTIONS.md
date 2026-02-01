# Running the UI demo in Xcode

Quick steps to open and run the app UI (SwiftUI) and run tests.

1) Open the repo in Xcode

- Option A (recommended): Open the package in Xcode

  - In Xcode: File → Open... → select `Package.swift` at the repo root.
  - Xcode will open the package. You can view sources under `Sources/ShuHaiNoteCore` and `Tests`.

- Option B: Create a new App project and add files

  1. Xcode → File → New → Project → App (SwiftUI). Name it `ShuHaiNote`.
  2. Add the existing source files into the project:
     - Drag `ShuHaiNoteApp.swift`, `Views/`, `ViewModels/`, `CoreData/`, `Models/`, `Tests/` into the project navigator.
     - When prompted, add files to the app target (check the app target box).
  3. Set the project's deployment target to iOS 15+ (or your device).

2) Run the app in Simulator

- Select a Simulator (e.g., iPhone 14) and press Run (Cmd+R). The app entrypoint is `ShuHaiNoteApp.swift`.

3) Use SwiftUI Previews

- Open `Views/ContentView.swift` and click the Canvas Resume button to show the SwiftUI preview.

4) Run the unit tests (command line)

```bash
# from repo root
swift test --package-path /Users/yuanchenwang/Documents/GitHub/TechNow/Projects/BoOcean
```

This runs the in-memory tests we configured. You already ran tests locally; they passed.

5) Notes & troubleshooting

- If you choose Option A (open Package.swift), Xcode can run tests for the package, but to run the full iOS app you still need an app target (Option B) or create an Xcode project that depends on the package target.
- If SwiftUI previews fail, open the canvas diagnostics and make sure the active scheme is the app target and a simulator device is selected.
- If you prefer, I can generate an Xcode project skeleton that includes all files and a configured app target — tell me and I'll add it.

---
File locations referenced:

- `ShuHaiNoteApp.swift` — app entry
- `Views/ContentView.swift` — main UI
- `ViewModels/NotesViewModel.swift` — data layer
- `CoreData/PersistenceController.swift` — programmatic Core Data stack
- `Tests/NotesTests.swift` — unit tests (uses in-memory store)
