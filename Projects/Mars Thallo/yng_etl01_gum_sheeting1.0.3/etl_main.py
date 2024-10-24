import string
import sys
import pytz
import json
import pandas as pd  
import numpy as np  
from datetime import datetime, timedelta 
from azure.storage.blob import BlobServiceClient, BlobClient  
import io
import os
import configparser
import warnings
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='etl_error.log',
    filemode='a'
)
# 获取日志记录器并记录消息
logger = logging.getLogger()

# 忽略Pandas警告
warnings.filterwarnings("ignore")

#保留15s平均值的参数
#温度参数四舍五入保留到0.1
avg_temp_parm_list=['CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum1InletTemp', 
               'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rGumEntranceTemperature',
               'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum1OutletTemp',
               'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum2InletTemp',
               'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum2OutletTemp',
               'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rGumExitTempLeft',
               'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rGumExitTempRight',
               'CG_Sheeting.CG_Sheeting.Variables.rGumExtruderExitGumTemp',
               'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_UB_Temp_RealValue',
               'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_LB_Temp_RealValue',
               'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_PH_Temp_RealValue',
               'CG STI.CG STI.LoafGum.LoafGum01MaxTemp']

#保留30分钟内（or最近10次变化）的参数
#间隙参数四舍五入保留到0.001
keep_change_parm_list_gap = ['CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_GapBullRoll.rActualPosition_inches',
                             'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap1stSizing.rActualPosition_inches',
                             'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap2ndSizing.rActualPosition_inches',
                             'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap3rdSizing.rActualPosition_inches',
                             'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_GapFinalSizing.rActualPosition_inches']
#速度参数四舍五入保留到0.1
keep_change_parm_list_speed = ['CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_BullRoll.rSetpoint_Ratio',
                             'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_1stSizing.rSetpoint_Ratio',
                             'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_2ndSizing.rSetpoint_Ratio',
                             'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_3rdSizing.rSetpoint_Ratio',
                             'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_FinalSizing.rSetpoint_Ratio',
                             'CG_Sheeting.CG_Sheeting.dbHMI.Scoring.SRV_CircularScore.rSetpoint_Ratio',
                             'CG_Sheeting.CG_Sheeting.dbHMI.Scoring.SRV_CrossScore.rSetpoint_Ratio',
                             'CG_Sheeting.CG_Sheeting.dbHMI.Scoring.SRV_CrossScore.rActualVelocityRPM']
#温度参数四舍五入保留到0.1
keep_change_parm_list_temp = ['CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rChillerSetpoint',
                              'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_UB_Temp_SP',
                              'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_LB_Temp_SP',
                              'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_PH_Temp_SP']
#无需额外变动
keep_change_parm_list_other = ['SFBMix.plcSFBMix.dbAdditionalParameter.StateFromSheeting.bMachineRunning',
                             'CG_Sheeting.CG_Sheeting.sCurrentFormula']

keep_change_parm_list = keep_change_parm_list_gap + keep_change_parm_list_speed + keep_change_parm_list_temp + keep_change_parm_list_other
parm_list = avg_temp_parm_list + keep_change_parm_list

#创建empty curated_data
df_parm_empty = pd.DataFrame({
                'IOTDeviceID': [],
                'SiteId': [],
                'LineId': [],
                'SensorId': [],
                'MachineId': [],
                'Tag': [],
                'Value': [],
                'TS': [],
                'uuid':[],
                'TS2':[]
            })


def get_cst_time_formatter(pattern):
    cur_time = datetime.now()
    cst_timezone = pytz.timezone('Asia/Shanghai')
    cur_time = cur_time.astimezone(cst_timezone)
    cur_time = cur_time.strftime(pattern)
    return cur_time

