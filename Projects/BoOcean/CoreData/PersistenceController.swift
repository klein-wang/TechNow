import CoreData

struct PersistenceController {
    static let shared = PersistenceController()

    let container: NSPersistentContainer

    init(inMemory: Bool = false) {
        let model = NSManagedObjectModel()

        let noteEntity = NSEntityDescription()
        noteEntity.name = "Note"
        noteEntity.managedObjectClassName = "Note"

        var properties: [NSAttributeDescription] = []

        let idAttr = NSAttributeDescription()
        idAttr.name = "id"
        idAttr.attributeType = .UUIDAttributeType
        idAttr.isOptional = false
        properties.append(idAttr)

        let bookTitleAttr = NSAttributeDescription()
        bookTitleAttr.name = "bookTitle"
        bookTitleAttr.attributeType = .stringAttributeType
        bookTitleAttr.isOptional = true
        properties.append(bookTitleAttr)

        let contentAttr = NSAttributeDescription()
        contentAttr.name = "content"
        contentAttr.attributeType = .stringAttributeType
        contentAttr.isOptional = true
        properties.append(contentAttr)

        let quoteAttr = NSAttributeDescription()
        quoteAttr.name = "quote"
        quoteAttr.attributeType = .stringAttributeType
        quoteAttr.isOptional = true
        properties.append(quoteAttr)

        let tagsAttr = NSAttributeDescription()
        tagsAttr.name = "tags"
        tagsAttr.attributeType = .transformableAttributeType
        tagsAttr.attributeValueClassName = "NSArray"
        tagsAttr.valueTransformerName = NSValueTransformerName.secureUnarchiveFromDataTransformerName.rawValue
        tagsAttr.isOptional = true
        properties.append(tagsAttr)

        let dateAttr = NSAttributeDescription()
        dateAttr.name = "date"
        dateAttr.attributeType = .dateAttributeType
        dateAttr.isOptional = true
        properties.append(dateAttr)

        noteEntity.properties = properties

        model.entities = [noteEntity]

        container = NSPersistentContainer(name: "ShuHaiNote", managedObjectModel: model)

        if inMemory {
            let description = NSPersistentStoreDescription()
            description.type = NSInMemoryStoreType
            container.persistentStoreDescriptions = [description]
        }

        container.loadPersistentStores { desc, error in
            if let error = error {
                fatalError("Failed to load store: \(error)")
            }
        }
        container.viewContext.mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy
    }
}
