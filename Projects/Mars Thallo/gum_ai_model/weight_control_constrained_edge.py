import joblib
import json
import numpy as np
import pandas as pd
import datetime
import pytz
import io
from azureml.core.model import Model
from azure.core import exceptions as AzureExceptions
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import warnings

import time
from ortools.linear_solver import pywraplp

import urllib.request
import os
import ssl
import sys



warnings.filterwarnings(action='ignore', category=UserWarning)


class AzureBlobStorage:

    def __init__(self, connection_string):
        """
        创建 Azure Blob 存储客户端
        """
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    def upload_blob(self, container_name, blob_name, data):
        """
        上传数据到 Blob
        """
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(data, overwrite=True)

    def download_blob(self, container_name, blob_name):
        """
        下载 Blob 中的数据
        """
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        data = blob_client.download_blob().readall()
        return data

    def list_blobs(self, container_name):
        """
        列出 Blob 容器中的所有 Blob
        """
        container_client = self.blob_service_client.get_container_client(container_name)
        blobs = []
        try:
            for blob in container_client.list_blobs():
                blobs.append(blob.name)
        except Exception as e:
            print("error", e)
        return blobs

    def list_blobs(self, container_name, blob_name):
        """
        列出 Blob 容器中的所有 Blob
        """
        container_client = self.blob_service_client.get_container_client(container_name)
        blobs = []
        try:
            for blob in container_client.list_blobs(name_starts_with=blob_name):
                blobs.append(blob.name)
        except Exception as e:
            print("error", e)
        return blobs

    def list_container(self):
        container_list = []
        for container in self.blob_service_client.list_containers():
            container_list.append(container.name)
            return container_list

    def create_container(self, container_name):
        """
        创建 Blob 容器
        """
        container_client = self.blob_service_client.create_container(container_name)
        return container_client

    def delete_container(self, container_name):
        """
        删除 Blob 容器
        """
        container_client = self.blob_service_client.get_container_client(container_name)
        container_client.delete_container()

    def delete_blob(self, container_name, blob_name):
        """
        删除 Blob
        """
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.delete_blob()


# The variables
def init():
    '''

    :param endpoint_entry:
        if using from AML services, endpoint_entry=True,
        if debugging from local, endpoint_entry=False
    :return:
    '''

    global ESM_weight_model, EXOM_weight_model, EXSB_weight_model, endpoint_entry_method, Syrup_Drying_model, \
           Appearance_Bayesian_Model, SQL_Connection, ACI_Connection, Syrup_Drying_10a_model, Syrup_Drying_10b_model, \
           Syrup_Drying_11_model, Syrup_Drying_12_model

    esm_path = 'ESM_weight_control.joblib'
    exom_path = 'ESOM_weight_control.joblib'
    exsb_path = 'ESOM_weight_control.joblib'
    syrup_drying_path = 'Syrup_Drying_Relation.joblib'
    appearance_bayesian_path = 'appearance_bayesian_model.joblib'
    syrup_drying_10a_path = 'Syrup_Drying_10a.joblib'
    syrup_drying_10b_path = 'Syrup_Drying_10b.joblib'
    syrup_drying_11_path = 'Syrup_Drying_11.joblib'
    syrup_drying_12_path = 'Syrup_Drying_12.joblib'

    ESM_weight_model = joblib.load(esm_path)
    EXOM_weight_model = joblib.load(exom_path)
    EXSB_weight_model = joblib.load(exsb_path)
    Syrup_Drying_model = joblib.load(syrup_drying_path)
    Appearance_Bayesian_Model = joblib.load(appearance_bayesian_path)
    Syrup_Drying_10a_model = joblib.load(syrup_drying_10a_path)
    Syrup_Drying_10b_model = joblib.load(syrup_drying_10b_path)
    Syrup_Drying_11_model = joblib.load(syrup_drying_11_path)
    Syrup_Drying_12_model = joblib.load(syrup_drying_12_path)