def read_csv_blob_to_dataframe(connect_str, container_name, blob_name, empty_df):  
    """  
    从Azure Blob存储中读取CSV文件并将其转换为Pandas DataFrame。  
  
    参数:  
    - connect_str: Azure Blob存储的连接字符串。  
    - container_name: 包含CSV文件的容器名称。  
    - blob_name: CSV文件的名称（包括扩展名）。  
  
    返回:  
    - DataFrame: 包含CSV文件数据的Pandas DataFrame。  
    """  
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)  
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)  
    
    # 检查Blob是否存在  
    if blob_client.exists():  
        blob_data = blob_client.download_blob().content_as_bytes()  
        csv_data = blob_data.decode('utf-8')  
        df = pd.read_csv(io.StringIO(csv_data))  
        return df  
    else:  
        # 如果文件不存在，返回一个指定的空的DataFrame  
        return empty_df


def save_dataframe_to_csv_blob(connect_str, container_name, blob_name, df, index=False):  
    """  
    将Pandas DataFrame保存为Azure Blob存储中的CSV文件。  
  
    参数:  
    - connect_str: Azure Blob存储的连接字符串。  
    - container_name: 要保存CSV文件的容器名称。  
    - blob_name: CSV文件的名称（包括扩展名）。  
    - df: 要保存的Pandas DataFrame。  
    - index: 是否将DataFrame的索引也写入CSV文件，默认为False。  
  
    无返回值（但会创建或覆盖Blob存储中的文件）。  
    """  
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)  
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)  
    csv_buffer = io.StringIO()  
    df.to_csv(csv_buffer, index=index, encoding='utf-8')  
    blob_client.upload_blob(csv_buffer.getvalue(), blob_type="BlockBlob", overwrite=True)


def temp_cur_process(now, df_T, df_cur, parm, max_rows=60):  
    """  
    更新温度参数最近过去15分钟每15s的均值共60个到df_cur，或者保留最近15分钟的数据
    """
    
    # 筛选df_T中tag等于parm的行，去掉 
    filtered_df = df_T[df_T['Tag'] == parm]
    # 筛选出df_cur中Tag='parm'的行  
    df_cur_parm = df_cur[df_cur['Tag'] == parm]
    df_cur_parm.sort_values(by='TS', inplace=True)  
    df_cur = df_cur[df_cur['Tag'] != parm]

    # 计算最近15分钟的时间范围  
    recent_15min = now - pd.Timedelta('15min')  
    # 筛选最近15分钟内的行  
    mask_recent_15min = df_cur_parm['TS'] >= recent_15min  
    df_parm_updated = df_cur_parm[mask_recent_15min]

    #如果df_T中没有任何关于parm的行，直接更新df_cur,保留最近15min数据
    if filtered_df.empty: 
        df_cur = pd.concat([df_cur, df_parm_updated], ignore_index=True)
        return df_cur
    
    # 如果所有Value都是空值，则mean_value为NaN,否则为均值
    if filtered_df['Value'].dropna().empty:    
        mean_value = np.nan  
    else:
        #保证Value是float，再求mean
        filtered_df['Value'] = filtered_df['Value'].astype(float)  
        mean_value = filtered_df['Value'].mean().round(1) 
      
    # 构造要插入df_cur的行  
    new_row = filtered_df.iloc[0]
    new_row['Value'] = mean_value
    new_row['TS'] = now
    new_row_df = pd.DataFrame([new_row])  
    
    row_len = max_rows-1
    if len(df_parm_updated) > row_len:
        # 如果行数超过限制，删除最早的记录直到满足要求    
        to_remove = len(df_parm_updated) - row_len
        if to_remove > 0: 
            parm_rows = df_parm_updated.sort_values(by='TS', ascending=True) 
            parm_rows_final = df_parm_updated.iloc[len(df_cur_parm) - row_len:]
            df_cur = pd.concat([df_cur, df_parm_updated, parm_rows_final], ignore_index=True)
    else:
        df_cur = pd.concat([df_cur, df_parm_updated, new_row_df], ignore_index=True) 
    return df_cur


