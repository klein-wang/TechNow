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


def fit_range(x, lb, ub):
    if x < lb:
        return lb
    elif x > ub:
        return ub
    return x


def single_factor_change(initial_weight, target_weight, initial_x, k, lb, ub):
    delta = (target_weight - initial_weight) / k
    new_x = fit_range(initial_x + delta, lb, ub)
    new_weight = initial_weight + (new_x - initial_x) * k
    return new_x, new_weight


def constrained_optimization(thresholds, weight_prediction, current_data):

    DV = ['Gap1', 'Gap2', 'Gap3', 'GapFS']

    solver = pywraplp.Solver.CreateSolver('SCIP')
    bigM = 10 ** 10
    infinity = solver.infinity()

    # Decision Variables
    DV_factor_values = {
        x: solver.NumVar(
            thresholds[x]['lb'], thresholds[x]['ub'], '''Suggested_Value_%s''' % (x)
        ) for x in DV
    }
    weight_after_change = weight_prediction + \
                          K_Gap1 * (DV_factor_values['Gap1'] - current_data['Gap1']) + \
                          K_Gap2 * (DV_factor_values['Gap2'] - current_data['Gap2']) + \
                          K_Gap3 * (DV_factor_values['Gap3'] - current_data['Gap3']) + \
                          K_GapFS * (DV_factor_values['GapFS'] - current_data['GapFS'])

    # 1st Priority Objective
    final_weight_gap = weight_after_change - Target_Weight
    OBJ_abs_weight_gap = solver.NumVar(0, 100, 'OBJ_weight_gap')

    # 2nd Priority Objecticce
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
    solver.Add(OBJ_abs_weight_gap >= final_weight_gap)
    solver.Add(OBJ_abs_weight_gap >= (-1) * final_weight_gap)
    solver.Add(abs_1_2_diff_change >= diff_1_2_before - diff_1_2_after)
    solver.Add(abs_1_2_diff_change >= diff_1_2_after - diff_1_2_before)
    solver.Add(abs_2_3_diff_change >= diff_2_3_before - diff_2_3_after)
    solver.Add(abs_2_3_diff_change >= diff_2_3_after - diff_2_3_before)
    solver.Add(abs_3_FS_diff_change >= diff_3_FS_before - diff_3_FS_after)
    solver.Add(abs_3_FS_diff_change >= diff_3_FS_after - diff_3_FS_before)

    status = solver.Solve()
    if status == pywraplp.Solver.OPTIMAL:
        return DV_factor_values['Gap1'].solution_value(), DV_factor_values['Gap2'].solution_value(),\
            DV_factor_values['Gap3'].solution_value(),DV_factor_values['GapFS'].solution_value(), \
            weight_after_change.solution_value()
    else:
        return current_data['Gap1'], current_data['Gap2'], current_data['Gap3'], current_data['GapFS'], \
            weight_prediction


def multi_factors_change(initial_weight, dic_initial_x, dic_k, dic_lb, dic_ub):

    solver = pywraplp.Solver.CreateSolver('SCIP')
    bigM = 10 ** 10
    infinity = solver.infinity()

    DV_factor_changes = {
        x: solver.IntVar(0, 1, '''Is_Change_%s''' % (x)) for x in dic_initial_x
    }
    DV_factor_values = {
        x: solver.NumVar(
            np.min([dic_lb[x], dic_initial_x[x]]),
            np.max([dic_ub[x], dic_initial_x[x]]),
            '''Suggested_Value_%s''' % (x)
        ) for x in dic_initial_x
    }

    weight_after_change = initial_weight + np.sum([
        (DV_factor_values[x] - dic_initial_x[x]) * dic_k[x] for x in dic_initial_x
    ])
    OBJ_count_changed_factors = np.sum([
        DV_factor_changes[x] for x in dic_initial_x
    ])
    final_weight_gap = weight_after_change - Target_Weight
    OBJ_abs_weight_gap = solver.NumVar(0, 100, 'OBJ_weight_gap')
    solver.Minimize(OBJ_abs_weight_gap + 0.001 * OBJ_count_changed_factors)
    solver.Add(OBJ_abs_weight_gap >= final_weight_gap)
    solver.Add(OBJ_abs_weight_gap >= (-1) * final_weight_gap)

    # DV_factor_changes[x]越小越好，这里自带一个趋势
    for x in dic_initial_x:
        solver.Add(bigM * (DV_factor_changes[x]) >= DV_factor_values[x] - dic_initial_x[x])
        solver.Add(bigM * (DV_factor_changes[x]) >= dic_initial_x[x] - DV_factor_values[x])

    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        return {
            x: DV_factor_changes[x].solution_value() for x in DV_factor_changes
        }, {
            x: DV_factor_values[x].solution_value() for x in DV_factor_values
        }, weight_after_change.solution_value()
    else:
        return {x: 0 for x in DV_factor_changes}, dic_initial_x, initial_weight