def load_data():

    global df_formula, Weight_Model, dic_formula, dic_appearance_thresholds, default_settings, pc_standards

    with open('son_recipe_settings.json', 'r') as f:
        dic_formula_all = json.load(f)
    dic_formula = {
        int(p): {
            int(c): dic_formula_all[SKU][p][c] for c in dic_formula_all[SKU][p]
        } for p in dic_formula_all[SKU]
    }
    with open('appearance_config_data.json', 'r') as f:
        dic_appearance_thresholds = json.load(f)

    if 'ESM' in SKU:
        Weight_Model = ESM_weight_model
    elif 'EXOM' in SKU:
        Weight_Model = EXOM_weight_model
    else:
        Weight_Model = EXSB_weight_model

    default_settings = dic_formula_all
    with open('son_limitValue_settings.json', 'r') as f:
        pc_standards_all = json.load(f)
    pc_standards = {}
    for row in pc_standards_all:
        if row['skuName'] == SKU:
            pc_standards[(int(row['phase'])), (int(row['cycle']))] = {
                'wlsl': row['wlsl'],
                'wlcl': row['wlcl'],
                'wucl': row['wucl'],
                'wusl': row['wusl'],
                'appearanceCheck': row['appearanceCheck'],
                'CanBeSkipped': row['CanBeSkipped'],
                'l1PCT': float(row['l1PCT'].replace('', '0')),
                'l2PCT': float(row['l2PCT'].replace('', '1')),
                'l3PCT': float(row['l3PCT'].replace('', '1')),
                'l1Disaster': float(row['L1Proportion'].replace('', '0'))
            }

    for p in dic_formula:
        if p > 13:
            continue
        for c in dic_formula[p]:
            if p > Phase or (p == Phase and c > Cycle):
                MainData['prediction'][(p, c)] = {
                    'predictionWeight': None,'surfacePercent': None
                }
                MainData['suggestion'][(p, c)] = {
                    'speed_1': float(dic_formula[p][c]['Drumspeed_N_default_value']),
                    'speed_2': float(dic_formula[p][c]['Drumspeed_S_default_value']),
                    'syrup': float(dic_formula[p][c]['Syrup_default_value']),
                    'drying': float(dic_formula[p][c]['Drying_default_value']),
                    'pause': float(dic_formula[p][c]['Pause_default_value']),
                    'action': None
                }

    if len(dic_formula) == 0 or len(pc_standards) == 0:
        return False
    else:
        return True



def weight_prediction_by_formula_till_end():

    list_pc = sorted(list(MainData['prediction'].keys()))
    weight_pc = Weight
    for (p, c) in list_pc:
        syrup_pc = MainData['suggestion'][(p, c)]['syrup']
        action_pc = MainData['suggestion'][(p, c)]['action']
        if not action_pc or action_pc != 'Skip':
            weight_pc += syrup_pc * Gradient_Syrup
        MainData['prediction'][(p, c)]['predictionWeight'] = weight_pc


def weight_suggestion_phase_10():

    if Cycle <= 4 and MainData['prediction'][(10, 5)]['predictionWeight'] >= Phase_10_End_MinTarget:
        MainData['suggestion'][(10, 5)]['action'] = '再次称重 Check Weight Again'
    elif Cycle <= 5 and MainData['prediction'][(10, 6)]['predictionWeight'] >= Phase_10_End_MinTarget:
        MainData['suggestion'][(10, 6)]['action'] = '再次称重 Check Weight Again'
    elif Cycle <= 6:
        MainData['suggestion'][(10, 7)]['action'] = '再次称重 Check Weight Again'


def calculate_gap(x):
    if np.isnan(x):
        return 0
    if x <= 0:
        return 0
    else:
        return x


def appearance_gaps(start_phase, start_cycle):

    standard = pc_standards[(start_phase, start_cycle)]
    threshold_score = 10 * standard['l1PCT'] + 3 * standard['l2PCT'] + 1 * standard['l3PCT']
    Appearance_1_Gap = standard['l1PCT'] - Appearance_1_Num / Num_Samples
    Appearance_2_Gap = Appearance_2_Num / Num_Samples - standard['l2PCT']
    Appearance_3_Gap = Appearance_3_Num / Num_Samples - standard['l3PCT']
    if Appearance_1_Num / Num_Samples <= standard['l1Disaster']:
        return_dict['data']['NeedManualTakeover'] = True
    if Appearance_1_Gap <= 0 and Appearance_2_Gap <= 0 and Appearance_3_Gap <= 0:
        return 'MeetTarget', 0
    elif Appearance_3_Num / Num_Samples >= standard['l3PCT'] * 2:
        return 'LargeGap', Appearance_3_Num / Num_Samples - standard['l3PCT']
    else:
        return 'SmallGap', Appearance_3_Num / Num_Samples - standard['l3PCT']


