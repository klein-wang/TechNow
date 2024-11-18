import pandas as pd
import numpy as np
import joblib
import json
from ortools.linear_solver import pywraplp
import sys
import string
import pytz
import json
import datetime
from azure.storage.blob import BlobServiceClient, BlobClient
import io
import os
import configparser
import warnings
import edge_blob
import data_mapping
import db_service
from db_factory import SpcDBFactory
from config import SpcDBPoolConfig


def fit_range(x, lb, ub):
    if x < lb:
        return lb
    elif x > ub:
        return ub
    return x


# def single_factor_change(initial_weight, target_weight, initial_x, k, lb, ub):
#     delta = (target_weight - initial_weight) / k
#     new_x = fit_range(initial_x + delta, lb, ub)
#     new_weight = initial_weight + (new_x - initial_x) * k
#     return new_x, new_weight


def datetime_to_list(x):
    return [int(x.year), int(x.month), int(x.day), int(x.hour), int(x.minute), int(x.second)]


def constrained_optimization(thresholds, weight_prediction, current_data, service_level=1):

    # Set four decision variables, Drum 1, Drum 2, Drum 3, Final Sizing Drum
    DV = ['Gap1', 'Gap2', 'Gap3', 'GapFS']

    solver = pywraplp.Solver.CreateSolver('SCIP')
    bigM = 10 ** 10
    infinity = solver.infinity()

    # Decision Variables
    # Set upper and lower bound for gap of four drums to be set
    DV_factor_values = {
        x: solver.NumVar(
            thresholds[x]['lb'], thresholds[x]['ub'], '''Suggested_Value_%s''' % (x)
        ) for x in DV
    }
    DV_factor_is_change = {
        x: solver.IntVar(
            0, 1, '''Is_Change_%s''' % (x)
        ) for x in DV
    }

    # Predicted weight if we make changes on drum gaps
    weight_after_change = weight_prediction + \
                          K_Gap1 * (DV_factor_values['Gap1'] - current_data['Gap1']) + \
                          K_Gap2 * (DV_factor_values['Gap2'] - current_data['Gap2']) + \
                          K_Gap3 * (DV_factor_values['Gap3'] - current_data['Gap3']) + \
                          K_GapFS * (DV_factor_values['GapFS'] - current_data['GapFS'])

    # 1st Priority Objective =
    #   ABS(weight after change - target weight)
    final_weight_gap = weight_after_change - Target_Weight
    OBJ_abs_weight_gap = solver.NumVar(0, 100, 'OBJ_weight_gap')

    # 2nd Priority Objective =
    #   ABS(weight difference change between drum 1 and drum 2)
    #   + ABS(weight difference change between drum 2 and drum 3)
    #   + ABS(weight difference change between drum 3 and final sizing drum)
    diff_1_2_before = current_data['Gap1'] - current_data['Gap2']
    diff_1_2_after = DV_factor_values['Gap1'] - DV_factor_values['Gap2']
    diff_2_3_before = current_data['Gap2'] - current_data['Gap3']
    diff_2_3_after = DV_factor_values['Gap2'] - DV_factor_values['Gap3']
    diff_3_FS_before = current_data['Gap3'] - current_data['GapFS']
    diff_3_FS_after = DV_factor_values['Gap3'] - DV_factor_values['GapFS']
    abs_1_2_diff_change = solver.NumVar(0, 0.1, '1_2_diff_change')
    abs_2_3_diff_change = solver.NumVar(0, 0.1, '2_3_diff_change')
    abs_3_FS_diff_change = solver.NumVar(0, 0.1, '3_FS_diff_change')

    # Objective Function
    solver.Minimize(OBJ_abs_weight_gap + 0.01 * (2 * abs_1_2_diff_change + abs_2_3_diff_change + abs_3_FS_diff_change))

    # Constraints

    # Change limit is 0.003
    solver.Add(DV_factor_values['Gap1'] - current_data['Gap1'] >= -0.001)
    solver.Add(DV_factor_values['Gap1'] - current_data['Gap1'] <= 0.001)
    solver.Add(DV_factor_values['Gap2'] - current_data['Gap2'] >= -0.001)
    solver.Add(DV_factor_values['Gap2'] - current_data['Gap2'] <= 0.001)
    solver.Add(DV_factor_values['Gap3'] - current_data['Gap3'] >= -0.001)
    solver.Add(DV_factor_values['Gap3'] - current_data['Gap3'] <= 0.001)
    solver.Add(DV_factor_values['GapFS'] - current_data['GapFS'] >= -0.001)
    solver.Add(DV_factor_values['GapFS'] - current_data['GapFS'] <= 0.001)

    # Math needed to turn an ABS function into an integer linear programing one. So it can solve much quicker.
    solver.Add(OBJ_abs_weight_gap >= final_weight_gap)
    solver.Add(OBJ_abs_weight_gap >= (-1) * final_weight_gap)
    solver.Add(abs_1_2_diff_change >= diff_1_2_before - diff_1_2_after)
    solver.Add(abs_1_2_diff_change >= diff_1_2_after - diff_1_2_before)
    solver.Add(abs_2_3_diff_change >= diff_2_3_before - diff_2_3_after)
    solver.Add(abs_2_3_diff_change >= diff_2_3_after - diff_2_3_before)
    solver.Add(abs_3_FS_diff_change >= diff_3_FS_before - diff_3_FS_after)
    solver.Add(abs_3_FS_diff_change >= diff_3_FS_after - diff_3_FS_before)

    # Good Manufacturing Practice
    if service_level == 1:
        if (weight_prediction > Control_UB and weight_prediction - Control_UB <= 0.15) \
                or (weight_prediction < Control_LB and Control_LB - weight_prediction <= 0.15):
            solver.Add(DV_factor_values['Gap1'] - current_data['Gap1'] == 0)
            solver.Add(DV_factor_values['Gap2'] - current_data['Gap2'] == 0)
            # None

    status = solver.Solve()
    if status == pywraplp.Solver.OPTIMAL:
        return DV_factor_values['Gap1'].solution_value(), DV_factor_values['Gap2'].solution_value(),\
            DV_factor_values['Gap3'].solution_value(),DV_factor_values['GapFS'].solution_value(), \
            weight_after_change.solution_value(), True
    else:
        return current_data['Gap1'], current_data['Gap2'], current_data['Gap3'], current_data['GapFS'], \
            weight_prediction, False