def map_data():

    file_path_now = input_data['filePath']
    merge_file_path = ''

    if 'Local_Curated_Data' in input_data['filePath']:
        merge_file_path = input_data['filePath'] + 'merge.csv'
        df_curated_data = pd.read_csv(input_data['filePath'] + 'curated_parm.csv')
        df_spc_data = pd.read_csv(input_data['filePath'] + 'curated_spc.csv')
        file_path_last = input_data['filePath'][:19] + (
                datetime.datetime.strptime(input_data['filePath'][19:], '%Y/%m/%d/%H/%M/%S/') - datetime.timedelta(seconds=15)
            ).strftime('%Y/%m/%d/%H/%M/%S/')
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
                'Prev_CG_Sheeting.CG_Sheeting.Variables.rGumExtruderExitGumTemp'
            ]
        })
        try:
            df_prev_merge = pd.read_csv(file_path_last + 'merge.csv')
        except:
            df_prev_merge = df_prev_merge_empty
    else:
        df_curated_data = edge_blob.read_csv_blob_to_dataframe(input_data['filePath'] + 'curated_parm.csv')
        df_spc_data = edge_blob.read_csv_blob_to_dataframe(input_data['filePath'] + 'curated_spc.csv')
        file_path_last = (
                datetime.datetime.strptime(input_data['filePath'], '%Y/%m/%d/%H/%M/%S/') - datetime.timedelta(seconds=15)
            ).strftime('%Y/%m/%d/%H/%M/%S/')
        try:
            df_prev_merge = edge_blob.read_csv_blob_to_dataframe(file_path_last + 'merge.csv')
        except:
            df_prev_merge = df_prev_merge_empty

    # df_mapping, current_data = data_mapping.merge_data(df_curated_data, df_spc_data, df_prev_merge)

    df_mapping, current_data = data_mapping.process_etl_data(
        now=T,
        parm=df_curated_data,
        spc=df_spc_data,
        prev_merge=df_prev_merge,
        merge_OT_SPC=data_mapping.merge_OT_SPC,
        output_file=merge_file_path
    )

    if 'Local_Curated_Data' not in input_data['filePath']:
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
        'Prev_CG_Sheeting.CG_Sheeting.Variables.rGumExtruderExitGumTemp': 'Prev_TempExtruder'
    }

    df_mapping = df_mapping.rename(columns=name_mapping)

    fixed_keys = list(current_data.keys())
    for c in fixed_keys:
        if c in name_mapping:
            current_data[name_mapping[c]] = current_data[c]

    return df_mapping, current_data

def predict_weight_now(df_mapping, current_data):

    df_mapping['Gap1_Influence'] = (current_data['Gap1'] - df_mapping['Gap1']) * K_Gap1
    df_mapping['Gap1_Influence'] = df_mapping['Gap1_Influence'].fillna(0)
    df_mapping['Gap2_Influence'] = (current_data['Gap2'] - df_mapping['Gap2']) * K_Gap2
    df_mapping['Gap2_Influence'] = df_mapping['Gap2_Influence'].fillna(0)
    df_mapping['Gap3_Influence'] = (current_data['Gap3'] - df_mapping['Gap3']) * K_Gap3
    df_mapping['Gap3_Influence'] = df_mapping['Gap3_Influence'].fillna(0)
    df_mapping['GapFS_Influence'] = (current_data['GapFS'] - df_mapping['GapFS']) * K_GapFS
    df_mapping['GapFS_Influence'] = df_mapping['GapFS_Influence'].fillna(0)
    df_mapping['Temp1_Influence'] = (current_data['Temp1'] - df_mapping['Temp1']) * K_Gap1
    df_mapping['Temp1_Influence'] = df_mapping['Temp1_Influence'].fillna(0)
    df_mapping['Temp2_Influence'] = (current_data['Temp2'] - df_mapping['Temp2']) * K_Gap1
    df_mapping['Temp2_Influence'] = df_mapping['Temp2_Influence'].fillna(0)

    df_mapping['Modified_Weight'] = df_mapping['Weight'] + df_mapping['Gap1_Influence'] + \
                                    df_mapping['Gap2_Influence'] + df_mapping['Gap3_Influence'] + \
                                    df_mapping['GapFS_Influence']

    df_mapping['Date'] = [pd.Timestamp(x) for x in df_mapping['Date']]
    df_mapping = df_mapping.sort_values(by='Date', ascending=False)
    w_prev = df_mapping['Weight'][0]
    mw_prev = df_mapping['Modified_Weight'][0]
    t_end = datetime.datetime.strptime(input_data['fileLastTs'], "%Y-%m-%d %H:%M:%S")
    df_15 = df_mapping[df_mapping['Date']>=t_end - datetime.timedelta(minutes=15)]
    df_30 = df_mapping[df_mapping['Date']>=t_end - datetime.timedelta(minutes=30)]
    if len(df_15) >= 1:
        w_15 = np.mean(df_15['Weight'])
        mw_15 = np.mean(df_15['Modified_Weight'])
    else:
        w_15 = w_prev
        mw_15 = mw_prev
    if len(df_30) >= 1:
        w_30 = np.mean(df_30['Weight'])
        mw_30 = np.mean(df_30['Modified_Weight'])
    else:
        w_30 = w_prev
        mw_30 = mw_prev

    return 0.6 * mw_prev + 0.3 * mw_15 + 0.1 * mw_30, w_prev