def get_appearance_suggestion(start_phase, start_cycle, smoothness_now):

    global Next_Checkpoint_Good_Smoothness_Probability, changeable_pc
    return_dict['data']['surface_now'] = smoothness_now
    changeable = {
            'DryingTime': False,
            'PauseTime': False,
            'DrumspeedN': False,
            'DrumspeedS': False
        }

    list_pc = sorted(list(MainData['prediction'].keys()))
    changeable_pc = []
    for (p, c) in list_pc:
        if len(changeable_pc) >= 3:
            break
        if pc_standards[(p, c)]['appearanceCheck'] == '是':
            changeable_pc.append((p, c))

    if changeable_pc == []:
        return {
            'DryingTime': 'Medium',
            'PauseTime': 'Medium',
            'DrumspeedN': 'Medium',
            'DrumspeedS': 'Medium'
        }

    for (p, c) in changeable_pc:
        if dic_formula[p][c]['Pause_status']:
            changeable['PauseTime'] = True
            dic_formula[p][c]['Pause_default_value'] = float(dic_formula[p][c]['Pause_default_value'])
        if dic_formula[p][c]['Drying_status']:
            changeable['DryingTime'] = True
            dic_formula[p][c]['Drying_default_value'] = float(dic_formula[p][c]['Drying_default_value'])
        if dic_formula[p][c]['Drumspeed_N_status']:
            changeable['DrumspeedN'] = True
            dic_formula[p][c]['Drumspeed_N_default_value'] = float(dic_formula[p][c]['Drumspeed_N_default_value'])
        if dic_formula[p][c]['Drumspeed_S_status']:
            changeable['DrumspeedS'] = True
            dic_formula[p][c]['Drumspeed_S_default_value'] = float(dic_formula[p][c]['Drumspeed_S_default_value'])

    df = pd.DataFrame.from_dict({'LastSmoothness': [smoothness_now], 'k': [1]})
    df = pd.merge(df, pd.DataFrame.from_dict({'Syrup': ['Medium'], 'k': [1]}), how='inner', on='k')
    if changeable['PauseTime']:
        df = pd.merge(df, pd.DataFrame.from_dict({'PauseTime': ['Low', 'Medium', 'High'], 'k': [1, 1, 1]}),
                      how='inner', on='k')
    else:
        df = pd.merge(df, pd.DataFrame.from_dict({'DryingTime': ['Medium'], 'k': [1]}), how='inner', on='k')
    if changeable['DryingTime']:
        df = pd.merge(df, pd.DataFrame.from_dict({'DryingTime': ['Low', 'Medium', 'High'], 'k': [1, 1, 1]}),
                      how='inner', on='k')
    else:
        df = pd.merge(df, pd.DataFrame.from_dict({'PauseTime': ['Medium'], 'k': [1]}), how='inner', on='k')
    if changeable['DrumspeedS']:
        df = pd.merge(df, pd.DataFrame.from_dict({'DrumspeedS': ['Low', 'Medium', 'High'], 'k': [1, 1, 1]}),
                      how='inner', on='k')
    else:
        df = pd.merge(df, pd.DataFrame.from_dict({'DrumspeedS': ['Medium'], 'k': [1]}), how='inner', on='k')
    if changeable['DrumspeedN']:
        df = pd.merge(df, pd.DataFrame.from_dict({'DrumspeedN': ['Low', 'Medium', 'High'], 'k': [1, 1, 1]}),
                      how='inner', on='k')
    else:
        df = pd.merge(df, pd.DataFrame.from_dict({'DrumspeedN': ['Medium'], 'k': [1]}), how='inner', on='k')

    df_class = Appearance_Bayesian_Model.predict_probability(
        df[['DryingTime', 'PauseTime', 'LastSmoothness', 'DrumspeedN', 'DrumspeedS', 'Syrup']]
    )
    for col in df_class:
        df[col] = df_class[col]
    df = df.sort_values(by='Smoothness_MeetTarget', ascending=False).reset_index(drop=True)

    Next_Checkpoint_Good_Smoothness_Probability = df['Smoothness_MeetTarget'][0]
    checkpoint = changeable_pc[-1]
    MainData['prediction'][checkpoint]['surfacePercent'] = Next_Checkpoint_Good_Smoothness_Probability
    MainData['suggestion'][checkpoint]['action'] = 'Check Photo and Weight Again'

    if smoothness_now == 'MeetTarget':
        # checkpoint = list_pc[2]
        MainData['prediction'][checkpoint]['surfacePercent'] = np.max([0.95, Next_Checkpoint_Good_Smoothness_Probability])
        MainData['suggestion'][checkpoint]['action'] = 'Check Photo and Weight Again'
        return {
            'DryingTime': 'Medium',
            'PauseTime': 'Medium',
            'DrumspeedN': 'Medium',
            'DrumspeedS': 'Medium'
        }

    return {
            'DryingTime': df['DryingTime'][0],
            'PauseTime': df['PauseTime'][0],
            'DrumspeedN': df['DrumspeedN'][0],
            'DrumspeedS': df['DrumspeedS'][0]
        }


