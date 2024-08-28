import pandas as pd
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
                k = k.replace(' ', '_').replace(':', '_')  # replace space with underscore
                query += "a.{} = '{}',".format(k, v)
            query = query.rstrip(',')
            query += " RETURN a"
            result = session.run(query)
            print(result)

    def create_relationship(self, node1_label, node1_name, node2_label, node2_name, relationship_type):
        with self._driver.session() as session:
            query = "MATCH (a:{} {{name: '{}'}}), (b:{} {{name: '{}'}}) CREATE (a)-[:{}]->(b)".format(
                node1_label, node1_name, node2_label, node2_name, relationship_type)
            result = session.run(query)
            print(result)

    def extract_nodes_from_excel(self, excel_file_path):
        df = pd.read_excel(excel_file_path)
        return df

if __name__ == "__main__":
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "Quanjiaxinfu1@"
    excel_file_path = 'C:\\Users\\yuanchen.b.wang\\Desktop\\MARS YNG Gum\\Data Objects & Collection\\PLC_record\\db_path_and_mapping.xlsx'

    example = HelloWorldExample(uri, user, password)

    # Delete all nodes before creating new ones
    example.delete_all()

    # Extract node list from Excel file
    df = example.extract_nodes_from_excel(excel_file_path)
    machine_set = set()

    example.create_node("Target", name="Gum Weight", machine="SPC", process="Sheeting")

    # Create nodes based on the extracted list
    for index, row in df.iterrows():
        parameter_name = row['Parameters']
        machine_name = row['Machine']
        attributes = row.to_dict()
        attributes.pop('Parameters')
        attributes.pop('Machine')
        example.create_node("Parameter", name=parameter_name, machine=machine_name, process="Sheeting", **attributes)
        if machine_name not in machine_set:
            example.create_node("Machine", name=machine_name, process="Sheeting")
            example.create_relationship("Machine", machine_name, "Target", "Gum Weight", "HAS_Effect")
            machine_set.add(machine_name)
        example.create_relationship("Machine", machine_name, "Parameter", parameter_name, "HAS_Parameter")

    example.close()