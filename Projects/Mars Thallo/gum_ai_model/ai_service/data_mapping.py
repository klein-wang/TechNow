import pandas as pd
import numpy as np
from pandas.api.types import CategoricalDtype
from datetime import datetime, timedelta


def merge_data(df_params, df_spc, df_prev_merge):

    required_columns = [
        "SFBMix.plcSFBMix.dbAdditionalParameter.StateFromSheeting.bMachineRunning",
        "CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap3rdSizing.rActualPosition_inches",
        "CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap2ndSizing.rActualPosition_inches",
        "CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap1stSizing.rActualPosition_inches",
        "CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_GapFinalSizing.rActualPosition_inches",
        "CG_Sheeting.CG_Sheeting.dbHMI.Scoring.SRV_CrossScore.rSetpoint_Ratio",
        "CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rChillerSetpoint",
        "CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum1InletTemp",
        "CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum2InletTemp",
        "CG_Sheeting.CG_Sheeting.Variables.rGumExtruderExitGumTemp"
    ]
    df_params = pd.merge(pd.DataFrame.from_dict({'Tag': required_columns}), df_params, how='inner', on='Tag').\
        sort_values(by='TS', ascending=False)
    df_spc['Date'] = df_spc['DataTime']
    df_spc['Weight'] = df_spc['Actual']
    df_merge = df_spc[['Date', 'Weight']].sort_values(by='Date', ascending=False)
    dict_values = {}




