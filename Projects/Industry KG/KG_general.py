import pandas as pd
from neo4j import GraphDatabase

class Gum_KG_Generate(object):
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def create_node(self, label, name):
        with self._driver.session() as session:
            query = "CREATE (a:{} {{name: '{}'}}) RETURN a".format(label, name)
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
    password = "xxxxx"
    excel_file_path = 'C:\\Users\\yuanchen.b.wang\\Desktop\\MARS YNG Gum\\Data Objects & Collection\\PLC_record\\db_path_and_mapping.xlsx'

    example = Gum_KG_Generate(uri, user, password)

    # Extract node list from Excel file
    df = example.extract_nodes_from_excel(excel_file_path)
    machine_set = set()

    example.create_node("Target", "Gum Weight")

    # Create nodes based on the extracted list
    for index, row in df.iterrows():
        parameter_name = row['Parameters']
        machine_name = row['Machine']
        example.create_node("Parameter", parameter_name)
        if machine_name not in machine_set:
            example.create_node("Machine", machine_name)
            example.create_relationship("Machine", machine_name, "Target", "Gum Weight", "HAS_Effect")
            machine_set.add(machine_name)
        example.create_relationship("Machine", machine_name, "Parameter", parameter_name, "HAS_Parameter")

    example.close()