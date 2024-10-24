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


def temp_cur_process(now, df_T, df_cur):  
    """  
    更新温度参数最近过去15分钟每15s的均值共60个到df_cur，或者保留最近15分钟的数据
    """
    # 温度参数
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
    df_tag = pd.DataFrame(avg_temp_parm_list, columns=['Tag'])
    df_parm = pd.merge(df_T, df_tag, how = 'inner', on = 'Tag')
    df_parm['Value'] = df_parm['Value'].astype(float) 
    # 计算每个温度参数T时间内的均值（15s）
    df_g = df_parm.groupby('Tag').agg({'Value': np.mean, 'IOTDeviceID': 'first', 'SiteId': 'first', 'LineId': 'first', 
                                   'SensorId': 'first' , 'MachineId': 'first' ,'uuid': 'first' , 'TS2': 'first' })
    df_g['Value'] = df_g['Value'].round(1)
    df_g = pd.merge(df_tag, df_g, how = 'left', on = 'Tag')
    df_g['TS'] = now
    # 新的T时刻数据合并到 T-1时刻的df_cur中
    df_cur = pd.concat([df_cur, df_g], ignore_index=True)
    # 筛选并输出T时刻df_cur中最近15分钟内的行 
    recent_15min = now - pd.Timedelta('15min')    
    mask_recent_15min = df_cur['TS'] >= recent_15min  
    df_cur_updated = df_cur[mask_recent_15min].reset_index(drop=True)
    return df_cur_updated


