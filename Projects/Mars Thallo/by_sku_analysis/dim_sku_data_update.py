import os
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

# Generate the SQL statements
sql_statements = generate_update_sql(db_name, df_sku, columns, name_mapping_dict)

# Print the SQL statements
for sql in sql_statements:
    print(sql)