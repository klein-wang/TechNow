import pandas as pd
import numpy as np
import joblib
import json
from ortools.linear_solver import pywraplp
import sys
import string
import pytz
import json
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, BlobClient
import io
import os
import configparser
import warnings


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


def run(input_str):

    global Target_Weight
    Control_UB = 35.36
    Control_LB = 35.1
    Target_Weight = 35.23

    input_data = json.loads(input_str)
    t = input_data['time']
    # file_path = '''History_Data/%s/%s/%s/%s/%s/initial_x.json''' % (
    #     str(t[0]), str(t[1]), str(t[2]), str(t[3]), str(t[4])
    # )
    # with open(file_path, 'r') as f:
    #     initial_data = json.load(f)
    # with open(file_path, 'r') as f:
    #     Suggestion = json.load(f)
    if input_data['method'] == 'Local Test':
        df_mapping = pd.read_csv('merge_final_py.csv')


    # Load Models
    model_forming_roller_gap = joblib.load('Models/Forming Roller 定型辊间隙.joblib')
    K_forming_roller_gap = model_forming_roller_gap.coef_[0]
    model_forming_roller_speed = joblib.load('Models/Forming Roller 辊轮速度.joblib')
    K_forming_roller_speed = model_forming_roller_speed.coef_[0]

    model_3_roller_gap = joblib.load('Models/3号辊间隙.joblib')
    K_3_roller_gap = model_3_roller_gap.coef_[0]
    model_3_roller_speed = joblib.load('Models/3号辊轮速度.joblib')
    K_3_roller_speed = model_3_roller_speed.coef_[0]

    model_2_roller_gap = joblib.load('Models/2号辊间隙.joblib')
    K_2_roller_gap = model_2_roller_gap.coef_[0]
    model_2_roller_speed = joblib.load('Models/2号辊轮速度.joblib')
    K_2_roller_speed = model_2_roller_speed.coef_[0]

    model_1_roller_gap = joblib.load('Models/1号辊间隙.joblib')
    K_1_roller_gap = model_1_roller_gap.coef_[0]
    model_1_roller_speed = joblib.load('Models/1号辊轮速度.joblib')
    K_1_roller_speed = model_1_roller_speed.coef_[0]

    model_2_cooling_roller_temperature = joblib.load('Models/2号冷辊入口温度.joblib')
    K_2_colling_roller_tempereature = model_2_cooling_roller_temperature.coef_[0]
    model_1_cooling_roller_temperature = joblib.load('Models/1号冷辊入口温度.joblib')
    K_1_colling_roller_tempereature = model_1_cooling_roller_temperature.coef_[0]

    model_big_roller_speed = joblib.load('Models/大辊速度.joblib')
    K_big_roller_speed = model_big_roller_speed.coef_[0]

    dic_lb_ub = {
        'big_roller_spped': {'ub': 25.0, 'lb': 20.0},
        '1_roller_speed': {'ub': 85.0, 'lb': 75.0},
        '1_roller_gap': {'ub': 0.12, 'lb': 0.1},
        '2_roller_speed': {'ub': 125.0, 'lb': 110.0},
        '2_roller_gap': {'ub': 0.08, 'lb': 0.065},
        '3_roller_speed': {'ub': 145.0, 'lb': 125.0},
        '3_roller_gap': {'ub': 0.075, 'lb': 0.06},
        'forming_roller_speed': {'ub': 170.0, 'lb': 140.0},
        'forming_roller_gap': {'ub': 0.07, 'lb': 0.06},
        '1_cooling_roller_temperature': {'ub': -10.0, 'lb': -15.0},
        '2_cooling_roller_temperature': {'ub': -10.0, 'lb': -15.0}
    }

    weight_prediction = initial_data['Weight']
    print(weight_prediction)

    # 先试试定型辊
    if weight_prediction > Control_UB or weight_prediction < Control_LB:
        Suggestion['forming_roller_gap'], weight_prediction = single_factor_change(
            weight_prediction, Target_Weight, Suggestion['forming_roller_gap'], K_forming_roller_gap,
            dic_lb_ub['forming_roller_gap']['lb'], dic_lb_ub['forming_roller_gap']['ub']
        )
    print(weight_prediction)

    # 再试试三号辊
    if weight_prediction > Control_UB or weight_prediction < Control_LB:
        Suggestion['3_roller_gap'], weight_prediction = single_factor_change(
            weight_prediction, Target_Weight, Suggestion['3_roller_gap'], K_3_roller_gap,
            dic_lb_ub['3_roller_gap']['lb'], dic_lb_ub['3_roller_gap']['ub']
        )
    print(weight_prediction)

    level_2_factors = [
        '1_roller_gap', '2_roller_gap', '1_cooling_roller_temperature', '2_cooling_roller_temperature'
    ]
    if weight_prediction > Control_UB or weight_prediction < Control_LB:
        whether_changes, updated_x, weight_prediction = multi_factors_change(
            weight_prediction,
            {f: Suggestion[f] for f in level_2_factors},
            {
                '1_roller_gap': K_1_roller_gap,
                '2_roller_gap': K_2_roller_gap,
                '1_cooling_roller_temperature': K_1_colling_roller_tempereature,
                '2_cooling_roller_temperature': K_2_colling_roller_tempereature
            },
            {f: dic_lb_ub[f]['lb'] for f in level_2_factors},
            {f: dic_lb_ub[f]['ub'] for f in level_2_factors}
        )
        Suggestion.update(updated_x)

    print (Suggestion)

    params = [
        'big_roller_speed', '1_roller_speed', '1_roller_gap', '2_roller_speed', '2_roller_gap', '3_roller_speed',
        '3_roller_gap', 'forming_roller_speed', 'forming_roller_gap', '1_cooling_roller_temperature',
        '2_cooling_roller_temperature'
    ]
    output_dict = {
        'initial_params': {x: float(initial_data[x]) for x in params},
        'suggested_params': {x : float(Suggestion[x]) for x in params},
        'initial_weight': float(initial_data['Weight']),
        'predicted_weight_after_suggestion': float(weight_prediction)
    }

    file_path = '''History_Data/%s/%s/%s/%s/%s/ai_output.json''' % (
        str(t[0]), str(t[1]), str(t[2]), str(t[3]), str(t[4])
    )
    with open(file_path, 'w') as json_file:
        json.dump(output_dict, json_file, indent=4)

    file_path = '''output_files/ai_output.json'''
    with open(file_path, 'w') as json_file:
        json.dump(output_dict, json_file, indent=4)


if __name__ == '__main__':

    # raw_data = sys.argv[1]
    raw_data = json.dumps({
        'time': [2024, 6, 12, 0, 0],
        'method': 'Local Test'
    })
    output_json = run(raw_data)