def keepchange_cur_process(now, df_T, df_cur):  
    """  
    更新间隙、速度和其他相关参数最近10次&最近30分钟变化时候的值到df_cur，
    如果最近30分钟变化超过10次，则取最近30分钟。否则取最近10次
    """
    #间隙参数四舍五入保留到0.001
    keep_change_parm_list_gap = ['CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_GapBullRoll.rActualPosition_inches',
                             'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap1stSizing.rActualPosition_inches',
                             'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap2ndSizing.rActualPosition_inches',
                             'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap3rdSizing.rActualPosition_inches',
                             'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_GapFinalSizing.rActualPosition_inches']
    #速度和温度参数四舍五入保留到0.1
    keep_change_parm_list_speed_temp = ['CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_BullRoll.rSetpoint_Ratio',
                                 'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_1stSizing.rSetpoint_Ratio',
                                 'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_2ndSizing.rSetpoint_Ratio',
                                 'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_3rdSizing.rSetpoint_Ratio',
                                 'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_FinalSizing.rSetpoint_Ratio',
                                 'CG_Sheeting.CG_Sheeting.dbHMI.Scoring.SRV_CircularScore.rSetpoint_Ratio',
                                 'CG_Sheeting.CG_Sheeting.dbHMI.Scoring.SRV_CrossScore.rSetpoint_Ratio',
                                 'CG_Sheeting.CG_Sheeting.dbHMI.Scoring.SRV_CrossScore.rActualVelocityRPM',
                                 'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rChillerSetpoint',
                                 'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_UB_Temp_SP',
                                 'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_LB_Temp_SP',
                                 'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_PH_Temp_SP']
    #无需额外变动
    keep_change_parm_list_other = ['SFBMix.plcSFBMix.dbAdditionalParameter.StateFromSheeting.bMachineRunning',
                                 'CG_Sheeting.CG_Sheeting.sCurrentFormula']
    #完整参数列表
    #keep_change_parm_list = keep_change_parm_list_gap + keep_change_parm_list_speed_temp + keep_change_parm_list_other
    #对T时刻的数据根据参数类型保留小数
    df_tag_gap = pd.DataFrame(keep_change_parm_list_gap, columns=['Tag'])
    df_parm_gap = pd.merge(df_T, df_tag_gap, how = 'inner', on = 'Tag')
    df_parm_gap['Value'] = df_parm_gap['Value'].astype(float) 
    df_parm_gap['Value'] = df_parm_gap['Value'].round(3)
    
    df_tag_st = pd.DataFrame(keep_change_parm_list_speed_temp, columns=['Tag'])
    df_parm_st = pd.merge(df_T, df_tag_st, how = 'inner', on = 'Tag')
    df_parm_st['Value'] = df_parm_st['Value'].astype(float) 
    df_parm_st['Value'] = df_parm_st['Value'].round(1)

    df_tag_other = pd.DataFrame(keep_change_parm_list_other, columns=['Tag'])
    df_parm_other = pd.merge(df_T, df_tag_other, how = 'inner', on = 'Tag')
    
    #筛选保留第一次变化的行
    df_cur_gap = df_cur[df_cur['Tag'].isin(keep_change_parm_list_gap)].astype({'Value': 'float'})
    df_cur_st = df_cur[df_cur['Tag'].isin(keep_change_parm_list_speed_temp)].astype({'Value': 'float'})
    df_cur_other = df_cur[df_cur['Tag'].isin(keep_change_parm_list_other)]
    
    df_cur = pd.concat([df_cur_gap, df_cur_st, df_cur_other, df_parm_gap, df_parm_st, df_parm_other], ignore_index=True)
    df_cur.sort_values(by=['Tag', 'TS'], ascending=True, inplace=True)
    df_cur['last_Tag'] = df_cur['Tag'].shift(1)
    df_cur['last_Value'] = df_cur['Value'].shift(1)
    df_cur = df_cur[(df_cur['Tag'] != df_cur['last_Tag']) | (df_cur['Value'] != df_cur['last_Value'])].reset_index(drop=True)

    # 筛选并输出T时刻df_cur中最近30分钟或者最近10次变化的行
    # 使用groupby和rank根据'Tag'分组，并按照'TS'排序
    df_cur = df_cur.sort_values(by='TS', ascending=False)    
    # 分组并分配序号（从0开始），然后加1以从1开始编号  
    df_cur['row_number'] = df_cur.groupby('Tag').cumcount() + 1
    df_cur_recent_30min = df_cur[df_cur['TS'] >= (now - pd.Timedelta('30min') )]
    if len(df_cur_recent_30min)>10:
        df_cur_updated = df_cur_recent_30min
    else:
        df_cur_updated = df_cur[df_cur['row_number'] <= 10]
    
    df_cur_updated = df_cur_updated.loc[:, ['IOTDeviceID','SiteId','LineId',
                    'SensorId','MachineId','Tag','Value','TS','uuid','TS2']]

    return df_cur_updated.reset_index(drop=True)


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
    blob_name_rawdata_parm = os.path.join(file_path,"CG_Sheeting_HHData.csv")
    blob_name_curdata_parm = os.path.join(file_path_T1,"curated_parm.csv")
    parm_data = read_csv_blob_to_dataframe(connect_str, container_name_rawdata, blob_name_rawdata_parm, df_parm_empty)
    curated_data_parm = read_csv_blob_to_dataframe(connect_str, container_name_curateddata, blob_name_curdata_parm, df_parm_empty)

    #######################开始etl处理######################
    

    #######################处理参数表######################
    if not parm_data.empty:
        try:
            parm_data['TS'] = pd.to_datetime(parm_data['TS'], format="%Y-%m-%d %H:%M:%S.%f %z", errors='coerce').dt.tz_localize(None)
            parm_data['TS'] = pd.to_datetime(parm_data['TS']).dt.strftime("%Y-%m-%d %H:%M:%S")
            #parm_data['TS'] = pd.to_datetime(parm_data['TS'].str.split('.').str[0])
        except Exception as e:
            logger.error("发生了一个错误: %s", str(e))
            print(e)
            try:
                parm_data['TS'] = parm_data['TS'].map(lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S.%f %z").replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")) 
            except Exception as e:
                logger.error("发生了一个错误: %s", str(e))
                print(e)
                blob_name_curdata_parm = os.path.join(file_path, "curated_parm.csv")
                save_dataframe_to_csv_blob(connect_str, container_name_curateddata, blob_name_curdata_parm, curated_data_parm, index=False)
                return      
    if not curated_data_parm.empty:
        curated_data_parm['TS'] = pd.to_datetime(curated_data_parm['TS'])

    curated_data_parm_temp = temp_cur_process(now, parm_data, curated_data_parm)
    curated_data_parm_keepchange = keepchange_cur_process(now, parm_data, curated_data_parm)
    curated_data_parm = pd.concat([curated_data_parm_temp, curated_data_parm_keepchange], ignore_index=True)
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