def case_based_reasoning_pause_drying(start_phase, start_cycle, directions, smoothness_now):

    # 在训练的时候，我们维护golden_batches的数据集。在任何一次的观测后，如果这次观测的最终是最好的，那么就是golden batch
    # 换言之，在情况A下，我们做了B操作，拿到了好的结果
    # 见贤思齐
    df_golden_batches = pd.read_csv('Golden_Batches.csv')
    # df_golden_batches = df_golden_batches[
    #     (df_golden_batches['Phase']==start_phase) & (df_golden_batches['Cycle']==start_cycle) \
    #     & (df_golden_batches['SKU']==SKU) & (df_golden_batches['ActionResult']=='Good')
    #     ]

    method_class = 'nothing'
    if Phase == 8:
        method_class = 'P8'
    elif Phase == 10 and Cycle <= 4:
        method_class = 'P10A'
    elif Phase == 10 and Cycle >= 5:
        method_class = 'P10B'
    elif Phase >= 11 and Phase <= 13:
        method_class = 'P11+'

    df_golden_batches = df_golden_batches[
        (df_golden_batches['method_class'] == method_class) \
        & (df_golden_batches['ActionResult'] == 'Good')
        ].reset_index(drop=True)

    # 如果没有参照，那么就按照default来吧
    list_pc = sorted(list(MainData['prediction'].keys()))
    if len(df_golden_batches) == 0:
        for (p, c) in list_pc[:3]:
            # if p != Phase:
            #     continue
            if dic_formula[p][c]['Pause_status']:
                if directions['PauseTime'] == 'Low':
                    MainData['suggestion'][(p, c)]['pause'] -= np.abs(dic_formula[p][c]['Pause_step_size'])
                elif directions['PauseTime'] == 'High':
                    MainData['suggestion'][(p, c)]['pause'] += np.abs(dic_formula[p][c]['Pause_step_size'])
            if dic_formula[p][c]['Drying_status']:
                if directions['DryingTime'] == 'Low':
                    MainData['suggestion'][(p, c)]['drying'] -= np.abs(dic_formula[p][c]['Drying_step_size'])
                elif directions['DryingTime'] == 'High':
                    MainData['suggestion'][(p, c)]['drying'] += np.abs(dic_formula[p][c]['Drying_step_size'])
            if dic_formula[p][c]['Drumspeed_S_status']:
                if directions['DrumspeedS'] == 'Low':
                    MainData['suggestion'][(p, c)]['speed_2'] -= np.abs(dic_formula[p][c]['Drumspeed_S_step_size'])
                elif directions['DrumspeedS'] == 'High':
                    MainData['suggestion'][(p, c)]['speed_2'] += np.abs(dic_formula[p][c]['Drumspeed_S_step_size'])
            if dic_formula[p][c]['Drumspeed_N_status']:
                if directions['DrumspeedN'] == 'Low':
                    MainData['suggestion'][(p, c)]['speed_1'] -= np.abs(dic_formula[p][c]['Drumspeed_N_step_size'])
                elif directions['DrumspeedN'] == 'High':
                    MainData['suggestion'][(p, c)]['speed_1'] += np.abs(dic_formula[p][c]['Drumspeed_N_step_size'])

    # 否则找同样工况下的golden batches
    else:

        df_golden_batches['pc'] = 100 * df_golden_batches['Phase'] + df_golden_batches['Cycle']
        df_golden_batches['l1_distance'] = \
            np.abs(Appearance_1_Num / Num_Samples - df_golden_batches['Rate1']) \
            + np.abs(Appearance_2_Num / Num_Samples - df_golden_batches['Rate2']) \
            + np.abs(Appearance_3_Num / Num_Samples - df_golden_batches['Rate3'])

        df_golden_batches['weight'] = 1 / (df_golden_batches['l1_distance'] + 1)

        golden_pause_ratio = np.sum(df_golden_batches['AvgPauseDF'] * df_golden_batches['weight']) / np.sum(
            df_golden_batches['weight'])
        if directions['PauseTime'] == 'Low':
            golden_pause_ratio = fit_range(golden_pause_ratio, 0, 0.99)
        elif directions['PauseTime'] == 'Medium':
            golden_pause_ratio = fit_range(golden_pause_ratio, 0.8, 1.2)
        elif directions['PauseTime'] == 'High':
            golden_pause_ratio = fit_range(golden_pause_ratio, 1.01, 5)

        golden_drying_ratio = np.sum(df_golden_batches['AvgDryingDF'] * df_golden_batches['weight']) / np.sum(
            df_golden_batches['weight'])
        if directions['DryingTime'] == 'Low':
            golden_drying_ratio = fit_range(golden_pause_ratio, 0, 0.95)
        elif directions['DryingTime'] == 'Medium':
            golden_drying_ratio = fit_range(golden_pause_ratio, 0.9, 1.1)
        elif directions['DryingTime'] == 'High':
            golden_drying_ratio = fit_range(golden_pause_ratio, 1.05, 5)

        golden_speed1_ratio = np.sum(df_golden_batches['AvgDryingDF'] * df_golden_batches['weight']) / np.sum(
            df_golden_batches['weight'])
        if directions['DrumspeedN'] == 'Low':
            golden_speed1_ratio = fit_range(golden_pause_ratio, 0, 0.95)
        elif directions['DrumspeedN'] == 'Medium':
            golden_speed1_ratio = fit_range(golden_pause_ratio, 0.9, 1.1)
        elif directions['DrumspeedN'] == 'High':
            golden_speed1_ratio = fit_range(golden_pause_ratio, 1.05, 5)

        golden_speed2_ratio = np.sum(df_golden_batches['AvgDryingDF'] * df_golden_batches['weight']) / np.sum(
            df_golden_batches['weight'])
        if directions['DrumspeedS'] == 'Low':
            golden_speed2_ratio = fit_range(golden_pause_ratio, 0, 0.95)
        elif directions['DrumspeedS'] == 'Medium':
            golden_speed2_ratio = fit_range(golden_pause_ratio, 0.9, 1.1)
        elif directions['DrumspeedS'] == 'High':
            golden_speed2_ratio = fit_range(golden_pause_ratio, 1.05, 5)

        for (p, c) in sorted(list(MainData['prediction'].keys()))[:3]:

            MainData['suggestion'][(p, c)]['drying'] = \
                MainData['suggestion'][(p, c)]['drying'] * golden_drying_ratio
            MainData['suggestion'][(p, c)]['pause'] = \
                MainData['suggestion'][(p, c)]['pause'] * golden_pause_ratio


def fill_date(x):
    if x >= 10:
        return str(int(x))
    else:
        return '0' + str(int(x))