def run(input_str):

    global Target_Weight, df_mapping, input_data, current_data, K_GapFS, K_Gap3, K_Gap1, K_Gap2, K_Temp1, K_Temp2, T

    Control_UB = 35.36
    Control_LB = 35.1
    Target_Weight = 35.23

    input_data = json.loads(input_str)
    T = datetime.datetime(
        input_data['time'][0], input_data['time'][1], input_data['time'][2],
        input_data['time'][3], input_data['time'][4], input_data['time'][5]
    )

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
        'Gap1': {'ub': 0.12, 'lb': 0.1},
        'Gap2': {'ub': 0.08, 'lb': 0.065},
        'Gap3': {'ub': 0.075, 'lb': 0.06},
        'GapFS': {'ub': 0.07, 'lb': 0.06},
        'Temp1': {'ub': -10.0, 'lb': -15.0},
        'Temp2': {'ub': -10.0, 'lb': -15.0}
    }

    df_mapping, current_data = map_data()
    weight_prediction, actual_weight = predict_weight_now(df_mapping, current_data)
    print(weight_prediction)

    Suggestion_Dict = {
        'code': 200, # 这期都是200，异常处理下一期做
        'is_change': False, # 是否需要调整
        'Gap1': current_data['Gap1'], # 1号辊推荐间隙
        'Gap2': current_data['Gap2'], # 2号辊推荐间隙
        'Gap3': current_data['Gap3'], #  3号辊推荐间隙
        'GapFS': current_data['GapFS'], # 定型辊推荐间隙，FS = final sizing
        'ActualWeight': actual_weight,
        'WeightPredictionBeforeChange': weight_prediction, # 按照现有参数重量预测
        'WeightPredictionAfterChange': weight_prediction, # 按照推荐的参数重量预测
        'msg': ''
    }
    for x in input_data:
        Suggestion_Dict[x] = input_data[x]

    if weight_prediction > Control_UB or weight_prediction < Control_LB:
        New_Gap1, New_Gap2, New_Gap3, New_GapFS, New_PredWeight = constrained_optimization(
            dic_lb_ub, weight_prediction, current_data
        )
        if New_PredWeight != weight_prediction:
            Suggestion_Dict['Gap1'] = New_Gap1
            Suggestion_Dict['Gap2'] = New_Gap2
            Suggestion_Dict['Gap3'] = New_Gap3
            Suggestion_Dict['GapFS'] = New_GapFS
            Suggestion_Dict['WeightPredictionAfterChange'] = New_PredWeight
            Suggestion_Dict['is_change'] = True

        return json.dumps(Suggestion_Dict)


if __name__ == '__main__':

    # raw_data = sys.argv[1]
    raw_data = json.dumps({
        "time":  [2024, 8, 21, 10, 10, 0, 0],
        "fileFirstTs": "2024-07-91 16:55:16",
        "curTs": "2024-08-14 14:52:31",
        "filePath": "Local_Curated_Data/2024/08/21/10/10/00/",
        "fileLastTs": "2024-06-28 16:55:31"
    })
    output_json = run(raw_data)
    print (output_json)