#
# def multi_factors_change(initial_weight, dic_initial_x, dic_k, dic_lb, dic_ub):
#
#     solver = pywraplp.Solver.CreateSolver('SCIP')
#     bigM = 10 ** 10
#     infinity = solver.infinity()
#
#     DV_factor_changes = {
#         x: solver.IntVar(0, 1, '''Is_Change_%s''' % (x)) for x in dic_initial_x
#     }
#     DV_factor_values = {
#         x: solver.NumVar(
#             np.min([dic_lb[x], dic_initial_x[x]]),
#             np.max([dic_ub[x], dic_initial_x[x]]),
#             '''Suggested_Value_%s''' % (x)
#         ) for x in dic_initial_x
#     }
#
#     weight_after_change = initial_weight + np.sum([
#         (DV_factor_values[x] - dic_initial_x[x]) * dic_k[x] for x in dic_initial_x
#     ])
#     OBJ_count_changed_factors = np.sum([
#         DV_factor_changes[x] for x in dic_initial_x
#     ])
#     final_weight_gap = weight_after_change - Target_Weight
#     OBJ_abs_weight_gap = solver.NumVar(0, 100, 'OBJ_weight_gap')
#     solver.Minimize(OBJ_abs_weight_gap + 0.001 * OBJ_count_changed_factors)
#     solver.Add(OBJ_abs_weight_gap >= final_weight_gap)
#     solver.Add(OBJ_abs_weight_gap >= (-1) * final_weight_gap)
#
#     # DV_factor_changes[x]越小越好，这里自带一个趋势
#     for x in dic_initial_x:
#         solver.Add(bigM * (DV_factor_changes[x]) >= DV_factor_values[x] - dic_initial_x[x])
#         solver.Add(bigM * (DV_factor_changes[x]) >= dic_initial_x[x] - DV_factor_values[x])
#
#     status = solver.Solve()
#
#     if status == pywraplp.Solver.OPTIMAL:
#         return {
#             x: DV_factor_changes[x].solution_value() for x in DV_factor_changes
#         }, {
#             x: DV_factor_values[x].solution_value() for x in DV_factor_values
#         }, weight_after_change.solution_value()
#     else:
#         return {x: 0 for x in DV_factor_changes}, dic_initial_x, initial_weight


