import os
import json
import pandas as pd

file_names = 'SKU参数配置表.xlsx'
current_file_path = os.path.abspath(__file__)
current_file_directory = os.path.dirname(current_file_path)
file_path = os.path.join(current_file_directory, file_names)

df_sku = pd.read_excel(file_path)
sku_count = len(set(df_sku['skuName']))


def generate_update_sql(db_name, df_sku, columns, name_mapping_dict):
    # List to hold all SQL statements
    sql_statements = ['BEGIN']
    
    # Iterate over each row in the DataFrame
    for index, row in df_sku.iterrows():
        # Prepare the base part of the SQL UPDATE statement
        base_sql = f"    UPDATE [{db_name}].[dbo].[yng_dim_sku_data] SET "
        set_clauses = []
        
        for col in columns:
            # Map the column name using the name_mapping_dict if it exists
            mapped_col = name_mapping_dict.get(col, col)
            value = row[col]
            set_clauses.append(f"{mapped_col} = {value}")
        
        # Join the set clauses with commas to form the SET clause of the SQL statement
        set_clause_str = ", ".join(set_clauses)
        
        # Get the SKU name from the current row
        sku_name = row['skuName']
        
        # Construct the full SQL statement by combining the base, set clause, and WHERE clause
        full_sql = f"{base_sql}{set_clause_str} WHERE sku_name = '{sku_name}';"
        sql_statements.append(full_sql)
    
    sql_statements.append('END')
    
    return sql_statements

def replace_keys_in_grouped_data(grouped_data, mapping_dict):
    for sku, data in grouped_data.items():
        # Create a new dictionary with updated keys
        new_data = {mapping_dict.get(k, k): v for k, v in data.items()}
        # Update the original grouped_data with the new_data
        grouped_data[sku] = new_data
    return grouped_data

def generate_json(df_sku):
    # Create an empty dictionary to hold the grouped data
    grouped_data = {}

    # Iterate over each row in the DataFrame
    for index, row in df_sku.iterrows():
        # Use the SKU name as the key and create a dictionary of the row data as the value
        sku_name = row['skuName']
        grouped_data[sku_name] = row.to_dict()
        del grouped_data[sku_name]['skuName']
        updated_grouped_data = replace_keys_in_grouped_data(grouped_data, json_name_mapping_dict)

    # Convert the dictionary to a JSON string
    json_data = json.dumps(updated_grouped_data, indent=4)

    # Write the JSON string to a file
    json_file_path = os.path.join(current_file_directory, 'sku_data.json')
    with open(json_file_path, 'w') as json_file:
        json_file.write(json_data)

    return json_file_path


print(f'一共有{sku_count}个SKU')
print('-------------- Running -------------- \n')
db_name = 'test-portaldb'
columns = ['重量_UB', '重量_LB', '重量_STD', '挤压机出口胶温_UB', '挤压机出口胶温_LB']
name_mapping_dict = {
    '重量_UB': 'fz_top_limit',
    '重量_LB': 'fz_bottom_limit',
    '重量_STD': 'fz_std',
    '挤压机出口胶温_UB': 'extruder_exit_gum_temp_top_limit',
    '挤压机出口胶温_LB': 'extruder_exit_gum_temp_bottom_limit'
}

json_name_mapping_dict = {
    '重量_UB': 'Weight_UB',
    '重量_LB': 'Weight_LB',
    '重量_STD': 'fz_std',
    '厚度_UB': 'Thickness_UB',
    '厚度_LB': 'Thickness_LB',
    '厚度_STD': 'fh_std',
    '深度_UB': 'Depth_UB',
    '深度_LB': 'Depth_LB',
    '深度_STD': 'fs_std',
    '长度_UB': 'Length_UB',
    '长度_LB': 'Length_LB',
    '长度_STD': 'fc_std',
    '宽度_UB': 'Width_UB',
    '宽度_LB': 'Width_LB',
    '宽度_STD': 'fk_std',
    '1号辊_Step_UB': 'Gap1_Step_UB',
    '1号辊_UB': 'Gap1_UB',
    '1号辊_LB': 'Gap1_LB',
    '2号辊_Step_UB': 'Gap2_Step_UB',
    '2号辊_UB': 'Gap2_UB',
    '2号辊_LB': 'Gap2_LB',
    '3号辊_Step_UB': 'Gap3_Step_UB',
    '3号辊_UB': 'Gap3_UB',
    '3号辊_LB': 'Gap3_LB',
    '定型辊_Step_UB': 'GapFS_Step_UB',
    '定型辊_UB': 'GapFS_UB',
    '定型辊_LB': 'GapFS_LB',
    '横刀_Step_UB': 'CS_Step_UB',
    '横刀_UB': 'CS_UB',
    '横刀_LB': 'CS_LB',
    '挤压机_Step_UB': 'Temp_Step_UB',
    '挤压机_UB': 'Temp_UB',
    '挤压机_LB': 'Temp_LB',
    '挤压机出口胶温_UB': 'Gum_Temp_UB',
    '挤压机出口胶温_LB': 'Gum_Temp_LB'
}

json_file_path = generate_json(df_sku)

# Generate the SQL statements
sql_statements = generate_update_sql(db_name, df_sku, columns, name_mapping_dict)

# Print the SQL statements
for sql in sql_statements:
    print(sql)