def list_to_datetime(x):
    return datetime.datetime(x[0], x[1], x[2], x[3], x[4], x[5])


def datetime_to_list(x):
    return [int(x.year), int(x.month), int(x.day), int(x.hour), int(x.minute), int(x.second)]


def fit_range(x, lb, ub):
    if x <= lb:
        return lb
    elif x >= ub:
        return ub
    else:
        return x


def or_model_soft_constraints_level(start_phase, start_cycle, start_weight, Syrup_Added_Till_Now, smoothness_now,
                                    soft_constraints_level):

    solver = pywraplp.Solver.CreateSolver('SCIP')
    bigM = 10 ** 10
    infinity = solver.infinity()

    pc_feasible = sorted([pc for pc in MainData['suggestion']])
    # Whether we shall execute or skip each phase and cycle
    # DV for decision variables (by definition in operations research)
    DV_pc_execute = {
        pc: 1 if pc_standards[pc]['CanBeSkipped'] != '是'
        else solver.IntVar(0, 1, '''Whether_Execute_Phase_%s_Cycle_%s''' % (str(pc[0]), str(pc[1])))
        for pc in pc_feasible
    }
    count_pc_executed = 0
    pc_size_executed = 0
    for pc in DV_pc_execute:
        count_pc_executed += DV_pc_execute[pc]
        pc_size_executed += 10 * pc[0] * DV_pc_execute[pc] + pc[1] * DV_pc_execute[pc]

    # How much syrup shall be added to each phase and cycle.

    # Level 1: Do not change the syrup in phase 10
    if soft_constraints_level == 1:
        DV_pc_syrup = {
            pc: solver.NumVar(
                dic_formula[pc[0]][pc[1]]['Syrup_LB'],
                dic_formula[pc[0]][pc[1]]['Syrup_UB'],
                '''Syrup_Phase_%s_Cycle_%s''' % (str(pc[0]), str(pc[1]))
            ) if pc_standards[pc]['CanBeSkipped'] != '是' and pc[0] != 10
            else(
                dic_formula[pc[0]][pc[1]]['Syrup_default_value'] \
                    if pc_standards[pc]['CanBeSkipped'] != '是' and pc[0] == 10
                    else
                        # solver.NumVar(
                        # 0,
                        # dic_formula[pc[0]][pc[1]]['Syrup_UB'],
                        # '''Syrup_Phase_%s_Cycle_%s''' % (str(pc[0]), str(pc[1]))
                        # )
                        dic_formula[pc[0]][pc[1]]['Syrup_default_value'] * DV_pc_execute[pc]
                    ) for pc in pc_feasible
        }  # DV_pc_syrup[pc] shall be 0 if not executed, it will be added in constraints.

    elif soft_constraints_level == 2 or soft_constraints_level == 3:
        DV_pc_syrup = {
            pc: solver.NumVar(
                dic_formula[pc[0]][pc[1]]['Syrup_LB'],
                dic_formula[pc[0]][pc[1]]['Syrup_UB'],
                '''Syrup_Phase_%s_Cycle_%s''' % (str(pc[0]), str(pc[1]))
            ) if pc_standards[pc]['CanBeSkipped'] != '是'
            else solver.NumVar(
                0,
                dic_formula[pc[0]][pc[1]]['Syrup_UB'],
                '''Syrup_Phase_%s_Cycle_%s''' % (str(pc[0]), str(pc[1]))
            ) for pc in pc_feasible
        }

    # Final Weight = Current Weight + Gradient Syrup * All Syrup to be Added + Intercept
    # Final Weight Gap = ABS(Final Weight - Target Weight)

    final_weight_gap = start_weight + Gradient_Syrup * np.sum([
        DV_pc_syrup[pc] for pc in DV_pc_syrup
    ]) - Target_Weight

    # Add Constraints

    # Transforming a non-linear programming with abs formulas into a linear programming
    # Some math tricks in OR here to make it run faster
    # OBJ for objective function (by definition in operations research)
    OBJ_final_weight_gap = solver.NumVar(0, 10, 'OBJ_final_weight_gap')
    solver.Minimize(OBJ_final_weight_gap * 10 ** 6 + count_pc_executed + 0.01 * pc_size_executed)
    solver.Add(OBJ_final_weight_gap >= final_weight_gap)
    solver.Add(OBJ_final_weight_gap >= (-1) * final_weight_gap)

    # Syrup at any phase and cycle. If a (phase, cycle) is not executed, syrup added shall be 0

    for pc in DV_pc_execute:

        # If not execute, then syrup shall be 0.
        # Some math thricks in OR here to convert a what-if constraint to a integer-linear one. So it runs faster.
        if pc_standards[pc]['CanBeSkipped'] != '是':
            continue

        solver.Add(bigM * DV_pc_execute[pc] >= DV_pc_syrup[pc])
        solver.Add(DV_pc_syrup[pc] >= DV_pc_execute[pc] * dic_formula[pc[0]][pc[1]]['Syrup_LB'])
    
    # Syrup added shall be less and less

    phase_10_end_weight = start_weight
    for pc in DV_pc_syrup:
        if pc[0] == 10:
            phase_10_end_weight += DV_pc_syrup[pc] * Gradient_Syrup

    if soft_constraints_level == 1:
        solver.Add(phase_10_end_weight >= Phase_10_End_Min)
        solver.Add(phase_10_end_weight <= Phase_10_End_Max)

    if (soft_constraints_level in (1, 2, 3)) and len(DV_pc_syrup) >= 1:
        # for pc in DV_pc_syrup:
        #     if pc[0] == 10 and (pc[0], pc[1] + 1) in DV_pc_syrup:
        #         solver.Add(DV_pc_syrup[pc] >= DV_pc_syrup[(pc[0], pc[1] + 1)])
        #     elif pc[0] == 11 and (pc[0], pc[1] + 1) in DV_pc_syrup:
        #         solver.Add(DV_pc_syrup[pc] >= DV_pc_syrup[(pc[0], pc[1] + 1)])
        for i in range(len(pc_feasible) - 1):
            break
            this_pc = pc_feasible[i]
            next_pc = pc_feasible[i+1]
            solver.Add(DV_pc_syrup[this_pc] >= DV_pc_syrup[next_pc])

    if soft_constraints_level in (1, 2, 3):
        # Total syrup added
        total_syrup = Syrup_Added_Till_Now + np.sum([DV_pc_syrup[pc] for pc in DV_pc_syrup])
        solver.Add(total_syrup >= Total_Syrup_LB)
        solver.Add(total_syrup <= Total_Syrup_UB)


    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:

        for pc in pc_feasible:
            try:
                MainData['suggestion'][pc]['syrup'] = DV_pc_syrup[pc].solution_value()
                # print ({pc: DV_pc_syrup[pc].solution_value()})
            except AttributeError:
                MainData['suggestion'][pc]['syrup'] = DV_pc_syrup[pc]
                # print ({pc: DV_pc_syrup[pc]})
        weight_prediction_by_formula_till_end()
        end_weight = MainData['prediction'][(13, 1)]['predictionWeight']
        if end_weight >= MinTarget and end_weight <= MaxTarget:
            print('optimal_weight = ' + str(end_weight))
            return True
        else:
            print ('optimal_weight = ' + str(end_weight))
            return False

    else:
        print ('solution not found')
        return False