def keepchange_cur_process(now, df_T, df_cur, parm, max_rows=10):  
    """  
    更新间隙、速度和其他相关参数最近10次&最近30分钟变化时候的值到df_cur，
    如果最近30分钟变化超过10次，则取最近30分钟。否则取最近10次
    """
  
    # 筛选出df_T中Tag为'parm'且Value不是NaN的行  
    df_parm = df_T[(df_T['Tag'] == parm) & (df_T['Value'].notna())]
    # 筛选出df_cur中Tag='parm'的行  
    df_cur_parm = df_cur[df_cur['Tag'] == parm]    
    df_cur_parm.sort_values(by='TS', inplace=True)
    df_cur = df_cur[df_cur['Tag'] != parm]
    
    # 计算最近30分钟的时间范围  
    recent_30min = now - pd.Timedelta('30min')  
    # 筛选最近30分钟内的行  
    mask_recent_30min = df_cur_parm['TS'] >= recent_30min  
    df_parm_recent_30min = df_cur_parm[mask_recent_30min]
    # 如果最近30分钟内的变化超过10次，则只保留这30分钟内的行  
    # 否则，保留最近10次变化  
    if len(df_parm_recent_30min) > max_rows:  
        df_parm_updated = df_parm_recent_30min        
    else:  
        df_parm_updated = df_cur_parm.iloc[-10:]
    
    #如果df_T中没有任何关于parm的行，直接更新df_cur,保留最近30min数据
    if df_parm.empty: 
        df_cur = pd.concat([df_cur, df_parm_updated], ignore_index=True)
        return df_cur
    
    #根据参数的类型，df_T的value四舍五入到对应的格式
    if parm in keep_change_parm_list_gap:
        df_parm['Value'] = df_parm['Value'].astype(float)
        df_parm['Value'] = df_parm['Value'].round(3)
        #df_parm['Value'].round(3, inplace=True)
    elif parm in keep_change_parm_list_speed:
        df_parm['Value'] = df_parm['Value'].astype(float)
        df_parm['Value'] = df_parm['Value'].round(1)
        #df_parm['Value'].round(1, inplace=True)
    elif parm in keep_change_parm_list_temp:
        df_parm['Value'] = df_parm['Value'].astype(float)
        df_parm['Value'] = df_parm['Value'].round(1)
        #df_parm['Value'].round(1, inplace=True)
 
    # 按TS列排序  
    df_parm.sort_values(by='TS', inplace=True)
    # 找到每个新值（非NaN）首次出现的行  
    # 使用shift()比较当前行与前一行的Value是否相同  
    # 如果不同，并且当前行不是第一行（即shift()后的结果不是NaN），则保留该行  
    # 注意：这里我们使用~来反转布尔索引的结果，因为我们想要的是True的位置  
    mask = ~(df_parm['Value'].shift(1) == df_parm['Value']) | (df_parm['Value'].shift(1).isna())  
    df_parm = df_parm[mask]

    # 检查df_parm中时间最早的value是否和df_cur中Tag=parm最新的value一样  
    if not df_cur_parm.empty and not df_parm.empty:  
        latest_parm_value_df_cur = df_cur_parm.iloc[-1]['Value']  
        earliest_parm_value_df_parm = df_parm.iloc[0]['Value']  
        if latest_parm_value_df_cur == earliest_parm_value_df_parm:  
            # 如果相同，则从df_parm中移除时间最早的行  
            df_parm = df_parm.iloc[1:] 
  
    # 将筛选后的行合并到df_cur中  
    df_cur = pd.concat([df_cur, df_parm_updated, df_parm], ignore_index=True)
  
    return df_cur


