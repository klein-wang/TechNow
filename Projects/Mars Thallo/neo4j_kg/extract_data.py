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
                k = re.sub('[\n,.：()、—— :（）#\/]', '_', k).replace('#', 'No').replace('1号', 'no1_').replace('2号', 'no2_').replace('3号', 'no3_')
                query += "{}:'{}',".format(k, v)
            query = query.rstrip(',')
            query += "}) RETURN a"
            result = session.run(query)
            logging.info(f"Created node with label {label}: {result}")

    def create_relationship(self, node1_label, node1_name, node2_label, node2_name, relationship_type):
        with self._driver.session() as session:
            query = "MATCH (a:{} {{name: '{}'}}), (b:{} {{name: '{}'}}) MERGE (a)-[:{}]->(b)".format(
                node1_label, node1_name, node2_label, node2_name, relationship_type)
            result = session.run(query)
            # print(result, node1_name, relationship_type, node2_name)
            logging.info(f"Created relationship from {node1_name} to {node2_name} with type {relationship_type}: {result}")

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
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(script_dir, 'config.ini')
    config = configparser.ConfigParser()
    config.read(config_file_path)

    if not config.sections():
        print("Error: config.ini file is empty or not found.")
        print("Current Working Directory:", os.getcwd())
        exit(1)

    uri = config.get('neo4j', 'uri')
    user = config.get('neo4j', 'user')
    password = config.get('neo4j', 'password')
    database = config.get('neo4j', 'database')

    # Construct the relative path to the energy file
    gum_file_path = os.path.join(script_dir, config.get('files', 'gum_file_path'))
    csv_file_path = os.path.join(script_dir, config.get('files', 'export_csv_file_path'))
    current_date = datetime.datetime.now().strftime('%Y%m%d')

    session = Gum_KG_Generate(uri, user, password, database)
    # session.export_all_data(csv_file_path)
    with session._driver.session() as session:
        result = session.run("MATCH p = (n:Measure)-[*2..4]-(m:Parameter) RETURN p")
        for record in result:
            path = record['p']
            print(path,"\n\n")


    print("check schema: CALL db.schema.visualization()")

    # return 工序到产出物 process-product-sku path: MATCH p = (n)-[*]->(m:Product)-[*]->(k) RETURN p;
    # return 工序到工步 process-step path: MATCH p = (n:Process)-[*]->(m:Step) RETURN p;
    # return 设备到人 machine-man path: MATCH p = (n:Man)-[*]->(m:Machine) RETURN p;
    # return 设备到参数 machine-parameter path: MATCH p = (n:Machine)-[*]->(m:Parameter) RETURN p;
    print("return 产品到SKU product-sku path: MATCH p = (n:Product)-[*]-(m:SKU) RETURN p;")
    # return 环境变量 environment-process path: MATCH p = ()-[r]-(e:Environment) RETURN p;
    print("return 测量到参数 measure-parameter path: MATCH p = (n:Measure)-[*2..4]-(m:Parameter) RETURN p;")
    # return 物料到工步再到工序 material-(step)-process path: MATCH p = (n:Material)-[*]->(m:Process) RETURN p;

    # check saving: MATCH (n:Step) WHERE n.Saving_kJ <> "nan" RETURN n;
    # MATCH (n) DETACH DELETE n

    # return parameter path: MATCH p = (n:Machine)-[*]->(k:Parameter)-[*]->(m:Measure) RETURN p;
    # session.set_node_color('Parameter','表面粉下涂抹器（设定值）','purple') #不会改变实际的颜色

    session.close()

    # Links: https://www.cnblogs.com/yin-jihu/p/17983407