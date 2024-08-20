import pandas as pd
import re
import os
import configparser
import csv
import datetime
from neo4j import GraphDatabase
# pip install -r requirements.txt


class Gum_KG_Generate(object):
    def __init__(self, uri, user, password, database):
        self._driver = GraphDatabase.driver(uri, auth=(user, password), database=database)

    def close(self):
        self._driver.close()

    def delete_all(self):
        with self._driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def create_node(self, label, **attributes):
        with self._driver.session() as session:
            query = "MERGE (a:{} {{".format(label)
            for k, v in attributes.items():
                k = re.sub('[\n,.：()、—— :（）#\/]', '_', k).replace('#', 'No')
                query += "{}:'{}',".format(k, v)
            query = query.rstrip(',')
            query += "}) RETURN a"
            result = session.run(query)
            print(result, label)

    def create_relationship(self, node1_label, node1_name, node2_label, node2_name, relationship_type):
        with self._driver.session() as session:
            query = "MATCH (a:{} {{name: '{}'}}), (b:{} {{name: '{}'}}) MERGE (a)-[:{}]->(b)".format(
                node1_label, node1_name, node2_label, node2_name, relationship_type)
            result = session.run(query)
            print(result, node1_name, relationship_type, node2_name)

    def set_node_color(self, label, name, color):
        with self._driver.session() as session:
            result = session.run("MATCH (n:{} {{name: '{}'}}) RETURN n".format(label, name))
            node = result.single()
            if node:
                session.run("MATCH (n) WHERE elementID(n) = $elementid SET n.color = $color", elementid=node["n"].element_id, color=color)
                print(f'Color of node {name} has been updated into {color}.')

    def extract_nodes_from_excel(self, excel_file_path, sheet_name='Sheet1', start_row=1):
        df = pd.read_excel(excel_file_path, sheet_name=sheet_name, skiprows=start_row-1, header=0)
        return df

    def export_all_data(self, csv_file_path):
        # Create the directory if it doesn't exist
        directory = os.path.dirname(csv_file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        with self._driver.session() as session:
            # Open a CSV file to write the results
            with open(csv_file_path, mode='w', newline='', encoding='utf-8-sig') as csvfile: # utf-16 is a more robust encoding for handling Unicode characters
                csv_writer = csv.writer(csvfile)
                
                # Write the header row
                csv_writer.writerow(['Path'])
                
                # Run the Cypher query to get all paths
                result = session.run("MATCH p = (n)-[r]->(m) RETURN p")
                
                # Write each path to the CSV file
                for record in result:
                    # Extract the path from the record
                    path = record['p']
                    # print(path)
                    # Write the path to the CSV file
                    csv_writer.writerow([str(path)])

                print(f"File exported into: {csv_file_path}.")


if __name__ == "__main__":
    # 启动Neo4j - Windows: bin\neo4j-admin server console
    # 启动Neo4j - Mac: ./bin/neo4j-admin server console
    config = configparser.ConfigParser()
    config.read('config.ini')

    if not config.sections():
        print("Error: config.ini file is empty or not found.")
        print("Current Working Directory:", os.getcwd())
        exit(1)

    uri = config.get('neo4j', 'uri')
    user = config.get('neo4j', 'user')
    password = config.get('neo4j', 'password')
    database = config.get('neo4j', 'database')

    energy_file_path = config.get('files', 'energy_file_path')
    gum_file_path = config.get('files', 'gum_file_path')
    export_csv_file_path = config.get('files', 'export_csv_file_path')
    current_date = datetime.datetime.now().strftime('%Y%m%d')
    base_name, extension = os.path.splitext(export_csv_file_path)
    export_csv_file_path = f"{base_name}_{current_date}{extension}"


    session = Gum_KG_Generate(uri, user, password, database)

    # Delete all nodes before creating new ones
    session.delete_all()

    # Extract node list from Excel file
    df_energy = session.extract_nodes_from_excel(energy_file_path, 'GUM-KG0813', 4)
    df_product = session.extract_nodes_from_excel(gum_file_path, 'product')
    df_process = session.extract_nodes_from_excel(gum_file_path, 'process_machine_man')
    df_env = session.extract_nodes_from_excel(gum_file_path, 'environment')
    df_material = session.extract_nodes_from_excel(gum_file_path, 'material')
    df_parameter = session.extract_nodes_from_excel(gum_file_path, 'parameter')
    df_effect = session.extract_nodes_from_excel(gum_file_path, 'effect')


    session.create_node("Product", name="Gum Stick", product="Gum Stick")
    # Measure & Target
    for index, row in df_effect.iterrows():
        measure_name = row['Measure']
        target_name = row['Target']
        session.create_node("Measure", name=measure_name, product="Gum Stick")
        session.create_node("Target", name=target_name, product="Gum Stick")
        session.create_relationship("Measure", measure_name , "Target", target_name, "HAS_Target") # Measure & Target
        session.create_relationship("Measure", measure_name , "Product", "Gum Stick", "HAS_Product") # Measure & Product

    # Process & Machine & Man
    for index, row in df_process.iterrows():
        process_name = row['Process']
        machine_name = row['Machine']
        man_name = row['Man']
        session.create_node("Process", name=process_name, product="Gum Stick") # create Process node
        session.create_node("Man", name=man_name, product="Gum Stick")
        session.create_node("Machine", name=machine_name, product="Gum Stick")
        # session.create_relationship("Process", process_name, "Measure", "Gum Weight", "HAS_Effect") # Process & Measure
        session.create_relationship("Man", man_name, "Machine", machine_name, "HAS_Machine") # Man & Machine
        session.create_relationship("Machine", machine_name, "Process", process_name, "HAS_Process") # Machine & Process

    # Environment and Process
    for index, row in df_env.iterrows():
        env_name = row['Environment']
        process_name = row['Process']
        session.create_node("Environment", name=env_name, product="Gum Stick")
        session.create_relationship("Environment", env_name, "Process", process_name, "HAS_Process") # Environment & Process
    # Material and Process
    for index, row in df_material.iterrows():
        material_name = row['Material']
        process_name = row['Process']
        session.create_node("Material", name=material_name, product="Gum Stick")
        session.create_relationship("Material", material_name, "Process", process_name, "HAS_Process") # Material & Process

    # Product and SKU
    for index, row in df_product.iterrows():
        product_name = row['Product']
        sku_name = row['SKU']
        attributes = row.to_dict()
        attributes.pop('Product')
        attributes.pop('SKU')
        session.create_node("Product", name=product_name, product="Gum Stick")
        session.create_node("SKU", name=sku_name, product="Gum Stick", **attributes)
        session.create_relationship("SKU", sku_name, "Product", product_name , "HAS_Product") # Product & SKU

    # Machine and Process and Step
    for index, row in df_energy.iterrows():
        value_stream_name = row['Value Stream']
        process_name = row['Process']
        step_name = row['Step']
        machine_name = row['设备']
        attributes = row.to_dict()
        attributes.pop('Step')
        session.create_node("Step", name=step_name, product="Gum Stick", **attributes)
        session.create_node("Value_Stream", name=value_stream_name, product="Gum Stick")
        session.create_node("Process", name=process_name, product="Gum Stick")
        session.create_node("Machine", name=machine_name, product="Gum Stick")
        session.create_relationship("Product", "Gum Stick", "Value_Stream", value_stream_name, "HAS_Value_Stream") # Product & Value_Stream
        session.create_relationship("Process", process_name, "Step", step_name, "HAS_Step") # Process & Step
        session.create_relationship("Process", process_name, "Product", product_name, "HAS_Product") # Process & Product
        session.create_relationship("Step", step_name, "Machine", machine_name, "HAS_Machine") # Step & Machine

    # Machine and Parameter
    for index, row in df_parameter.iterrows():
        parameter_name = row['Parameters']
        machine_name = row['Machine']
        attributes = row.to_dict()
        attributes.pop('Process')
        attributes.pop('Parameters')
        attributes.pop('Machine')
        session.create_node("Parameter", name=parameter_name, machine=machine_name, product="Gum Stick", **attributes)
        session.create_relationship("Machine", machine_name, "Parameter", parameter_name, "HAS_Parameter") # Machine & Parameter

    # check schema: CALL db.schema.visualization()

    # return 工序到产出物 process-product-sku path: MATCH p = (n)-[*]->(m:Product)-[*]->(k) RETURN p;
    # return 工序到工步 process-step path: MATCH p = (n:Process)-[*]->(m:Step) RETURN p;
    # return 设备到人 machine-man path: MATCH p = (n:Man)-[*]->(m:Machine) RETURN p;
    # return 设备到参数 machine-parameter path: MATCH p = (n:Machine)-[*]->(m:Parameter) RETURN p;
    # return 产品到SKU product-sku path: MATCH p = (n:Product)-[*]->(m:SKU) RETURN p;
    # return 环境变量 environment-process path: MATCH p = ()-[r]-(e:Environment) RETURN p;
    # return 测量 measure-product path: MATCH p = ()-[r]-(e:Measure) RETURN p;
    # return 物料到工步再到工序 material-(step)-process path: MATCH p = (n:Material)-[*]->(m:Process) RETURN p;

    # check saving: MATCH (n:Step) WHERE n.Saving_kJ <> "nan" RETURN n;

    # return parameter path: MATCH p = (n:Machine)-[*]->(k:Parameter)-[*]->(m:Measure) RETURN p;
    # session.set_node_color('Parameter','表面粉下涂抹器（设定值）','purple') #不会改变实际的颜色

    session.export_all_data(export_csv_file_path)
    session.close()

    # Links: https://www.cnblogs.com/yin-jihu/p/17983407