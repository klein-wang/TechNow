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
    # test
    # curated_parm = parm
    # curated_spc = spc

    # Step 1: 处理 spc 数据
    spc = curated_spc[['DataTime', 'Item', 'Load', 'Actual']].copy()
    spc.rename(columns={'Actual': 'Weight'}, inplace=True)

    # 根据Item的首字母判断是否含有糖
    spc['Sugar'] = np.where(spc['Item'].str[0].isin(['D', 'W', 'R']), 'Sugar', 'Sugarfree')

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
        "CG_Sheeting.CG_Sheeting.Variables.rGumExtruderExitGumTemp"
    ]

    # Step 2: 处理 para 数据
    para = curated_parm.copy()
    #   para.rename(columns={'TS': 'Date'}, inplace=True)
    # 行转列

    para = para.pivot_table(index='TS', columns='Tag', values='Value', aggfunc='mean').reset_index()

    # 确保所有必需的列都存在，缺失的列用 NA 填充
    for col in required_columns:
        if col not in para.columns:
            para[col] = np.nan

    # 选择列并按顺序排列
    para = para[required_columns]
    para.fillna(method='ffill', inplace=True)

    # later delet this: just to fill the NA
    # para.fillna(method='bfill', inplace=True)
    para['TS'] = pd.to_datetime(para['TS']) + timedelta(minutes=1)
    # 将 TS 列重命名为 Date
    para.rename(columns={'TS': 'DataTime'}, inplace=True)

    # 提取最新一条记录
    # latest_dict = para.iloc[-1, 2:].to_dict()
    latest_dict = para.iloc[-1].to_dict()

    # Step 3: 进行数据合并与计算
    # 当在 spc 数据框中找到一个 Date 值时，它会在 para 数据框中查找等于或早于该 Date 值的最近一行进行匹配。
    # 因此，如果 spc 中某个 Date 的值在 para 中找不到完全相同的 Date，则会回退到最接近但早于它的那个 Date 进行匹配。
    merge = pd.merge_asof(spc.sort_values('DataTime'),
                          para.sort_values('DataTime'),
                          on='DataTime',
                          direction='backward')

    merge['Prev_Weight'] = merge['Weight'].shift(1)

    # 计算过去 5, 15 和 30 分钟的均值，不包含当前重量
    # closed='left'：指定窗口左闭右开，这意味着在计算滚动平均值时，窗口会排除当前记录的值，只考虑当前记录之前的值。
    # df[col] 是一个 Series 对象，而不是一个 DataFrame，因此它无法识别 on='DataTime' 选项。
    # 在 DataFrame 上调用 rolling，而不是在 Series 上调用。
    def calculate_avg_weight(df, minutes_back, col):
        if df[col].isna().all():
            return df[col]  # 如果全是空值，返回原列
        # 使用 DataFrame 而不是 Series 进行 rolling 操作
        return df.rolling(f'{minutes_back}T', on='DataTime', closed='left', min_periods=1)[col].mean()

    # 示例：对每个列进行检查并计算滚动平均值
    merge['Avg_Weight_5min'] = calculate_avg_weight(merge, 5, 'Weight')
    merge['Avg_Weight_15min'] = calculate_avg_weight(merge, 15, 'Weight')
    merge['Avg_Weight_30min'] = calculate_avg_weight(merge, 30, 'Weight')

    # 仅处理 key_columns 中除了前两个元素以外的所有列
    for col in required_columns[2:]:
        merge[f'Prev_{col}'] = merge[col].shift(1)

    # 按照指定顺序重新排列列
    # merge 数据框中的列会按照以下顺序排列：
    # 固定顺序的列（Date, Load, Item, Sugar, Weight, Prev_Weight, Avg_Weight_5min, Avg_Weight_15min, Avg_Weight_30min）。
    # 动态生成的列，这些列以原列名和对应的 Prev_ 前缀列名成对排列。

    # merge = merge[['DataTime', 'Load', 'Item', 'Sugar',
    #               'Weight', 'Prev_Weight', 'Avg_Weight_5min', 'Avg_Weight_15min', 'Avg_Weight_30min'] +
    #             [col for pair in zip(key_columns, [f'Prev_{col}' for col in key_columns]) for col in pair]]

    # 构建固定的列列表
    base_columns = ['DataTime', 'Load', 'Item', 'Sugar',
                    'Weight', 'Prev_Weight', 'Avg_Weight_5min', 'Avg_Weight_15min', 'Avg_Weight_30min']

    # 动态生成要选择的列，确保选择的列存在于 merge 中
    dynamic_columns = [col for pair in zip(required_columns, [f'Prev_{col}' for col in required_columns])
                       for col in pair if col in merge.columns]

    # 合并固定列和动态生成的列
    selected_columns = base_columns + dynamic_columns

    # 选择存在的列，不会因缺少某些列而报错
    merge = merge[selected_columns]

    # 返回结果
    return merge, latest_dict


def process_etl_data(now,
                     parm,
                     spc,
                     prev_merge,
                     merge_OT_SPC=None,
                     output_file="merge_final_py2.csv"):
    # Step 1: 读取当前ETL生成的15秒的数据 + 上一个合并文件
    # parm = pd.read_csv(parm_file)
    # spc = pd.read_csv(spc_file)
    # prev_merge = pd.read_csv(prev_merge_file)

    # 转化时间格式为没有时区信息的 pandas.Timestamp 对象
    parm['TS'] = pd.to_datetime(parm['TS'], format="%Y-%m-%d %H:%M:%S", utc=True).dt.tz_localize(None)
    spc['DataTime'] = pd.to_datetime(spc['DataTime'], format="%Y-%m-%d %H:%M:%S", utc=True).dt.tz_localize(None)
    prev_merge['DataTime'] = pd.to_datetime(prev_merge['DataTime'], format="%Y-%m-%d %H:%M:%S",
                                            utc=True).dt.tz_localize(None)

    # 删除 parm 中 TS 列为空值的行
    parm = parm.dropna(subset=['TS'])

    # Step 2: 直接进行合并，获取 merge 和 merge_latest_dict
    merge_new, merge_latest_dict = merge_OT_SPC(parm, spc)

    # Step 3: 筛选数据，去掉既不是最近30分钟又不是最近10次的数据
    recent_30min = now - timedelta(minutes=30)

    # 保留最近30分钟的数据
    merge_recent_30min = merge_new[merge_new['DataTime'] >= recent_30min]

    # 保留最近10次的记录
    merge_recent_10 = merge_new.tail(10)

    # 选择两者中的较大集合：去掉既不是最近30分钟又不是最近10次的数据作为当前15秒的merge结果
    if len(merge_recent_30min) >= len(merge_recent_10):
        merge_final = merge_recent_30min
    else:
        merge_final = merge_recent_10

    # 保存 merge_final 到 output_file
    if output_file:
        merge_final.to_csv(output_file, index=False)

    # Step 5: 获取最新一条数据（离当前时间最近的一条）
    latest_data = merge_final.sort_values(by='DataTime', ascending=False).iloc[0]

    # 生成 dictionary {列名：当前值}
    latest_dict = latest_data.to_dict()

    # 输出两个latest_dict进行对比
    print("Merge Latest Dict:")
    print(merge_latest_dict)

    print("\nProcess ETL Data Latest Dict:")
    print(latest_dict)

    # 返回 merge_latest_dict 和 latest_dict
    return merge_final, merge_latest_dict