def give_suggestions_constrained_optimization(start_phase, start_cycle, start_weight, Syrup_Added_Till_Now,
                                              smoothness_now):

    if MainData['prediction'] == {}:
        return start_weight

    end_weight_by_formula = MainData['prediction'][(13, 1)]['predictionWeight']
    return_dict['data']['predicted_end_weight_by_formula'] = end_weight_by_formula
    if end_weight_by_formula >= MinTarget and end_weight_by_formula <= MaxTarget:
        return end_weight_by_formula

    solution_found = False

    # Level 1: Limit P10 Syrup to Default if Phase 10 can end with 1.38 - 1.39
    print('L1')
    solution_found = or_model_soft_constraints_level(start_phase, start_cycle, start_weight,
                                                                 Syrup_Added_Till_Now, smoothness_now, 1)
    if not solution_found:
        print('L2')
        solution_found = or_model_soft_constraints_level(start_phase, start_cycle, start_weight,
                                                                     Syrup_Added_Till_Now, smoothness_now, 2)
    if not solution_found:
        print('L3')
        solution_found = or_model_soft_constraints_level(start_phase, start_cycle, start_weight,
                                                                     Syrup_Added_Till_Now, smoothness_now, 3)

    pc_feasible = [pc for pc in MainData['suggestion']]
    # If we find an optimal solution
    if solution_found:
        for pc in pc_feasible:
            if pc[0] == 10 and pc[1] <= 4:
                MainData['suggestion'][pc]['drying'] += Syrup_Drying_10a_model.coef_[0] * (
                    MainData['suggestion'][pc]['syrup'] - dic_formula[pc[0]][pc[1]]['Syrup']
                )
            elif pc[0] == 10 and pc[1] >= 5:
                MainData['suggestion'][pc]['drying'] += Syrup_Drying_10b_model.coef_[0] * (
                    MainData['suggestion'][pc]['syrup'] - dic_formula[pc[0]][pc[1]]['Syrup']
                )
            elif pc[0] == 11:
                MainData['suggestion'][pc]['drying'] += Syrup_Drying_11_model.coef_[0] * (
                    MainData['suggestion'][pc]['syrup'] - dic_formula[pc[0]][pc[1]]['Syrup']
                )
            elif pc[0] == 12:
                MainData['suggestion'][pc]['drying'] += Syrup_Drying_12_model.coef_[0] * (
                    MainData['suggestion'][pc]['syrup'] - dic_formula[pc[0]][pc[1]]['Syrup']
                )
            if pc_standards[pc]['CanBeSkipped'] != '是':
                if MainData['suggestion'][pc]['action'] != 'Check Photo and Weight Again':
                    MainData['suggestion'][pc]['action'] = 'Execute'
            # elif DV_pc_execute[pc].solution_value() == 0:
            elif MainData['suggestion'][pc]['syrup'] == 0:
                MainData['suggestion'][pc]['action'] = 'Skip'
            # elif DV_pc_execute[pc].solution_value() == 1:
            elif MainData['suggestion'][pc]['syrup'] > 0:
                if MainData['suggestion'][pc]['action'] != 'Check Photo and Weight Again':
                    MainData['suggestion'][pc]['action'] = 'Execute'
        
        # The best thing we can achieve if we follow all the constraints
        weight_prediction_by_formula_till_end()
        return_dict['data']['predicted_end_weight_after_suggestion'] = MainData['prediction'][(13, 1)]['predictionWeight']
        return_dict['msg'] += 'Optimal Solution Found. '
        return MainData['prediction'][(13, 1)]['predictionWeight']
    else:
        # If no feasible solution can be found, we can only suggest by formula and ask line engineer to take over.
        return_dict['msg'] += 'Optimal Solution NOT Found. Keep Default Formula'
        return_dict['data']['NeedManualTakeover'] = True
        return_dict['data']['ManualTakeoverReason'] = '无法在配方表规定的上下限内，将重量控制到目标区间'
        weight_prediction_by_formula_till_end()
        return_dict['data']['predicted_end_weight_after_suggestion'] = MainData['prediction'][(13, 1)][
            'predictionWeight']
        # return_dict['data']['predicted_end_weight_after_suggestion'] = \
        #     return_dict['data']['predicted_end_weight_by_formula']
        return end_weight_by_formula