def map_data():

    file_path_now = input_data['filePath']
    merge_file_path = ''

    df_prev_merge_empty = pd.DataFrame.from_dict({
            x: [] for x in [
                'DataTime', 'Load', 'Item', 'Sugar', 'Weight', 'Prev_Weight',
                'Avg_Weight_5min', 'Avg_Weight_15min', 'Avg_Weight_30min',
                'SFBMix.plcSFBMix.dbAdditionalParameter.StateFromSheeting.bMachineRunning',
                'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap3rdSizing.rActualPosition_inches',
                'Prev_CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap3rdSizing.rActualPosition_inches',
                'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap2ndSizing.rActualPosition_inches',
                'Prev_CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap2ndSizing.rActualPosition_inches',
                'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap1stSizing.rActualPosition_inches',
                'Prev_CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap1stSizing.rActualPosition_inches',
                'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_GapFinalSizing.rActualPosition_inches',
                'Prev_CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_GapFinalSizing.rActualPosition_inches',
                'CG_Sheeting.CG_Sheeting.dbHMI.Scoring.SRV_CrossScore.rSetpoint_Ratio',
                'Prev_CG_Sheeting.CG_Sheeting.dbHMI.Scoring.SRV_CrossScore.rSetpoint_Ratio',
                'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rChillerSetpoint',
                'Prev_CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rChillerSetpoint',
                'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum1InletTemp',
                'Prev_CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum1InletTemp',
                'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum2InletTemp',
                'Prev_CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum2InletTemp',
                'CG_Sheeting.CG_Sheeting.Variables.rGumExtruderExitGumTemp',
                'Prev_CG_Sheeting.CG_Sheeting.Variables.rGumExtruderExitGumTemp',
                'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_LB_Temp_SP',
                'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_UB_Temp_SP',
                'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_LB_Temp_RealValue',
                'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_LB_Temp_RealValue'
            ]
        })


    if Connection_Method == 'Azure':

        Blob_Target = edge_blob.AzureBlobStorage(connection_string=edge_blob.BlobConfig.target_conn_str)
        merge_file_path = input_data['filePath'] + 'merge.csv'
        curated_file_path = input_data['filePath'] + 'curated_parm.csv'
        blob_data = Blob_Target.download_blob(edge_blob.BlobConfig.target_container_name,
                                              curated_file_path)
        df_curated_data = pd.read_csv(io.BytesIO(blob_data))
        # df_spc_data = db_service.get_spc_data(T, 'YNG_SPC_TReceive', 'YNG_SPC_TItem')
        # df_spc_data = pd.read_csv(input_data['filePath'] + 'curated_spc.csv')
        file_path_last = input_data['filePath'][:7] + (
                datetime.datetime.strptime(input_data['filePath'][7:], '%Y/%m/%d/%H/%M/%S/') - datetime.timedelta(seconds=15)
            ).strftime('%Y/%m/%d/%H/%M/%S/')
        try:
            df_prev_merge = pd.read_csv(file_path_last + 'merge.csv')
        except:
            df_prev_merge = df_prev_merge_empty
        try:
            blob_data = Blob_Target.download_blob(edge_blob.BlobConfig.target_container_name,
                                                  file_path_last + 'curated_spc_data.csv')
            df_last_spc = pd.read_csv(io.BytesIO(blob_data))
            df_spc_data = db_service.get_spc_data(
                now=T, spc_table_name='YNG_SPC_TReceive', item_table_name='YNG_SPC_TItem', initialization=False,
                df_last_spc=df_last_spc
            )
        except:
            df_spc_data = db_service.get_spc_data(
                now=T, spc_table_name='YNG_SPC_TReceive', item_table_name='YNG_SPC_TItem'
            )
        Blob_Target.upload_blob(edge_blob.BlobConfig.target_container_name, input_data['filePath'] + 'curated_spc_data.csv',
                                df_spc_data.to_csv(index=False).encode('utf-8'))

    else:
        df_curated_data = edge_blob.read_csv_blob_to_dataframe(input_data['filePath'] + 'curated_parm.csv')
        #df_spc_data = edge_blob.read_csv_blob_to_dataframe(input_data['filePath'] + 'curated_spc.csv')
        #从spc 数据库获取spc data
        # df_spc_data = db_service.get_spc_data(T)
        file_path_last = (
                datetime.datetime.strptime(input_data['filePath'], '%Y/%m/%d/%H/%M/%S/') - datetime.timedelta(seconds=15)
            ).strftime('%Y/%m/%d/%H/%M/%S/')
        try:
            df_prev_merge = edge_blob.read_csv_blob_to_dataframe(file_path_last + 'merge.csv')
            if df_prev_merge.empty:
               df_prev_merge = df_prev_merge_empty
        except:
            df_prev_merge = df_prev_merge_empty
        try:
            df_last_spc = edge_blob.read_csv_blob_to_dataframe(file_path_last + 'curated_spc_data.csv')
            df_spc_data = db_service.get_spc_data(now=T, initialization=False, df_last_spc=df_last_spc)
        except:
            df_spc_data = db_service.get_spc_data(now=T)
        edge_blob.save_dataframe_to_csv_blob(input_data['filePath'] + 'curated_spc_data.csv', df_spc_data)


    # df_mapping, current_data = data_mapping.merge_data(df_curated_data, df_spc_data, df_prev_merge)

    df_mapping, current_data, df_weight, df_thickness_depth, df_legnth_width, update_time_dict = \
        data_mapping.process_etl_data(
            now=T,
            parm=df_curated_data,
            spc=df_spc_data,
            prev_merge=df_prev_merge,
            merge_OT_SPC=data_mapping.merge_OT_SPC,
            output_file=merge_file_path
        )

    if Connection_Method == 'Azure':
        Blob_Target.upload_blob(edge_blob.BlobConfig.target_container_name, input_data['filePath'] + 'merge.csv',
                                df_mapping.to_csv(index=False).encode('utf-8'))
    else:
        edge_blob.save_dataframe_to_csv_blob(input_data['filePath'] + 'merge.csv', df_mapping)

    name_mapping = {
        'DataTime': 'Date',
        'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap3rdSizing.rActualPosition_inches': 'Gap3',
        'Prev_CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap3rdSizing.rActualPosition_inches': 'Prev_Gap3',
        'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap2ndSizing.rActualPosition_inches': 'Gap2',
        'Prev_CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap2ndSizing.rActualPosition_inches': 'Prev_Gap2',
        'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap1stSizing.rActualPosition_inches': 'Gap1',
        'Prev_CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap1stSizing.rActualPosition_inches': 'Prev_Gap1',
        'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_GapFinalSizing.rActualPosition_inches': 'GapFS',
        'Prev_CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_GapFinalSizing.rActualPosition_inches': 'Prev_GapFS',
        'CG_Sheeting.CG_Sheeting.dbHMI.Scoring.SRV_CrossScore.rSetpoint_Ratio': 'CrossScore',
        'Prev_CG_Sheeting.CG_Sheeting.dbHMI.Scoring.SRV_CrossScore.rSetpoint_Ratio': 'Prev_CrossScore',
        'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rChillerSetpoint': 'TempChiller',
        'Prev_CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rChillerSetpoint': 'Prev_TempChiller',
        'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum1InletTemp': 'Temp1',
        'Prev_CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum1InletTemp': 'Prev_Temp1',
        'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum2InletTemp': 'Temp2',
        'Prev_CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum2InletTemp': 'Prev_Temp2',
        'CG_Sheeting.CG_Sheeting.Variables.rGumExtruderExitGumTemp': 'TempExtruder',
        'Prev_CG_Sheeting.CG_Sheeting.Variables.rGumExtruderExitGumTemp': 'Prev_TempExtruder',
        'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_LB_Temp_SP': 'TempLowerSetValue',
        'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_UB_Temp_SP': 'TempUpperSetValue',
        'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_LB_Temp_RealValue': 'TempLowerRealValue',
        'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_UB_Temp_RealValue': 'TempUpperRealValue'
    }

    df_mapping = df_mapping.rename(columns=name_mapping)

    fixed_keys = list(current_data.keys())
    for c in fixed_keys:
        if c in name_mapping:
            current_data[name_mapping[c]] = current_data[c]

    fixed_keys = list(update_time_dict.keys())
    for c in fixed_keys:
        if c in name_mapping:
            update_time_dict[name_mapping[c]] = update_time_dict[c]

    return df_mapping, current_data, df_weight, df_thickness_depth, df_legnth_width, update_time_dict

