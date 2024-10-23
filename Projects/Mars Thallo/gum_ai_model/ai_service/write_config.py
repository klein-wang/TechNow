import json
import pandas as pd

df_config = pd.read_excel('SKU参数配置表.xlsx', sheet_name='sheet2')
df_name = pd.read_csv('sku_mapping.csv')

name_mapping = {
    '重量_UB': 'Weight_UB',
    '重量_LB': 'Weight_LB',
    '厚度_UB': 'Thickness_UB',
    '厚度_LB': 'Thickness_LB',
    '深度_UB': 'Depth_UB',
    '深度_LB': 'Depth_LB',
    '长度_UB': 'Length_UB',
    '长度_LB': 'Length_LB',
    '宽度_UB': 'Width_UB',
    '宽度_LB': 'Width_LB',
    '1号辊_UB': 'Gap1_UB',
    '1号辊_LB': 'Gap1_LB',
    '1号辊_Step_UB': 'Gap1_Step_UB',
    '2号辊_UB': 'Gap2_UB',
    '2号辊_LB': 'Gap2_LB',
    '2号辊_Step_UB': 'Gap2_Step_UB',
    '3号辊_UB': 'Gap3_UB',
    '3号辊_LB': 'Gap3_LB',
    '3号辊_Step_UB': 'Gap3_Step_UB',
    '定型辊_Step_UB': 'GapFS_Step_UB',
    '定型辊_UB': 'GapFS_UB',
    '定型辊_LB': 'GapFS_LB',
    '横刀_Step_UB': 'CS_Step_UB',
    '横刀_UB': 'CS_UB',
    '横刀_LB': 'CS_LB',
    '挤压机_Step_UB': 'Temp_Step_UB',
    '挤压机_UB': 'Temp_UB',
    '挤压机_LB': 'Temp_LB'
}

config_data = {}
for i, row in df_config.iterrows():
    config_data[row['sku_name_en']] = {
        name_mapping[k]: float(row[k]) for k in name_mapping
    }

with open('sku_config.json', 'w') as f:
    json.dump(config_data, f)