def write_return_format():

    list_pc = sorted(list(MainData['prediction'].keys()))
    for (p, c) in MainData['prediction']:
        return_dict['data']['prediction']['P' + str(p) + '_C' + str(c)] = MainData['prediction'][(p, c)]
    # if Phase >= 10:
    if False:
        for (p, c) in MainData['suggestion']:
            if MainData['suggestion'][(p, c)]['action'] != 'Skip':
                return_dict['data']['suggestion']['P' + str(p) + '_C' + str(c)] = MainData['suggestion'][(p, c)]
            else:
                return_dict['data']['suggestion']['P' + str(p) + '_C' + str(c)] = {
                    'speed_1': None, 'speed_2': None, 'syrup': None, 'drying': None, 'pause': None,
                    'action:': 'Skip'
                }
    else:
        list_pc = sorted(list(MainData['prediction'].keys()))
        for (p, c) in list_pc[:6]:
            return_dict['data']['suggestion']['P' + str(p) + '_C' + str(c)] = MainData['suggestion'][(p, c)]
            if not MainData['suggestion'][(p, c)]['action']:
                continue
            elif MainData['suggestion'][(p, c)]['action'] == 'Skip':
                for k in return_dict['data']['suggestion']['P' + str(p) + '_C' + str(c)]:
                    if k != 'action':
                        return_dict['data']['suggestion']['P' + str(p) + '_C' + str(c)][k] = None


