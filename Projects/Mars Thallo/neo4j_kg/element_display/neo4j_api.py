from neo4j import GraphDatabase

class HelloWorldExample(object):
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def delete_all(self):
        with self._driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def create_node(self, label, **attributes):
        with self._driver.session() as session:
            query = "CREATE (a:{} ) SET ".format(label)
            for k, v in attributes.items():
                query += "a.{} = '{}',".format(k, v)
            query = query.rstrip(',')
            query += " RETURN a"
            result = session.run(query)
            print(result)

if __name__ == "__main__":
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "Quanjiaxinfu1@"
    example = HelloWorldExample(uri, user, password)

    # Delete all nodes before creating new ones
    example.delete_all()

    example.create_node("Message", message="Hi!")
    example.create_node("Person", name="Klein", age=30)
    example.create_node("Greeting", message="Hello, world!", sender="Klein")
    example.close()