def predict_weight_now(df_mapping, current_data):

    df_mapping['Gap1_Influence'] = (current_data['Gap1'] - df_mapping['Gap1']) * K_Gap1
    df_mapping['Gap1_Influence'] = df_mapping['Gap1_Influence'].fillna(0)
    df_mapping['Gap2_Influence'] = (current_data['Gap2'] - df_mapping['Gap2']) * K_Gap2
    df_mapping['Gap2_Influence'] = df_mapping['Gap2_Influence'].fillna(0)
    df_mapping['Gap3_Influence'] = (current_data['Gap3'] - df_mapping['Gap3']) * K_Gap3
    df_mapping['Gap3_Influence'] = df_mapping['Gap3_Influence'].fillna(0)
    df_mapping['GapFS_Influence'] = (current_data['GapFS'] - df_mapping['GapFS']) * K_GapFS
    df_mapping['GapFS_Influence'] = df_mapping['GapFS_Influence'].fillna(0)
    df_mapping['Temp1_Influence'] = (current_data['Temp1'] - df_mapping['Temp1']) * K_Temp1
    df_mapping['Temp1_Influence'] = df_mapping['Temp1_Influence'].fillna(0)
    df_mapping['Temp2_Influence'] = (current_data['Temp2'] - df_mapping['Temp2']) * K_Temp1
    df_mapping['Temp2_Influence'] = df_mapping['Temp2_Influence'].fillna(0)

    df_mapping['Modified_Weight'] = df_mapping['Weight'] + df_mapping['Gap1_Influence'] + \
                                    df_mapping['Gap2_Influence'] + df_mapping['Gap3_Influence'] + \
                                    df_mapping['GapFS_Influence']

    df_mapping['Date'] = [pd.Timestamp(x) for x in df_mapping['Date']]
    df_mapping = df_mapping.sort_values(by='Date', ascending=False, ignore_index=True)

    dic_name_en_cn = {
        'FVPP': 'FVPP（FIVE激酷薄荷味-NCS）',
        'FVSS': 'FVSS（FIVE酷酸草莓味-NCS）',
        'FVWM': 'FVWM（FIVE奔涌西瓜-NCS）',
        'FVBB': 'FVBB（FIVE魅幻蓝莓-NCS）',
        'DMRC': 'DMRC（绿箭樱花薄荷）',
        'EXSM': 'EXSM（益达沁凉薄荷-NCS）',
        'DMPY': 'DMPY（绿箭金装薄荷）',
        'DMLM': 'DMLM（绿箭青柠薄荷）',
        'EXCW': 'EXCW（益达西瓜-NCS）',
        'EXTP': 'EXTP（益达热带水果-NCS）',
        'EBB': 'EBB（益达蓝莓-NCS）',
        'WSP': 'WSP（白箭留兰香薄荷）',
        'RPCM': 'RPCM（维能酷爽薄荷）',
        'AUWM': 'AUWM（澳洲FIVE奔涌西瓜味）',
        'DMRR': 'DMRR（真叶玫瑰薄荷）',
        'DMRJ': 'DMRJ（茉莉薄荷）',
        'EXPP': 'EXPP（益达冰凉薄荷味）',
        'DMPE': 'DMPE 绿箭原味薄荷',
        'RPSY': 'RPSY（维能劲爆麻辣）',
        'RPWP': 'RPWP（维能西瓜红石榴）',
        'DMLG': 'DMLG（柠檬草薄荷）',
        'DMRM': 'DMRM（真叶薄荷）'
    }

    if 'Name_CN' in Thresholds:
        name_cn = Thresholds['Name_CN']
    else:
        name_cn = dic_name_en_cn[SKU]

    df_mapping = df_mapping.sort_values(by='Date', ascending=False).reset_index(drop=True)
    if len(df_mapping) == 1:
        actual_weight = df_mapping['Weight'][0]
    elif len(df_mapping) > 1:
        i = 1
        while i <= len(df_mapping) - 1:
            if df_mapping['Date'][i] - df_mapping['Date'][i-1] > datetime.timedelta(seconds=30):
                break
            i += 1
        actual_weight = np.mean(df_mapping['Weight'][:i+1])
    else:
        actual_weight = Target_Weight

    # df_mapping = df_mapping[df_mapping['Item']==name_cn]
    df_mapping = df_mapping[df_mapping['Date'] >= ValidTimeStart]
    print(df_mapping[['Weight', 'Date']])

    print(df_mapping[['Weight', 'Modified_Weight', 'Date']])

    if len(df_mapping) > 0:
        w_prev = df_mapping['Weight'][0]
        mw_prev = df_mapping['Modified_Weight'][0]
    else:
        w_prev = 35.23
        mw_prev = 35.23
    t_end = datetime.datetime.strptime(input_data['fileLastTs'], "%Y-%m-%d %H:%M:%S")
    df_5 = df_mapping[df_mapping['Date'] >= t_end - datetime.timedelta(minutes=5)]
    df_15 = df_mapping[df_mapping['Date']>=t_end - datetime.timedelta(minutes=15)]
    df_30 = df_mapping[df_mapping['Date']>=t_end - datetime.timedelta(minutes=30)]
    if len(df_30) >= 1:
        w_30 = np.mean(df_30['Weight'])
        mw_30 = np.mean(df_30['Modified_Weight'])
    else:
        w_30 = w_prev
        mw_30 = mw_prev
    if len(df_15) >= 1:
        w_15 = np.mean(df_15['Weight'])
        mw_15 = np.mean(df_15['Modified_Weight'])
    else:
        w_15 = w_30
        mw_15 = mw_30
    if len(df_5) >= 1:
        w_5 = np.mean(df_5['Weight'])
        mw_5 = np.mean(df_5['Modified_Weight'])
    else:
        w_5 = w_15
        mw_5 = mw_15

    return 0.05 * mw_prev + 0.55 * mw_5 + 0.3 * mw_15 + 0.1 * mw_30, actual_weight


