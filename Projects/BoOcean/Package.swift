// swift-tools-version:5.8
import PackageDescription

let package = Package(
    name: "ShuHaiNoteCore",
    platforms: [ .macOS(.v12) ],
    products: [
        .library(name: "ShuHaiNoteCore", targets: ["ShuHaiNoteCore"]),
    ],
    targets: [
        .target(
            name: "ShuHaiNoteCore",
            path: "Sources/ShuHaiNoteCore"
        ),
        .testTarget(
            name: "ShuHaiNoteCoreTests",
            dependencies: ["ShuHaiNoteCore"],
            path: "Tests"
        )
    ]
)