# input_jsonify 是一个 JSON 字符串
# {"filePath": "some path", "ts": "上一步处理完的时间"}
def do_etl_process(input_jsonify: string) -> dict:
    try:  
        msg_in_dict = json.loads(input_jsonify)
    except json.JSONDecodeError:  
        print("Error: The input string is not a valid JSON format.") 
    
    # 在这里处理 ETL 的逻辑
    ####################################
    ###########run process##############
    ####################################
    # 创建ConfigParser对象，读取配置文件
    config = configparser.ConfigParser()
    config_filename = 'settings.ini'
    config.read(config_filename,'UTF-8')
    connect_str = config.get('blob','connect_str')
    container_name_rawdata = config.get('blob','container_name_rawdata')
    container_name_curateddata = config.get('blob','container_name_curateddata')

    #MQ传来的df_T文件路径, eg: "2024/06/28/16/55/15/"
    file_path = msg_in_dict["filePath"]

    #从file_path获取now时间，eg:datetime(2024, 8, 7, 11, 50, 15)
    # 去掉末尾的斜杠  
    formatted_string = file_path.rstrip('/')    
    # 使用strptime来解析字符串为datetime对象  
    # 格式字符串为 '%Y/%m/%d/%H/%M/%S'  
    now = datetime.strptime(formatted_string, '%Y/%m/%d/%H/%M/%S') 

    #找到curated data 在T-1时刻的路径，及T时刻file_path的15s之前
    # 找到15秒前的时间  
    fifteen_seconds_ago = now - timedelta(seconds=15)
    # 如果你想要确保所有部分都是两位数（例如，月份和分钟），你可以使用zfill方法  
    file_path_T1 = "{:02d}/{:02d}/{:02d}/{:02d}/{:02d}/{:02d}".format(  
        fifteen_seconds_ago.year,  
        fifteen_seconds_ago.month,  
        fifteen_seconds_ago.day,  
        fifteen_seconds_ago.hour,  
        fifteen_seconds_ago.minute,  
        fifteen_seconds_ago.second  
    ) 

    #读取blob文件
    try:
        blob_name_rawdata_parm = os.path.join(file_path,"CG_Sheeting_HHData.csv")
        blob_name_curdata_parm = os.path.join(file_path_T1,"curated_parm.csv")
        parm_data = read_csv_blob_to_dataframe(connect_str, container_name_rawdata, blob_name_rawdata_parm, df_parm_empty)
        curated_data_parm = read_csv_blob_to_dataframe(connect_str, container_name_curateddata, blob_name_curdata_parm, df_parm_empty)
    except Exception as e:
            logger.error("发生了一个错误: %s", str(e))

    #######################开始etl处理######################

    #处理参数表
    if not parm_data.empty:
        try:
            parm_data['TS'] = pd.to_datetime(parm_data['TS'], format="%Y-%m-%d %H:%M:%S.%f %z", errors='coerce').dt.tz_localize(None)
            parm_data['TS'] = pd.to_datetime(parm_data['TS']).dt.strftime("%Y-%m-%d %H:%M:%S")
            #parm_data['TS'] = pd.to_datetime(parm_data['TS'].str.split('.').str[0])
        except Exception as e:
            logger.error("发生了一个错误: %s", str(e))
            try:
                parm_data['TS'] = parm_data['TS'].map(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f %z").replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")) 
            except Exception as e:
                logger.error("发生了一个错误: %s", str(e))
                blob_name_curdata_parm = os.path.join(file_path, "curated_parm.csv")
                save_dataframe_to_csv_blob(connect_str, container_name_curateddata, blob_name_curdata_parm, curated_data_parm, index=False)
                return 
     
    if not curated_data_parm.empty:
        curated_data_parm['TS'] = pd.to_datetime(curated_data_parm['TS']) 
       
    for parm in avg_temp_parm_list:
        curated_data_parm = temp_cur_process(now, parm_data, curated_data_parm, parm, max_rows=60)
    for parm in keep_change_parm_list:
        curated_data_parm = keepchange_cur_process(now, parm_data, curated_data_parm, parm, max_rows=10)
    curated_data_parm = curated_data_parm.drop_duplicates()
    #保存curated_data成blob文件到T时刻文件路径
    blob_name_curdata_parm = os.path.join(file_path, "curated_parm.csv")
    save_dataframe_to_csv_blob(connect_str, container_name_curateddata, blob_name_curdata_parm, curated_data_parm, index=False)
    
    etlTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 返回一个 dict, 发送到 MQ 中
    return {
        "fileFirstTs":msg_in_dict["fileFirstTs"],
        "curTs":etlTime,
        "filePath": msg_in_dict["filePath"],
        "fileLastTs":msg_in_dict["fileLastTs"]
    }

   
def main():
    if sys.version < "3.5.3":
        raise Exception("The sample requires python 3.5.3+. Current version of Python: %s" % sys.version)
    do_etl_process({})


if __name__ == "__main__":
    main()