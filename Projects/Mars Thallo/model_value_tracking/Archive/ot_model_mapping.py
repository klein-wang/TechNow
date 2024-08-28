import pandas as pd

ot_data = pd.read_csv('/17_ML_Parameters_20240815.csv')
recommendations = pd.read_excel('/recommendation_log.xlsx')

# 数据时间格式统一
ot_data['TS'] = pd.to_datetime(ot_data['TS'])

ot_change_data = ['Tag', 'Last_Value', "Current_Value", 'TS']

recommendations['timestamp'] = pd.to_datetime(recommendations['create_time'])


acceptance_count = 0

#时间窗口
time_window = pd.Timedelta(minutes=5)

# 遍历每一条推荐记录
for index, rec_row in recommendations.iterrows():
    # 提取推荐时间和推荐调整参数
    rec_time = rec_row['timestamp']
    
    for param in rec_row.index:
        if param not in ['timestamp', 'create_time'] and pd.notna(rec_row[param]):
            rec_value = rec_row[param]
            
            # 找到推荐时间后的OT数据（在时间窗口内）
            future_ot_data = ot_data[(ot_data['timestamp'] > rec_time) & 
                                     (ot_data['timestamp'] <= rec_time + time_window)]
            
            # 获取推荐时间点OT数据中的参数值
            ot_value_before = ot_data.loc[ot_data['timestamp'] == rec_time, param].values[0]
            
            # 遍历未来OT数据，检查是否有匹配推荐调整的变化
            for _, ot_row in future_ot_data.iterrows():
                ot_value_after = ot_row[param]
                if ot_value_after == ot_value_before + rec_value:
                    acceptance_count += 1
                    break  # 一旦找到匹配，就停止进一步搜索

print(f"操作员在模型推荐后的5分钟按照推荐进行了参数调整的次数为: {acceptance_count}")