def run(raw_data):

    global SKU, Phase, Cycle, Weight, Concentration, Num_Gum_Center, Blob_Source, Blob_Target, Syrup_UB, Syrup_LB, \
        Target_Weight, return_dict, Suggestions, Num_Samples, Batch_ID, Total_Syrup_LB, Total_Syrup_UB, \
        Appearance_1_Num, Appearance_2_Num, Appearance_3_Num, Appearance_4_Num, GumCenterTotalWeight, \
        Next_Checkpoint_Good_Smoothness_Probability, MinTarget, MaxTarget, Phase_10_End_MinTarget, MainData, \
        Start_Appearance, Phase_10_End_Max, Phase_10_End_Min, Syrup_Added_till_Now, Default_Total_Syrup

    Syrup_UB = 50
    Syrup_LB = 10
    Target_Weight = 1.416 + 0.001154899
    MinTarget = Target_Weight - 0.002
    MaxTarget = Target_Weight + 0.002
    Phase_10_End_Min = 1.38
    Phase_10_End_Max = 1.39
    Total_Syrup_UB = 1000
    Total_Syrup_LB = 0
    input_dict = json.loads(raw_data)
    SKU = input_dict['SKU']
    Phase = input_dict['Phase']
    Cycle = input_dict['Cycle']
    Weight = input_dict['Weight']
    Num_Samples = input_dict['Pellets_in_Sample']
    Batch_ID = input_dict['Batch'],
    Appearance_1_Num = input_dict['Appearance_1_Num']
    Appearance_2_Num = input_dict['Appearance_2_Num']
    Appearance_3_Num = input_dict['Appearance_3_Num']
    Appearance_4_Num = input_dict['Appearance_4_Num']
    Syrup_Added_till_Now = input_dict['PhaseTotalSyrup2']
    Default_Total_Syrup = input_dict['SyrupTotalRecipeValue2']

    if Phase >= 9:
        Total_Syrup_UB = 1.02 * float(Default_Total_Syrup)
        Total_Syrup_LB = 0.98 * float(Default_Total_Syrup)

    if 'Concentration' in input_dict:
        try:
            Concentration = float(input_dict['Concentration'])
        except TypeError:
            Concentration = 0.7
    else:
        Concentration = 0.7

    if 'GumCenterTotalWeight' in input_dict:
        try:
            GumCenterTotalWeight = float(input_dict['GumCenterTotalWeight'])
        except TypeError:
            GumCenterTotalWeight = 2000
    else:
        GumCenterTotalWeight = 2000

    Num_Gum_Center = input_dict['Num_Gum_Center']
    Next_Checkpoint_Good_Smoothness_Probability = ''

    actual_now = datetime.datetime.now().astimezone(pytz.timezone("Asia/Shanghai"))
    str_now = actual_now.strftime("%Y-%m-%d %H:%M:%S")
    list_actual_now = datetime_to_list(actual_now)

    input_log_path = 'logs/Input ' + str_now + '.json'
    output_log_path = 'logs/Output ' + str_now + '.json'
    output_file_path = 'output_files/ai_result.json'

    with open(input_log_path, 'w') as f:
        json.dump(input_dict, f, indent=4)

    return_dict = {
        'code': 200,
        'data': {
            'predicted_end_weight_by_formula': 0,
            'predicted_end_weight_after_suggestion': 0,
            'surface_now': '',
            # 'phase_10_prediction': {},
            'suggestion': {},
            'prediction': {},
            'NeedManualTakeover': False,
            'ManualTakeoverReason': ''
        },
        'msg': ''
    }

    MainData = {
        'prediction': {},
        'suggestion': {}
    }


    load_data_success = load_data()
    if not load_data_success or (Phase >= 10 and Concentration == 0):
        return_dict['code'] = 300
        return_dict['data']['NeedManualTakeover'] = True
        return_dict['msg'] = 'Load Data Failure'
        return write_return_format(return_dict)

    global Gradient_Syrup
    Gradient_Syrup = 1000 * Concentration / Num_Gum_Center * Weight_Model.coef_[0]

    if Phase >= 8:
        weight_prediction_by_formula_till_end()
        appearance_cate, appearance_gap = appearance_gaps(Phase, Cycle)
        if appearance_cate != 'MeetTarget':
            directions = get_appearance_suggestion(Phase, Cycle, appearance_cate)
            case_based_reasoning_pause_drying(Phase, Cycle, directions, appearance_cate)

    if Phase >= 10 or (Phase == 9 and Cycle == 3):
        optimal_weight = give_suggestions_constrained_optimization(
            Phase, Cycle, Weight, Syrup_Added_till_Now, 'MeetTarget'
        )
        print (optimal_weight)
        if optimal_weight > MaxTarget or optimal_weight < MinTarget:
            return_dict['data']['NeedManualTakeover'] = True

    for (p, c) in MainData['suggestion']:
        if dic_formula[p][c]['Drumspeed_N_LB'] and dic_formula[p][c]['Drumspeed_N_UB']:
            MainData['suggestion'][(p, c)]['speed_1'] = float(np.round(fit_range(
                x=MainData['suggestion'][(p, c)]['speed_1'],
                lb=dic_formula[p][c]['Drumspeed_N_LB'],
                ub=dic_formula[p][c]['Drumspeed_N_UB']
            ), 1))
        if dic_formula[p][c]['Drumspeed_S_LB'] and dic_formula[p][c]['Drumspeed_S_UB']:
            MainData['suggestion'][(p, c)]['speed_2'] = float(np.round(fit_range(
                x=MainData['suggestion'][(p, c)]['speed_2'],
                lb=dic_formula[p][c]['Drumspeed_S_LB'],
                ub=dic_formula[p][c]['Drumspeed_S_UB']
            ), 1))
        if dic_formula[p][c]['Syrup_LB'] and dic_formula[p][c]['Syrup_UB']:
            MainData['suggestion'][(p, c)]['syrup'] = float(np.round(fit_range(
                x=MainData['suggestion'][(p, c)]['syrup'] * GumCenterTotalWeight / 2000,
                lb=dic_formula[p][c]['Syrup_LB'],
                ub=dic_formula[p][c]['Syrup_UB']
            ), 2))
        if dic_formula[p][c]['Drying_LB'] and dic_formula[p][c]['Drying_UB']:
            MainData['suggestion'][(p, c)]['drying'] = float(np.round(fit_range(
                x=MainData['suggestion'][(p, c)]['drying'],
                lb=dic_formula[p][c]['Drying_LB'],
                ub=dic_formula[p][c]['Drying_UB']
            ), 2))
        if dic_formula[p][c]['Pause_LB'] and dic_formula[p][c]['Pause_UB']:
            MainData['suggestion'][(p, c)]['pause'] = float(np.round(fit_range(
                x=MainData['suggestion'][(p, c)]['pause'],
                lb=dic_formula[p][c]['Pause_LB'],
                ub=dic_formula[p][c]['Pause_UB']
            ), 2))

    write_return_format()
    output_json = json.dumps(return_dict)
    # return_dict['MainData'] = MainData
    print (return_dict)

    with open(output_log_path, 'w') as f:
        json.dump(return_dict, f, indent=4)
    with open(output_file_path, 'w') as f:
        json.dump(return_dict, f)

    return output_json


if __name__ == '__main__':

    init()
    raw_data = sys.argv[1]
    output_json = run(raw_data)

    # print (json.loads(output_json))