def get_current_sku(file_path_last, Connection_Method):

    if Connection_Method == 'Azure':

        Blob_Target = edge_blob.AzureBlobStorage(connection_string=edge_blob.BlobConfig.target_conn_str)
        blob_data = Blob_Target.download_blob(edge_blob.BlobConfig.target_container_name,
                                                  file_path_last + 'curated_spc_data.csv')
        df_last_spc = pd.read_csv(io.BytesIO(blob_data))

    else:
        df_last_spc = edge_blob.read_csv_blob_to_dataframe(file_path_last + 'curated_spc_data.csv')

    df_last_spc = df_last_spc.sort_values(by='DataTime', ascending=True).reset_index(drop=True)
    df_mapping = pd.read_csv('sku_mapping.csv')
    dic_mapping = {
        row['SKU_CN']: row['SKU'] for i, row in df_mapping.iterrows()
    }
    return dic_mapping[df_last_spc['Item'][0]]


def list_to_datetime(x):
    return datetime.datetime(x[0], x[1], x[2], x[3], x[4], x[5])


def run(input_str):

    global Target_Weight, df_mapping, input_data, current_data, K_GapFS, K_Gap3, K_Gap1, K_Gap2, K_Temp1, K_Temp2, T, \
        Connection_Method, Thresholds, SKU, ValidTimeStart, Control_UB, Control_LB

    input_data = json.loads(input_str)
    SKU = input_data['SKU']

    with open('sku_config.json', 'r') as f:
        config_dict = json.load(f)
    Thresholds = config_dict[SKU]

    Control_UB = Thresholds['Weight_UB']
    Control_LB = Thresholds['Weight_LB']
    Target_Weight = 0.5 * (Control_LB + Control_UB)
    ValidTimeStart = list_to_datetime(input_data['lastStartTime'])

    T = datetime.datetime(
        input_data['time'][0], input_data['time'][1], input_data['time'][2],
        input_data['time'][3], input_data['time'][4], input_data['time'][5]
    )
    Connection_Method = 'Edge'
    if 'connection' in input_data:
        if input_data['connection'] == 'Azure':
            Connection_Method = 'Azure'

    if Connection_Method == 'Azure':
        Blob_Target = edge_blob.AzureBlobStorage(connection_string=edge_blob.BlobConfig.target_conn_str)
        Blob_Target.upload_blob(edge_blob.BlobConfig.target_container_name, input_data['filePath'] + 'azure_input_data.json',
                                json.dumps(input_data))
    else:
        try:
            edge_blob.save_dict_to_blob_json(input_data['filePath'] + 'edge_input_data.json', input_data)
        except Exception as e:
            print (e)

    # Load Models
    Model_GapFS = joblib.load('Models/Forming Roller 定型辊间隙.joblib')
    K_GapFS = Model_GapFS.coef_[0]
    Model_Gap3 = joblib.load('Models/3号辊间隙.joblib')
    K_Gap3 = Model_Gap3.coef_[0]
    Model_Gap2 = joblib.load('Models/2号辊间隙.joblib')
    K_Gap2 = Model_Gap2.coef_[0]
    Model_Gap1 = joblib.load('Models/1号辊间隙.joblib')
    K_Gap1 = Model_Gap1.coef_[0]
    Model_Temp2 = joblib.load('Models/2号冷辊入口温度.joblib')
    K_Temp2 = Model_Temp2.coef_[0]
    Model_Temp1 = joblib.load('Models/1号冷辊入口温度.joblib')
    K_Temp1 = Model_Temp1.coef_[0]

    dic_lb_ub = {
        'Gap1': {'ub': Thresholds['Gap1_UB'], 'lb': Thresholds['Gap1_LB']},
        'Gap2': {'ub': Thresholds['Gap2_UB'], 'lb': Thresholds['Gap2_LB']},
        'Gap3': {'ub': Thresholds['Gap3_UB'], 'lb': Thresholds['Gap3_LB']},
        'GapFS': {'ub': Thresholds['GapFS_UB'], 'lb': Thresholds['GapFS_LB']},
        'Temp1': {'ub': -10.0, 'lb': -15.0},
        'Temp2': {'ub': -10.0, 'lb': -15.0},
        'TempExtruder': {'ub': 70, 'lb': 45},
        'CrossScore': {'ub': Thresholds['CS_UB'], 'lb': Thresholds['CS_LB']}
    }

    azure_config = {
        'SPC_DB_SERVER': 'dev-ce2-iot-core-sql.database.chinacloudapi.cn',
        'SPC_DB_PORT': 1433,
        'SPC_DB_DATABASE': 'dev-ce2-iot-core-mgmtengine-sqldb',
        'SPC_DB_USERNAME': 'whi',
        'SPC_DB_PASSWORD': 'jxg-ml5@dga'
    }
    edge_config = {
        'SPC_DB_SERVER': '10.157.85.236',
        'SPC_DB_PORT': 1434,
        'SPC_DB_DATABASE': 'spc-datadb',
        'SPC_DB_USERNAME': 'spc_datauser',
        'SPC_DB_PASSWORD': 'Accenture@2024'
    }

    # 3 初始化相关配置文件
    if Connection_Method == 'Azure':
        SpcDBPoolConfig.init(azure_config)
    else:
        SpcDBPoolConfig.init(edge_config)

    # 4. 初始化db2连接池资源
    SpcDBFactory.init_pool(SpcDBPoolConfig)

    df_mapping, current_data, dic_weight, dic_thickness_depth, dic_length_width, last_change_time = map_data()
    weight_prediction, actual_weight = predict_weight_now(df_mapping, current_data)
    print(weight_prediction)

    Suggestion_Dict = {
        'code': 200, # 这期都是200，因为异常工况在YNG是放在后端的
        'human_takeover': False, # 是否需要人工接管
        'is_change': False, # 是否需要调整
        'Gap1': current_data['Gap1'], # 1号辊推荐间隙
        'Gap1_is_change': False, # 1号辊是否调整
        'Gap2': current_data['Gap2'], # 2号辊推荐间隙
        'Gap2_is_change': False, # 2号辊是否调整
        'Gap3': current_data['Gap3'], # 3号辊推荐间隙
        'Gap3_is_change': False, # 3号辊是否调整
        'GapFS': current_data['GapFS'], # 定型辊推荐间隙，FS = final sizing
        'GapFS_is_change': False, # 定型辊是否调整
        'CrossScore': current_data['CrossScore'], # 横刀速度
        'CrossScore_is_change': False, # 横刀是否调整
        'TempLowerSetValue': current_data['TempLowerSetValue'], # 夹套水下部温度
        'TempLowerSetValue_is_change': False, # 夹套水下部温度是否调整
        'TempUpperSetValue': current_data['TempUpperSetValue'], # 夹套水上部温度
        'TempUpperSetValue_is_change': False, # 夹套水上部温度是否调整
        'ActualWeight': actual_weight, # 真实重量
        'WeightPredictionBeforeChange': weight_prediction, # 按照现有参数重量预测
        'WeightPredictionAfterChange': weight_prediction, # 按照推荐的参数重量预测
        'msg': ''
    }
    for x in input_data:
        Suggestion_Dict[x] = input_data[x]

    CS_change_allowed = False
    Gaps_change_allowed = False
    Temprature_change_allowed = False

    # Lock for CrossScoring
    # if no recent value change within 15 minutes, and no change since last spc weighing, unlock
    # if T - last_change_time['CrossScore']['TS'] >= datetime.timedelta(minutes = 15) and \
    #         dic_weight['DataTime'] > last_change_time['CrossScore']['TS']:
    if dic_weight['DataTime'] > last_change_time['CrossScore']['TS']:
        CS_change_allowed = True


    # Lock for Gaps
    # if no recent value change within 15 minutes, and no change since last spc weighing, unlock
    most_recent_gap_change = np.max([
        last_change_time['Gap1']['TS'], last_change_time['Gap2']['TS'],
        last_change_time['Gap3']['TS'], last_change_time['GapFS']['TS']
    ])
    # if T - most_recent_gap_change >= datetime.timedelta(minutes = 15) and \
    #         dic_weight['DataTime'] > most_recent_gap_change:
    if dic_weight['DataTime'] > most_recent_gap_change:
        Gaps_change_allowed = True

    # Lock for Temperature
    # if no recent value change within 20 minutes, and no change since last spc weighing, unlock
    most_recent_temp_change = np.max([
        last_change_time['TempLowerSetValue']['TS'], last_change_time['TempUpperSetValue']['TS']
    ])
    if T - most_recent_temp_change >= datetime.timedelta(minutes = 20) and \
            dic_weight['DataTime'] > most_recent_temp_change:
        Temprature_change_allowed = True

    # Lock if still weighing
    if dic_weight['DataTime'] >= T - datetime.timedelta(seconds=30):
        Gaps_change_allowed = False
        CS_change_allowed = False
        Temprature_change_allowed = False
        Suggestion_Dict['msg'] += '正在SPC测量中。'

    # Lock if recent shut down
    if dic_weight['DataTime'] < ValidTimeStart:
        Gaps_change_allowed = False
        CS_change_allowed = False
        Temprature_change_allowed = False
        Suggestion_Dict['msg'] += '最近有停机。'


    if weight_prediction > Control_UB or weight_prediction < Control_LB:

        Suggestion_Dict['msg'] += '重量异常。'
        # Change CrossScoring Rollers if Length is not within the range we want
        if (dic_length_width['LengthOrThickness'] > Thresholds['Length_UB'] or \
            dic_length_width['LengthOrThickness'] < Thresholds['Length_LB']) \
                and CS_change_allowed:

            delta_cs = (Target_Weight - weight_prediction) * (-50)
            delta_cs = fit_range(delta_cs, -1 * Thresholds['CS_Step_UB'], Thresholds['CS_Step_UB'])
            Suggestion_Dict['CrossScore'] = fit_range(
                current_data['CrossScore'] + delta_cs, Thresholds['CS_LB'], Thresholds['CS_UB']
            )
            Suggestion_Dict['WeightPredictionAfterChange'] = Suggestion_Dict['WeightPredictionBeforeChange'] - \
                0.02 * (Suggestion_Dict['CrossScore'] - current_data['CrossScore'])
            if Suggestion_Dict['WeightPredictionAfterChange'] != Suggestion_Dict['WeightPredictionBeforeChange']:
                Suggestion_Dict['is_change'] = True
                Suggestion_Dict['CrossScore_is_change'] = True
                Suggestion_Dict['msg'] += '调整横刀速度'

        # If Length is OK, then change gaps
        elif Gaps_change_allowed:

            # 如果宽度没有问题，那么看能否通过做
            New_Gap1, New_Gap2, New_Gap3, New_GapFS, New_PredWeight, is_success = constrained_optimization(
                dic_lb_ub, weight_prediction, current_data, 1
            )
            if not is_success:
                New_Gap1, New_Gap2, New_Gap3, New_GapFS, New_PredWeight, is_success = constrained_optimization(
                    dic_lb_ub, weight_prediction, current_data, 2
                )
            if New_PredWeight != weight_prediction:
                if New_Gap1 != current_data['Gap1']:
                    Suggestion_Dict['Gap1'] = New_Gap1
                    Suggestion_Dict['Gap1_is_change'] = True
                if New_Gap2 != current_data['Gap2']:
                    Suggestion_Dict['Gap2'] = New_Gap2
                    Suggestion_Dict['Gap2_is_change'] = True
                if New_Gap3 != current_data['Gap3']:
                    Suggestion_Dict['Gap3'] = New_Gap3
                    Suggestion_Dict['Gap3_is_change'] = True
                # Suggestion_Dict['Gap2'] = New_Gap2
                # Suggestion_Dict['Gap3'] = New_Gap3
                # Suggestion_Dict['GapFS'] = New_GapFS
                Suggestion_Dict['WeightPredictionAfterChange'] = New_PredWeight
                Suggestion_Dict['is_change'] = True
                Suggestion_Dict['msg'] += '调整辊轮间隙。'

    # Change Temperature
    # if 'NCS' in dic_weight['Item']:
    #     temp_lb = 45.787
    #     temp_ub = 48.449
    # else:
    #     temp_lb = 48.519
    #     temp_ub = 50.845
    temp_lb = Thresholds['Gum_Temp_LB']
    temp_ub = Thresholds['Gum_Temp_UB']

    if Temprature_change_allowed:

        if current_data['TempExtruder'] > temp_ub:
            Suggestion_Dict['msg'] += '挤压机出口温度过高。'
            Suggestion_Dict['TempLowerSetValue'] = fit_range(
                current_data['TempLowerSetValue'] - Thresholds['Temp_Step_UB'],
                Thresholds['Temp_LB'], Thresholds['Temp_UB']
            )
            Suggestion_Dict['TempUpperSetValue'] = fit_range(
                current_data['TempUpperSetValue'] - Thresholds['Temp_Step_UB'],
                Thresholds['Temp_LB'], Thresholds['Temp_UB']
            )
            if Suggestion_Dict['TempLowerSetValue'] != current_data['TempLowerSetValue'] or \
                    Suggestion_Dict['TempUpperSetValue'] != current_data['TempUpperSetValue']:
                Suggestion_Dict['is_change'] = True
                Suggestion_Dict['msg'] += '调整夹套水温度。'

        elif current_data['TempExtruder'] < temp_lb:
            Suggestion_Dict['msg'] += '挤压机出口温度过低。'
            Suggestion_Dict['TempLowerSetValue'] = fit_range(
                current_data['TempLowerSetValue'] + Thresholds['Temp_Step_UB'],
                Thresholds['Temp_LB'], Thresholds['Temp_UB']
            )
            Suggestion_Dict['TempUpperSetValue'] = fit_range(
                current_data['TempUpperSetValue'] + Thresholds['Temp_Step_UB'],
                Thresholds['Temp_LB'], Thresholds['Temp_UB']
            )
            if Suggestion_Dict['TempLowerSetValue'] != current_data['TempLowerSetValue']:
                Suggestion_Dict['is_change'] = True
                Suggestion_Dict['msg'] += '调整夹套水(下)温度。'
                Suggestion_Dict['TempLowerSetValue_is_change'] = True
            if Suggestion_Dict['TempUpperSetValue'] != current_data['TempUpperSetValue']:
                Suggestion_Dict['is_change'] = True
                Suggestion_Dict['msg'] += '调整夹套水(上)温度。'
                Suggestion_Dict['TempUpperSetValue_is_change'] = True

    # 添加长度宽度厚度深度数据
    Suggestion_Dict['Length_Date'] = dic_length_width['DataTime'].strftime("%Y-%m-%d %H:%M:%S")
    Suggestion_Dict['Length'] = dic_length_width['LengthOrThickness']
    Suggestion_Dict['Length_std'] = dic_length_width['LengthOrThickness_std']
    Suggestion_Dict['width'] = dic_length_width['WidthOrDepth']
    Suggestion_Dict['width_std'] = dic_length_width['WidthOrDepth_std']

    Suggestion_Dict['Thickness_Date'] = dic_thickness_depth['DataTime'].strftime("%Y-%m-%d %H:%M:%S")
    Suggestion_Dict['Thickness'] = dic_thickness_depth['LengthOrThickness']
    Suggestion_Dict['Thickness_std'] = dic_thickness_depth['LengthOrThickness_std']
    Suggestion_Dict['Depth'] = dic_thickness_depth['WidthOrDepth']
    Suggestion_Dict['Depth_std'] = dic_thickness_depth['WidthOrDepth_std']

    Suggestion_Dict['Weight_Date'] = dic_weight['DataTime'].strftime("%Y-%m-%d %H:%M:%S")
    #shift_code = df_weight['shift'].strip()
    #shift_points = shift_code.split('\\u')
    #Suggestion_Dict['shift'] = ''.join([chr(int(code,16)) for code in shift_points[1:]]) 
    Suggestion_Dict['shift'] = dic_weight['shift'].strip()
    if Connection_Method == 'Azure':
        Blob_Target.upload_blob(edge_blob.BlobConfig.target_container_name, input_data['filePath'] + 'azure_output_data.json',
                                json.dumps(Suggestion_Dict))
    else:
        try:
            edge_blob.save_dict_to_blob_json(input_data['filePath'] + 'edge_output_data.json', Suggestion_Dict)
        except Exception as e:
            print (e)
    return json.dumps(Suggestion_Dict, ensure_ascii=False)


