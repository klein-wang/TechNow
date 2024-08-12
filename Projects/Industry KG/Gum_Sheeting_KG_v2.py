import pandas as pd
from neo4j import GraphDatabase

class Gum_KG_Generate(object):
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def delete_all(self):
        with self._driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def create_node(self, label, **attributes):
        with self._driver.session() as session:
            query = "CREATE (a:{} {{".format(label)
            for k, v in attributes.items():
                k = k.replace(' ', '_').replace(':', '_').replace('（', '_').replace('）', '_')  # replace space with underscore
                query += "{}:'{}',".format(k, v)
            query = query.rstrip(',')
            query += "}) RETURN a"
            result = session.run(query)
            print(result, label)

    def create_relationship(self, node1_label, node1_name, node2_label, node2_name, relationship_type):
        with self._driver.session() as session:
            query = "MATCH (a:{} {{name: '{}'}}), (b:{} {{name: '{}'}}) CREATE (a)-[:{}]->(b)".format(
                node1_label, node1_name, node2_label, node2_name, relationship_type)
            result = session.run(query)
            print(result, node1_name, relationship_type, node2_name)

    def extract_nodes_from_excel(self, excel_file_path, sheet_name='Sheet1'):
        df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
        return df

if __name__ == "__main__":
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "Quanjiaxinfu1@"
    excel_file_path = 'C:\\Users\\yuanchen.b.wang\\Desktop\\MARS YNG Gum\\Data Objects & Collection\\PLC_record\\db_path_and_mapping.xlsx'

    session = Gum_KG_Generate(uri, user, password)

    # Delete all nodes before creating new ones
    session.delete_all()

    # Extract node list from Excel file
    df = session.extract_nodes_from_excel(excel_file_path, 'parameter')
    df_process = session.extract_nodes_from_excel(excel_file_path, 'process_machine_man')
    df_env = session.extract_nodes_from_excel(excel_file_path, 'environment')
    df_material = session.extract_nodes_from_excel(excel_file_path, 'material')
    df_product = session.extract_nodes_from_excel(excel_file_path, 'product')
    df_effect = session.extract_nodes_from_excel(excel_file_path, 'effect')


    # Measure
    for measure_name in df_effect['Measure'].unique():
        session.create_node("Measure", name=measure_name, process="Sheeting")
    # Process
    for process_name in df_process['Process'].unique():
        session.create_node("Process", name=process_name, process="Sheeting")
        session.create_relationship("Process", process_name, "Measure", "Gum Weight", "HAS_Effect")
    # Machine
    for machine_name in df_process['Machine'].unique():
        session.create_node("Machine", name=machine_name, process="Sheeting")
    # Man
    for man_name in df_process['Man'].unique():
        session.create_node("Man", name=man_name, process="Sheeting")
    # Environment
    for env_name in df_env['Environment'].unique():
        session.create_node("Environment", name=env_name, process="Sheeting")
    # Material
    for material_name in df_material['Material'].unique():
        session.create_node("Material", name=material_name, process="Sheeting")
    # Product
    for index, row in df_product.iterrows():
        product_name = row['Product']
        attributes = row.to_dict()
        attributes.pop('Product')
        session.create_node("Product", name=product_name, process="Sheeting", **attributes)
        session.create_relationship("Process", "Mixing" , "Product", product_name, "HAS_Product")

    # Machine and Process
    for index, row in df_process.iterrows():
        machine_name = row['Machine']
        process_name = row['Process']
        man_name = row['Man']
        session.create_relationship("Man", man_name, "Machine", machine_name, "HAS_Responsible")
        session.create_relationship("Machine", machine_name, "Process", process_name, "HAS_Process")

    # Machine and Parameter
    for index, row in df.iterrows():
        parameter_name = row['Parameters']
        machine_name = row['Machine']

        attributes = row.to_dict()
        attributes.pop('Parameters')
        attributes.pop('Machine')

        session.create_node("Parameter", name=parameter_name, machine=machine_name, process="Sheeting", **attributes)
        session.create_relationship("Machine", machine_name, "Parameter", parameter_name, "HAS_Parameter")

    # Parameter and Measure
    for index, row in df_effect.iterrows():
        parameter_name = row['Parameter']
        measure_name = row['Measure']
        session.create_relationship("Parameter", parameter_name, "Measure", measure_name, "HAS_Effect")

    # Environment and Process
    for index, row in df_env.iterrows():
        env_name = row['Environment']
        process_name = row['Process']

        session.create_relationship("Process", process_name, "Environment", env_name, "HAS_Environmental_Factor")

    # Material and Process
    for index, row in df_material.iterrows():
        material_name = row['Material']
        process_name = row['Process']

        session.create_relationship("Process", process_name, "Material", material_name, "HAS_Material")

    session.close()