def merge_OT_SPC(curated_parm, curated_spc):
    
    # Step 1: 处理 spc 数据
    spc = curated_spc[(curated_spc['EntryType'] == 3) | (curated_spc['EntryType'] == 2)] 
    spc = spc[['DataTime', 'Item', 'Load', 'Weight','ItemCode','EntryType',
                      'LengthOrThickness', 'WidthOrDepth']].copy()
    spc['DataTime'] = pd.to_datetime(spc['DataTime'], format="%Y-%m-%d %H:%M:%S", utc=True).dt.tz_localize(None)

    # 排序 entry level = 3& =2
    spc = spc.sort_values(by='DataTime', ascending=True)

    #获取长度宽度数据
    spc_00 = curated_spc[curated_spc['EntryType'] == 3]
    spc_00 = spc_00.sort_values(by='DataTime', ascending=False)
    spc_0 = spc_00.iloc[0]
    spc_10 = curated_spc[curated_spc['EntryType'] == 1] 
    spc_1 = spc_10.iloc[0]
    spc_20 = curated_spc[curated_spc['EntryType'] == 2]
    spc_20 = spc_20.sort_values(by='DataTime', ascending=False)
    spc_2 = spc_20.iloc[0]

    # Step 2: 筛选 EntryType 等于 3 的数据，这个是重量数据
    entry_type_3 = spc[spc['EntryType'] == 3]
 
    # Step 3: MAPPING 长宽
    def find_corresponding_length_width(row, df):
        # 1分钟内的条件，并且 Load 和 Item 一致
        condition_1min = (
            (df['DataTime'] > row['DataTime']) &
            (df['DataTime'] <= row['DataTime'] + pd.Timedelta(minutes=1)) &
            (df['EntryType'] == 2) &
            (df['Load'] == row['Load']) & 
            (df['Item'] == row['Item'])
        )
        corresponding_row_1min = df[condition_1min]
        
        if not corresponding_row_1min.empty:
            # 取找到的第一个对应的行
            corresponding_row = corresponding_row_1min.iloc[0]
        else:
            # 如果1分钟内没有找到，查找3分钟内的最近一条数据，Load 和 ID 也必须一致
            condition_3min = (
                (df['DataTime'] > row['DataTime']) &
                (df['DataTime'] <= row['DataTime'] + pd.Timedelta(minutes=3)) &
                (df['EntryType'] == 2) &
                (df['Load'] == row['Load']) & 
                (df['Item'] == row['Item'])
            )
            corresponding_row_3min = df[condition_3min]
            
            if not corresponding_row_3min.empty:
                # 取找到的最近一条对应的行
                corresponding_row = corresponding_row_3min.iloc[0]
            else:
                # 如果3分钟内也找不到，返回NA
                return pd.Series({
                    'DataTime': row['DataTime'],
                    'Load': row['Load'],
                    'Item': row['Item'],
                    'Weight': row['Weight'],
                    'LengthOrThickness': 'NA',
                    'WidthOrDepth': 'NA',
                    'DataTime2': 'NA'
                })
        
        return pd.Series({
            'DataTime': row['DataTime'],
            'Load': row['Load'],
            'Item': row['Item'],
            'Weight': row['Weight'],  # EntryType == 3 的 Actual 值作为 Weight
            'LengthOrThickness': corresponding_row['LengthOrThickness'],
            'WidthOrDepth': corresponding_row['WidthOrDepth'],
            'DataTime2': corresponding_row['DataTime']  # 对应找到的行的时间
        })

    result3 = entry_type_3.apply(lambda row: find_corresponding_length_width(row, spc), axis=1)
    
    # 首先确保 DataTime 和 DataTime2 都是 datetime 类型
    result3['DataTime'] = pd.to_datetime(result3['DataTime'])
    result3['DataTime2'] = pd.to_datetime(result3['DataTime2'], errors='coerce')  # 遇到 'NA' 会处理为 NaT (Not a Time)

    # 增加一列：计算时间差 （optional）
    result3['TimeDiff'] = result3['DataTime2'] - result3['DataTime']
    spc = result3

    # 根据Item的首字母判断是否含有糖
    spc['Sugar'] = np.where(spc['Item'].str[0].isin(['D', 'W', 'R']), 'Sugar', 'Sugarfree')

    # Step 4: Parm Dataset
    curated_parm['TS'] = pd.to_datetime(curated_parm['TS'], format="%Y-%m-%d %H:%M:%S", utc=True).dt.tz_localize(None)
    parm = curated_parm.dropna(subset=['TS'])

    # 需要的列名列表
    required_columns = [
        "TS",
        "SFBMix.plcSFBMix.dbAdditionalParameter.StateFromSheeting.bMachineRunning",
        "CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap3rdSizing.rActualPosition_inches",
        "CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap2ndSizing.rActualPosition_inches",
        "CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap1stSizing.rActualPosition_inches",
        "CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_GapFinalSizing.rActualPosition_inches",
        "CG_Sheeting.CG_Sheeting.dbHMI.Scoring.SRV_CrossScore.rSetpoint_Ratio",
        "CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rChillerSetpoint",
        "CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum1InletTemp",
        "CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum2InletTemp",
        "CG_Sheeting.CG_Sheeting.Variables.rGumExtruderExitGumTemp",
        "SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_UB_Temp_SP",
        "SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_LB_Temp_SP"
    ]
    para = parm.copy()
    # 将 Tag 为 "SFBMix.plcSFBMix.dbAdditionalParameter.StateFromSheeting.bMachineRunning" 的 Value 列中的 True 和 False 修改为 1 和 0
    para.loc[para['Tag'] == "SFBMix.plcSFBMix.dbAdditionalParameter.StateFromSheeting.bMachineRunning", 'Value'] = \
        para.loc[para['Tag'] == "SFBMix.plcSFBMix.dbAdditionalParameter.StateFromSheeting.bMachineRunning", 'Value'].apply(lambda x: 1 if x == 'True' else 0)
    
    # 筛选出 Tag 列中在 required_columns 中的元素
    filtered_para = para[para['Tag'].isin(required_columns[1:])]  # required_columns[1:] 是除去 'TS' 的其他列

  # 行转列
    # 由于会出现一样的TS导致出现error，我们需要在pivot之前detect到重复
    def process_data_before_pivot(filtered_para):
        try:
            # Step 1: 尝试执行 pivot 操作
            para_pivoted = filtered_para.pivot(index='TS', columns='Tag', values='Value').reset_index()
            return para_pivoted
        except:
            # Step 2: 如果出现任何错误，删除 TS 和 Tag 列的重复组合，保留第一个出现的组合
            filtered_para = filtered_para.drop_duplicates(subset=['TS', 'Tag'], keep='first')
        
            try:
                # Step 3: 再次尝试执行 pivot 操作
                para_pivoted = filtered_para.pivot(index='TS', columns='Tag', values='Value').reset_index()
                return para_pivoted
            except:
                # Step 4: 如果再次失败，对 TS 列进行去重，保留前面那行
                filtered_para = filtered_para.drop_duplicates(subset='TS', keep='first')
                
                # 最终再次尝试 pivot 操作
                para_pivoted = filtered_para.pivot(index='TS', columns='Tag', values='Value').reset_index()
                return para_pivoted

    # 执行处理
    para_pivoted = process_data_before_pivot(filtered_para)

    # 遍历 required_columns 列表，检查 df 中是否存在这些列
    for col in required_columns:
        if col not in para_pivoted.columns:
            # 如果 df 中不存在某列，则添加该列并填充 NaN（或其他默认值）
            para_pivoted[col] = np.nan  # 你可以根据需要替换 np.nan 为其他默认值
    para = para_pivoted

    # 选择列并按顺序排列
    para_pivoted = para_pivoted[['TS'] + required_columns[1:]]

    # 由于在参数不调整的时候没有记录，在表格中会展示NAN，我们将有数值的中间填写相关数据
    para_pivoted.fillna(method='ffill', inplace=True)
    para = para_pivoted
    latest_dict = para.sort_values(by='TS', ascending=False).iloc[0].to_dict()

    # 遍历字典，将可转换为浮点数的字符串转换为浮点数
    for key, value in latest_dict.items():
        if isinstance(value, str):
            try:latest_dict[key] = float(value)
            except ValueError:
                continue

    para['TS'] = pd.to_datetime(para['TS']) + pd.Timedelta(minutes=1)

    # 将 TS 列重命名为 Date
    para.rename(columns={'TS': 'DataTime'}, inplace=True)

    merge = pd.merge_asof(spc.sort_values('DataTime'),
                          para.sort_values('DataTime'), 
                          on='DataTime', direction='backward')
    
    merge['Prev_Weight'] = merge['Weight'].shift(1)

    def calculate_avg_weight(df, minutes_back, col):
        if df[col].isna().all():
            return df[col]  # 如果全是空值，返回原列
        # 使用 DataFrame 而不是 Series 进行 rolling 操作
        return df.rolling(f'{minutes_back}T', on='DataTime', closed='left', min_periods=1)[col].mean()
    
    # 对每个列进行检查并计算滚动平均值
    merge['Avg_Weight_5min'] = calculate_avg_weight(merge, 5, 'Weight')
    merge['Avg_Weight_15min'] = calculate_avg_weight(merge, 15, 'Weight')
    merge['Avg_Weight_30min'] = calculate_avg_weight(merge, 30, 'Weight')

    for col in required_columns[2:]:
        merge[f'Prev_{col}'] = merge[col].shift(1)
    
    # 构建固定的列表
    base_columns = ['DataTime','TimeDiff',
                    'Load', 'Item', 'Sugar',
                     'LengthOrThickness', 'WidthOrDepth', 'Weight',
                    'Prev_Weight', 'Avg_Weight_5min', 'Avg_Weight_15min', 'Avg_Weight_30min']

    # 动态生成要选择的列，确保选择的列存在于 merge 中
    dynamic_columns = [col for pair in zip(required_columns, [f'Prev_{col}' for col in required_columns])
                       for col in pair if col in merge.columns]

    # 合并固定列和动态生成的列
    selected_columns = base_columns + dynamic_columns

    # 选择存在的列，不会因缺少某些列而报错
    merge = merge[selected_columns]

    # 确保merge里面所有列都尽可能是float格式，定义一个函数，将字符串转换为浮点
    def convert_to_float(value):
        if isinstance(value, str):  # 检查是否是字符串
            try:
                return float(value)
            except ValueError:
                return value  # 保留原值（如果无法转换）
        return value  # 如果不是字符串，保持原值

    # 使用 applymap 方法应用函数到整个 DataFrame
    merge = merge.applymap(convert_to_float)

    # 返回结果
    return merge, latest_dict, spc_0.to_dict(), spc_1.to_dict(), spc_2.to_dict()