if __name__ == '__main__':


    # raw_data = sys.argv[1]
    t = datetime.datetime(2024, 11, 12, 8, 32, 0)
    # T = [t.year, t.month, t.day, t.hour, t.minute, t.second]
    T = t
    while t <= datetime.datetime(2024, 11, 12, 8, 32, 0):
        sku = get_current_sku(
            "yngetl/" + (t - datetime.timedelta(seconds=15)).strftime('%Y/%m/%d/%H/%M/%S/'), 'Azure'
        )
        # sku = 'DMPE'
        raw_data = json.dumps({
            "time": datetime_to_list(t),
            "filePath": "yngetl/" + (t).strftime('%Y/%m/%d/%H/%M/%S/'),
            # "filePath": (t - datetime.timedelta(seconds=15)).strftime('%Y/%m/%d/%H/%M/%S/'),
            "fileLastTs": t.strftime('%Y-%m-%d %H:%M:%S'),
            "connection": "Azure",
            "SKU": sku,
            "lastStartTime": datetime_to_list(t - datetime.timedelta(minutes=20))
        })
        raw_data = '''
        {"time": [2024, 11, 12, 13, 36, 0], 
        "filePath": "yngetl/2024/11/12/13/35/45/", 
        "fileLastTs": "2024-11-12 13:36:00", 
        "SKU": "DMPY", 
        "lastStartTime": [2024, 11, 12, 13, 16, 54],
        "connection": "Azure"}
        '''
        # raw_data = json.dumps({
        #     "time": [2024, 11, 8, 8, 3, 0],
        #     "filePath": "yngetl/2024/11/08/08/02/45/",
        #     "fileLastTs": "2024-11-08 08:03:00",
        #     "connection": "Azure",
        #     "SKU": "AUWM",
        #     "lastStartTime": [2024, 11, 8, 7, 40, 0]
        # })
        if True:
            output_json = run(raw_data)

            output_dict = json.loads(output_json)

            print(output_dict['time'])
            if output_dict['is_change']:
                print(output_dict['msg'])
                print(output_json)
                print(output_dict['WeightPredictionBeforeChange'])
            else:
                print(output_dict['msg'])
        # except Exception as e:
        #     print (e)

        t += datetime.timedelta(seconds=60)
        break

