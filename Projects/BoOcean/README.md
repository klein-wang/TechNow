# ShuHaiNote iOS App

## Overview
"书海笔记" is an iOS application designed to help users record and manage their reading notes and quotes. The app allows users to categorize their notes using tags, search for specific entries, and receive daily inspirational quotes.

## Features
- **Note Management**: Users can add, edit, and delete notes that include the book title, content, quotes, and tags.
- **Tag Filtering**: Users can filter notes by tags and search for specific content.
- **Daily Quote Sharing**: The app sends daily notifications with a random quote from the user's notes.
- **User-Friendly Interface**: The app is designed with a clean and intuitive interface using SwiftUI.

## Setup Instructions
1. **Clone the Repository**: 
   ```
   git clone https://github.com/yourusername/ShuHaiNote.git
   ```
2. **Open the Project**: 
   Open `ShuHaiNote.xcodeproj` in Xcode.
3. **Build the App**: 
   Select a simulator or a physical device and click on the run button.
4. **Permissions**: 
   Ensure that notifications are enabled in the app settings for daily quote sharing.

## Architecture
The app follows the MVVM (Model-View-ViewModel) architecture:
- **Models**: Define the data structure (e.g., `Note`).
- **Views**: Present the user interface (e.g., `ContentView`, `AddNoteView`, `NotesListView`).
- **ViewModels**: Manage the data flow and business logic (e.g., `NotesViewModel`).

## Localization
The app supports multiple languages through the use of `Localizable.strings`. This allows for easy internationalization and customization of text displayed in the app.

## Testing Strategy
Unit tests are implemented to ensure the functionality and correctness of the app. The following components will be tested:
- **NotesViewModel**: Testing data fetching, adding, and deleting notes.
- **UI Components**: Testing the rendering of views and user interactions.

## Future Enhancements
- **Cloud Sync**: Implement iCloud support for syncing notes across devices.
- **Social Sharing**: Allow users to share quotes on social media platforms.
- **Advanced Search**: Enhance the search functionality with more filters and options.

## License
This project is licensed under the MIT License - see the LICENSE file for details.