def process_etl_data(now,
                     parm,
                     spc,
                     prev_merge,
                     merge_OT_SPC=None,
                     output_file="merge_final_py2.csv"):

    # 转化时间格式为没有时区信息的 pandas.Timestamp 对象
    parm['TS'] = pd.to_datetime(parm['TS'], format="%Y-%m-%d %H:%M:%S", utc=True).dt.tz_localize(None)
    #spc['DataTime'] = pd.to_datetime(spc['DataTime'], format="%Y-%m-%d %H:%M:%S", utc=True).dt.tz_localize(None)
    prev_merge['DataTime'] = pd.to_datetime(prev_merge['DataTime'], format="%Y-%m-%d %H:%M:%S", utc=True).dt.tz_localize(None)

    # 删除 parm 中 TS 列为空值的行
    parm = parm.dropna(subset=['TS'])

    # Step 2: 直接进行合并，获取 merge 和 merge_latest_dict
    merge_new, merge_latest_dict, spc_0, spc_1, spc_2 = merge_OT_SPC(parm, spc)

    time_needed = [
         # 'TS', 'SFBMix.plcSFBMix.dbAdditionalParameter.StateFromSheeting.bMachineRunning',
         'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap3rdSizing.rActualPosition_inches',
         'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap2ndSizing.rActualPosition_inches',
         'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap1stSizing.rActualPosition_inches',
         'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_GapFinalSizing.rActualPosition_inches',
         'CG_Sheeting.CG_Sheeting.dbHMI.Scoring.SRV_CrossScore.rSetpoint_Ratio',
         'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rChillerSetpoint',
         'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum1InletTemp',
         'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum2InletTemp',
         'CG_Sheeting.CG_Sheeting.Variables.rGumExtruderExitGumTemp',
         'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_UB_Temp_SP',
         'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_LB_Temp_SP'
    ]

    df_required_tags = pd.DataFrame.from_dict({
        'Tag': time_needed
        # 'Value': [merge_latest_dict[t] for t in list(merge_latest_dict.keys()) if t != 'TS']
    })
    df_update_time = pd.merge(parm, df_required_tags, how='inner', on=['Tag'])
    df_update_time['Value'] = df_update_time['Value'].astype('float64')
    df_update_time = df_update_time.sort_values(by=['Tag', 'Value', 'TS'], ascending=True).reset_index(drop=True)
    df_update_time['Last_Value'] = df_update_time['Value'].shift(1)
    df_update_time['Last_Tag'] = df_update_time['Tag'].shift(1)
    df_update_time = df_update_time[
        (df_update_time['Tag'] != df_update_time['Last_Tag']) | (df_update_time['Value'] != df_update_time['Last_Value'])
    ]
    update_time_dict = df_update_time.groupby('Tag').agg({'TS': np.min}).to_dict(orient='index')

    # # Step 3: 筛选数据，去掉既不是最近30分钟又不是最近10次的数据
    # recent_30min = now - timedelta(minutes=30)

    # 生成 dictionary {列名：当前值}
    latest_dict = merge_new.sort_values(by='DataTime', ascending=False).iloc[0].to_dict()
    for key, value in latest_dict.items():
        if isinstance(value, str):
            try:latest_dict[key] = float(value)
            except ValueError:
                continue

    # 输出两个latest_dict进行对比
    # print("Merge Latest Dict:")
    # print(merge_latest_dict)
    #
    # print("\nProcess ETL Data Latest Dict:")
    # print(latest_dict)
    #
    # print("\n Spc_0 Data Dict:")
    # print(spc_0)
    #
    # print("\n Spc_1 Data Dict:")
    # print(spc_1)
    #
    # print("\n Spc_2 Data Dict:")
    # print(spc_2)

    # 返回 merge_latest_dict 和 latest_dict
    return merge_new, merge_latest_dict, spc_0, spc_1, spc_2, update_time_dict
