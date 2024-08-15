import pandas as pd
import re
import os
import csv
import datetime
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
            query = "MERGE (a:{} {{".format(label)
            for k, v in attributes.items():
                k = k.replace(' ', '_').replace(':', '_').replace('（', '_').replace('）', '_')  # replace space with underscore
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

    def extract_nodes_from_excel(self, excel_file_path, sheet_name='Sheet1'):
        df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
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
                    print(path)
                    
                    # Write the path to the CSV file
                    csv_writer.writerow([str(path)])

                print(f"File exported into: {csv_file_path}.")
    

if __name__ == "__main__":
    # 启动Neo4j - bin\neo4j-admin server console
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "Quanjiaxinfu1@"
    excel_file_path = 'C:\\Users\\yuanchen.b.wang\\Desktop\\MARS YNG Gum\\Data Objects & Collection\\db_path_and_mapping.xlsx'

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


    # Measure & Target
    for index, row in df_effect.iterrows():
        measure_name = row['Measure']
        target_name = row['Target']
        session.create_node("Measure", name=measure_name, product="Gum Stick")
        session.create_node("Target", name=target_name, product="Gum Stick")
        session.create_relationship("Measure", measure_name , "Target", target_name, "HAS_Target") # Measure & Target

    # Process & Man
    for process_name in df_process['Process'].unique():
        session.create_node("Process", name=process_name, product="Gum Stick")
        session.create_relationship("Process", process_name, "Measure", "Gum Weight", "HAS_Effect") # Process & Measure
    for man_name in df_process['Man'].unique():
        session.create_node("Man", name=man_name, product="Gum Stick")

    # Machine
    for index, row in df_process.iterrows():
        machine_name = row['Machine']
        attributes = row.to_dict()
        attributes.pop('Machine')
        session.create_node("Machine", name=machine_name, product="Gum Stick", **attributes)

    # Environment
    for env_name in df_env['Environment'].unique():
        session.create_node("Environment", name=env_name, product="Gum Stick")
    # Material
    for material_name in df_material['Material'].unique():
        session.create_node("Material", name=material_name, product="Gum Stick")
    # Product & SKU
    for product_name in df_product['Product'].unique():
        session.create_node("Product", name=product_name, product="Gum Stick")
        session.create_relationship("Process", "Mixing" , "Product", product_name, "HAS_Product") # Process & Product
    for index, row in df_product.iterrows():
        product_name = row['Product']
        sku_name = row['SKU']
        attributes = row.to_dict()
        attributes.pop('Product')
        attributes.pop('SKU')
        session.create_node("SKU", name=sku_name, product="Gum Stick", **attributes)
        session.create_relationship("Product", product_name , "SKU", sku_name, "HAS_SKU") # Product & SKU

    # Machine and Process
    for index, row in df_process.iterrows():
        machine_name = row['Machine']
        process_name = row['Process']
        man_name = row['Man']
        session.create_relationship("Man", man_name, "Machine", machine_name, "HAS_Responsible") # Man & Machine
        session.create_relationship("Machine", machine_name, "Process", process_name, "HAS_Process") # Machine & Process

    # Machine and Parameter
    for index, row in df.iterrows():
        parameter_name = row['Parameters']
        machine_name = row['Machine']
        attributes = row.to_dict()
        attributes.pop('Process')
        attributes.pop('Parameters')
        attributes.pop('Machine')
        session.create_node("Parameter", name=parameter_name, machine=machine_name, product="Gum Stick", **attributes)
        session.create_relationship("Machine", machine_name, "Parameter", parameter_name, "HAS_Parameter") # Machine & Parameter
        
    # Parameter and Measure
    for index, row in df_effect.iterrows():
        parameter_name = row['Parameter']
        measure_name = row['Measure']
        session.create_relationship("Parameter", parameter_name, "Measure", measure_name, "HAS_Effect") # Parameter & Measure

    # Environment and Process
    for index, row in df_env.iterrows():
        env_name = row['Environment']
        process_name = row['Process']
        session.create_relationship("Process", process_name, "Environment", env_name, "HAS_Environmental_Factor") # Process & Environment

    # Material and Process
    for index, row in df_material.iterrows():
        material_name = row['Material']
        process_name = row['Process']
        session.create_relationship("Process", process_name, "Material", material_name, "HAS_Material") # Process & Material
    
    # check schema: CALL db.schema.visualization()
    # return product path: MATCH p = (n:Machine)-[*]->(k:Process)-[*]->(m:SKU) RETURN p;
    # return parameter path: MATCH p = (n:Machine)-[*]->(k:Parameter)-[*]->(m:Measure) RETURN p;
    # return all path: MATCH p = (n)-[r]->(m) RETURN p;

    # session.set_node_color('Parameter','表面粉下涂抹器（设定值）','purple') #不会改变实际的颜色

    csv_file_path = r'C:\Users\yuanchen.b.wang\Desktop\MARS YNG Gum\KG\output\Gum_KG_Data.csv'
    current_date = datetime.datetime.now().strftime('%Y%m%d')
    base_name, extension = os.path.splitext(csv_file_path)
    csv_file_path = f"{base_name}_{current_date}{extension}"

    session.export_all_data(csv_file_path)
    session.close()

    # Links: https://www.cnblogs.com/yin-jihu/p/17983407