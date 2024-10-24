
from config import Config
from marsproject import *
from marsproject.operation.models import *
from marsproject.recordlog.service import insert_event_data_pre, insert_alert_log_data_pre, unusual_service_condition_3
from marsproject.utils.log_util import get_log
from marsproject.utils.string_utils import getDictStrValue, substringToFixed, effectiveDigitToFixed, is_number_by_str
from marsproject.utils.time_utils import get_utc_to_cst_time, get_str_to_date_time, get_cst_second
from marsproject.utils.constant_value import *
from marsproject.utils.redis_util import RedisUtils
from datetime import datetime
import json
import requests
import traceback
import os

logger = get_log(__name__)

# 全局缓存
tag_data_cache = {}


# {"curTs":"2024-08-15 16:37:37","name":"SFBMix.plcSFBMix.dbDustCollector_FlowCont.DustCollector_MFG.rFlowActual","value":"97.219795","uuid":"640ffcf9-e504-4bbb-91c7-909536892882","ts":"2024-06-28 16:55:15.152 +08:00"}
# 获取实时点位数据
def receiveRealTimeData(obj):
    logger.debug("receiveRealTimeData param={}".format(obj))
    try:
        obj['ts'] = obj['ts'].split('.')[0] if '.' in obj['ts'] else obj['ts'].replace(" +08:00", "")
        # 处理时序数据
        tag_data = tag_data_cache.get(obj['name'])
        if not tag_data:
            # cn_name, value, action_code, ts_data_id,ts
            action_data = get_single_ts_data_action_and_value(obj['name'])
            if action_data:
                tag_data_cache[obj['name']] = action_data
        else:
            action_data = tag_data

        if action_data:
            # 对值去空
            obj['value'] = obj['value'].strip()
            # 如果传的是N/A就是没有值
            if obj['value'] == 'N/A':
                obj['value'] = ''
            ts_data_id = action_data['ts_data_id']
            if ts_data_id:
                # 更新
                update_ts_raw_last_data(obj['ts'], obj['value'], ts_data_id)
            else:
                # 插入
                ts_data_id = insert_ts_raw_last_data(obj)

            # 放入缓存中
            tag_data_cache[obj['name']] = {"cn_name": action_data['cn_name'],
                                           "value": obj['value'],
                                           "action_code": action_data['action_code'],
                                           "ts_data_id": ts_data_id,
                                           "ts": obj['ts']}
            # 判断动作是否是OPC点位值变化
            if action_data['action_code'] == 1:
                old_value = getDictStrValue(action_data, 'value', 'N/A')
                new_value = getDictStrValue(obj, 'value', 'N/A')
                if is_number_by_str(old_value):
                    old_value = effectiveDigitToFixed(old_value, 4, None)
                if is_number_by_str(new_value):
                    new_value = effectiveDigitToFixed(new_value, 4, None)
                if old_value != new_value:
                    insert_event_data_pre(type=3,
                                          type_name="OPC点位值变化",
                                          content=f"{action_data['cn_name']}由{old_value}调整为{new_value}",
                                          operator_user=SYSTEM_OPERATOR_NAME)

    except Exception as e:
        insert_alert_log_data_pre(content=f'receiveRealTimeData error:{str(e)}', operator_user=SYSTEM_OPERATOR_NAME)
        logger.error("receiveRealTimeData failed detail: {}".format(traceback.format_exc()))


# "{\"curTs\":\"2024-08-15 16:38:40\", \"fileFirstTs\":\"2024-06-28 16:55:16\",\"fileLastTs\":\"2024-06-28 16:55:31\", \"filePath\":\"2024/06/28/16/55/15/\"}"
# 调用aml获取推荐数据
def recommended_value_job(obj):
    logger.debug("recommended job rec:{}".format(obj))
    try:
        obj = json.loads(obj)
        sys_st = RedisUtils.get_value(RedisKey.SYSTEM_STATUS_KEY)
        if sys_st is None or '1' != str(sys_st, 'utf-8'):
            logger.info("system status is stop")
            return
        # 获取时间
        fileLastTs_time = datetime.strptime(obj['fileLastTs'], "%Y-%m-%d %H:%M:%S")
        target_weight = TARGET_WEIGHT
        # 获取最新表头的数据id
        last_data = get_common_header_last_data()
        sku = last_data[TAG_SKU] if last_data and last_data[TAG_SKU] else None
        formula = last_data[TAG_FORMULA] if last_data and last_data[TAG_FORMULA] else None
        extruder_temperature = last_data[TAG_EXTRUDER_TEMPERATURE] if last_data and last_data[TAG_EXTRUDER_TEMPERATURE] else None
        extruder_exit_gum_temp = last_data[TAG_EXTRUDER_EXIT_GUM_TEMP] if last_data and last_data[TAG_EXTRUDER_EXIT_GUM_TEMP] else None
        slice_product_line_speed = last_data[TAG_SLICE_PRODUCT_LINE_SPEED] if last_data and last_data[TAG_SLICE_PRODUCT_LINE_SPEED] else None
        n1_roller_gap = last_data[TAG_N1_ROLLER_GAP] if last_data and last_data[TAG_N1_ROLLER_GAP] else None
        n2_roller_gap = last_data[TAG_N2_ROLLER_GAP] if last_data and last_data[TAG_N2_ROLLER_GAP] else None
        n3_roller_gap = last_data[TAG_N3_ROLLER_GAP] if last_data and last_data[TAG_N3_ROLLER_GAP] else None
        forming_roller_gap = last_data[TAG_FORMING_ROLLER_GAP] if last_data and last_data[TAG_FORMING_ROLLER_GAP] else None
        extruder_temperature_up = last_data[TAG_EXTRUDER_TEMPERATURE_UP] if last_data and last_data[TAG_EXTRUDER_TEMPERATURE_UP] else None
        cross_cutter_speed = last_data[TAG_CROSS_CUTTER_SPEED] if last_data and last_data[TAG_CROSS_CUTTER_SPEED] else None

        # 调用模型获取推荐数据
        filePath = obj['filePath']
        if not fileLastTs_time or not filePath:
            insert_alert_log_data_pre(content=f"调用AML接口失败,参数不完整->fileLastTs_time:{fileLastTs_time},filePath:{filePath}", operator_user=SYSTEM_OPERATOR_NAME)
            return
        aml_data = call_aml_data(fileLastTs_time, filePath, obj['fileLastTs'])

        if not aml_data:
            insert_alert_log_data_pre(content='调用AML接口返回空数据!', operator_user=SYSTEM_OPERATOR_NAME)
            return
        if aml_data:
            code = aml_data['code']
            msg = aml_data['msg']
            logger.debug("调用AML接口 code: {}, response msg: {}".format(code, msg))
            # 是否需要调整
            is_change = aml_data.get('is_change', None)
            if is_change is not None:
                is_change = 1 if is_change else 0
            # 1号辊推荐间隙
            recommend_1_roller_gap = substringToFixed(getDictStrValue(aml_data, 'Gap1'), 4, None)
            # 2号辊推荐间隙
            recommend_2_roller_gap = substringToFixed(getDictStrValue(aml_data, 'Gap2'), 4, None)
            # 3号辊推荐间
            recommend_3_roller_gap = substringToFixed(getDictStrValue(aml_data, 'Gap3'), 4, None)
            # 定型辊推荐间隙
            recommend_forming_roller_gap = substringToFixed(getDictStrValue(aml_data, 'GapFS'), 4, None)
            # 这两字段预留 挤压机温度, 横刀速度
            recommend_extruder_temperature_up = substringToFixed(getDictStrValue(aml_data, 'TempUpperSetValue'), 4, None)
            recommend_cross_cutter_speed = substringToFixed(getDictStrValue(aml_data, 'CrossScore'), 2, None)
            # 按照现有参数重量预测 页面用这个值
            predicted_weight = aml_data.get('WeightPredictionBeforeChange', None)
            # 安装推荐的参数重量预测
            predicted_weight2 = aml_data.get('WeightPredictionAfterChange', None)
            ai_actual_weight = aml_data.get('ActualWeight', None)
            operator_time = get_cst_time_formatter('%Y-%m-%d %H:%M:%S')
            recommend_weight_data_id = None
            shift = aml_data.get('shift', None)
            weightTs = aml_data.get('Weight_Date', None)
            actual_weight = aml_data.get('ActualWeight', None)
            if code == 200 and is_change == 1:
                # 如果本次推荐的数据和最后一次拒绝的的推荐值一样则不进入推荐表中(6个推荐值)
                reject_data = get_single_recommend_weight_data_by_status(3)
                if not reject_data \
                        or getDictStrValue(reject_data, 'recommend_1_roller_gap', None) != recommend_1_roller_gap \
                        or getDictStrValue(reject_data, 'recommend_2_roller_gap', None) != recommend_2_roller_gap \
                        or getDictStrValue(reject_data, 'recommend_3_roller_gap', None) != recommend_3_roller_gap \
                        or getDictStrValue(reject_data, 'recommend_forming_roller_gap', None) != recommend_forming_roller_gap \
                        or getDictStrValue(reject_data, 'recommend_extruder_temperature_up', None) != recommend_extruder_temperature_up \
                        or getDictStrValue(reject_data, 'recommend_cross_cutter_speed', None) != recommend_cross_cutter_speed:
                    # 保存业务所需的推荐数据
                    recommend_weight_data_id = insert_recommend_weight_data((sku, formula, extruder_temperature,
                                                                             extruder_exit_gum_temp,
                                                                             slice_product_line_speed, n1_roller_gap,
                                                                             n2_roller_gap, n3_roller_gap,
                                                                             forming_roller_gap, extruder_temperature_up,
                                                                             cross_cutter_speed, target_weight,
                                                                             obj['fileLastTs'], weightTs, shift,
                                                                             actual_weight, recommend_1_roller_gap,
                                                                             recommend_2_roller_gap,  recommend_3_roller_gap,
                                                                             recommend_forming_roller_gap, recommend_extruder_temperature_up,
                                                                             recommend_cross_cutter_speed, predicted_weight,
                                                                             0, None, None, SYSTEM_OPERATOR_NAME, SYSTEM_OPERATOR_NAME,
                                                                             operator_time, operator_time))
            # ai返回的数据记录到日志中
            insert_recommend_weight_data_log((
                is_change, sku, formula, extruder_temperature, extruder_exit_gum_temp,
                slice_product_line_speed, n1_roller_gap, n2_roller_gap,
                n3_roller_gap, forming_roller_gap, extruder_temperature_up,
                cross_cutter_speed, target_weight, obj['fileLastTs'], weightTs, shift,
                actual_weight, ai_actual_weight, recommend_1_roller_gap,
                recommend_2_roller_gap, recommend_3_roller_gap,
                recommend_forming_roller_gap, recommend_extruder_temperature_up,
                recommend_cross_cutter_speed, predicted_weight,
                predicted_weight2, recommend_weight_data_id,
                SYSTEM_OPERATOR_NAME, SYSTEM_OPERATOR_NAME,
                operator_time, operator_time
            ))

        # 增加异常告警逻辑判断  Length
        unusual_service_condition_3(aml_data.get('Length', None))
    except Exception as e:
        insert_alert_log_data_pre(content=f'recommended_value_job 执行方法出现异常报错:{str(e)}', operator_user=SYSTEM_OPERATOR_NAME)
        logger.error("recommended_value_job failed detail:{}".format(traceback.format_exc()))


# 查询最新的实时数据组装表头数据
def get_common_header_last_data(attr=[TAG_RUNNING_STATUS, TAG_SKU, TAG_FORMULA, TAG_EXTRUDER_TEMPERATURE,
                                      TAG_EXTRUDER_EXIT_GUM_TEMP, TAG_SLICE_PRODUCT_LINE_SPEED,
                                      TAG_BIG_ROLLER_GAP, TAG_N1_ROLLER_GAP, TAG_N2_ROLLER_GAP,
                                      TAG_N3_ROLLER_GAP, TAG_FORMING_ROLLER_GAP, TAG_EXTRUDER_TEMPERATURE_UP,
                                      TAG_CROSS_CUTTER_SPEED]):

    tag_datas = get_multi_ts_last_value(attr)
    if not tag_datas:
        logger.error("get real data error, no data")
        return None
    last_dict = {item['map_tb_field_name']: item['value'] for item in tag_datas}
    last_dict['target_weight'] = TARGET_WEIGHT
    for item in attr:
        if item not in last_dict:
            last_dict[item] = None
    return last_dict


# 调用aml的逻辑
# 入参：
# {
#     "time": [2024, 6, 12, 0, 0,16] # 格式：[year, month, day, hour, minute, second],
# 	 "filePath": "2024/06/28/16/55/15/",
#    "fileLastTs": "2024-06-28 16:55:31"
# }
# 出参:
#   {
#         'code': 200, # 这期都是200，异常处理下一期做
#         'human_takeover': False,
#         'is_change': True,  # 是否需要调整
#         'Gap1': 0.10030000000000001,  # 1号辊推荐间隙
#         'Gap2': 0.067,  # 2号辊推荐间隙
#         'Gap3': 0.06,  # 3号辊推荐间
#         'GapFS': 0.06,  # 定型辊推荐间隙，FS = final sizing# 按照现有参数重量预测
#         'CrossScore': 1.236, # 横刀速度
#         'TempLowerSetValue': 1.336,  # 夹套水下部温度
#         'TempUpperSetValue': 1.336,  # 夹套水上部温度 (推荐挤压机温度取这个字段)
#         'ActualWeight': 35.49,
#         'WeightPredictionBeforeChange': 35.23,  # 按照现有参数重量预测 页面用这个值
#         'WeightPredictionAfterChange': 35.23,  # 安装推荐的参数重量预测
#         'msg': '',
#         'time':[2024,9,10,14,59,30],
#         'filePath':"2024/09/10/14/59/30/,
#         'fileLastTs':'2024-06-28 16:55:31',
#         'Length_Date':'2024-06-28 16:55:31',
#         'Length':71.03,
#         'Length_std':71.03,
#         'width':38.45,
#         'width_std':38.5,
#         'Thickness_Date':'2024-06-28 16:55:31',
#         'Thickness':1.66,
#         'Thickness_std':1.66,
#         'Depth':1.66,
#         'Depth_std':1.66,
#         'Weight_Date': '2024-06-28 16:55:31',
#         'shift': '中班'
#     }
def call_aml_data(fileLastTs_time, filePath, fileLastTs):
    try:
        payload = {"time": [fileLastTs_time.year,
                            fileLastTs_time.month,
                            fileLastTs_time.day,
                            fileLastTs_time.hour,
                            fileLastTs_time.minute,
                            fileLastTs_time.second], "filePath": filePath, "fileLastTs": fileLastTs}
        logger.info("call aml api reqParam:{}".format(payload))
        response = requests.post(Config.CALL_AML_URL, json=payload, headers={"Content-Type": "application/json"}, timeout=(15, 15))
        if response.status_code != 200:
            logger.error("call aml api error, resp code:{}".format(response.status_code))
            insert_alert_log_data_pre(content=f'调用AML模型,HTTP状态码错误:{response.status_code}', operator_user=SYSTEM_OPERATOR_NAME)
            return None
        # 解析数据
        res_data = response.json()
        logger.info("call aml api response:{}".format(res_data))
        return res_data
    except Exception as e:
        insert_alert_log_data_pre(content=f'call_aml_data 执行方法出现异常报错:{str(e)}', operator_user=SYSTEM_OPERATOR_NAME)
        logger.error("call_aml_data failed detail:{}".format(traceback.format_exc()))
    return None


# 更新推荐参数并回写接受
def update_recommend_weight_data_pre(write_req_param, data_obj, update_data_events):
    # 更新状态
    update_recommend_weight_data({
        "id": data_obj['id'],
        "recommend_1_roller_gap": data_obj['recommend_1_roller_gap'],
        "recommend_2_roller_gap": data_obj['recommend_2_roller_gap'],
        "recommend_3_roller_gap": data_obj['recommend_3_roller_gap'],
        "recommend_forming_roller_gap": data_obj['recommend_forming_roller_gap'],
        "recommend_extruder_temperature_up": data_obj['recommend_extruder_temperature_up'],
        "recommend_cross_cutter_speed": data_obj['recommend_cross_cutter_speed'],
        "operator_status": data_obj['operator_status'],
        "operator_user": data_obj['operator_user']
    })

    # 保存 事件数据
    for item in update_data_events:
        insert_event_data_pre(type=1,
                              type_name="推荐值修改",
                              content=item,
                              content_ext=f"recommend_weight_data_id:{data_obj['id']}",
                              operator_user=data_obj['operator_user'],
                              sku=data_obj['sku'],
                              shift=data_obj['shift'],
                              actual_weight=data_obj['actual_weight'])

    # 该行所有推荐数据的回写状态
    all_write_back_status = None
    # 正常点位回写集合
    req_normal = []
    # 挤压机温度特殊单独回写集合
    req_extruder_temperature = []
    if write_req_param:
        for key, value in write_req_param.items():
            if key in [WriteBackTagKey.WRITE_TAG_EXT_LB_TEMP_SP_TO_PLC, WriteBackTagKey.WRITE_TAG_EXT_UB_TEMP_SP_TO_PLC]:
                req_extruder_temperature.append({"Tag": key, "Value": float(value)})
            else:
                req_normal.append({"Tag": key, "Value": float(value)})
        # 回写正常点位
        status1 = write_back_normal_point(req_normal, write_req_param, data_obj)
        # 回写挤压机温度点位
        status2 = write_back_extruder_temperature_point(req_extruder_temperature, write_req_param, data_obj)
        # 赋值回写状态
        all_write_back_status = 1 if status1 == 1 and status2 == 1 else 0

    # 更新回写状态
    update_recommend_weight_data({"id": data_obj['id'], "write_back_status": all_write_back_status, "operator_user": data_obj['operator_user']})


# 调用回写接口
def call_write_back_httpApi(requestParam):
    try:
        # 查询自动回写开关状态
        switch_status = os.getenv("MY_WRITE_BACK_SWITCH")
        # 判断是否打开了回写
        if '1' != switch_status:
            logger.error("config write back close")
            return 0, None
        # 发送请求
        payload = {"methodName": "opcTagWrite", "responseTimeoutInSeconds": 5, "payload": requestParam}
        logger.info("call_write_back_httpApi url:{},data:{}".format(Config.WRITE_BACK_URL, payload))
        response = requests.post(Config.WRITE_BACK_URL,
                                 headers={'APIKey': Config.WRITE_BACK_AUTH_KEY, 'Content-Type': 'application/json'},
                                 json=payload, verify=False)
        if response.status_code != 200:
            logger.error('write back http statusCode error:{}'.format(response.status_code))
            return 0, None
        # 解析数据
        responseJon = str(response.text)
        logger.info("call_write_back_httpApi Response: {}".format(responseJon))
        for item in responseJon.split(","):
            if "OK" not in item:
                return 0, responseJon
        return 1, responseJon
    except Exception as e:
        insert_alert_log_data_pre(content=f'call_write_back_httpApi 执行方法出现异常报错:{str(e)}', operator_user=SYSTEM_OPERATOR_NAME)
        logger.error("call_write_back_httpApi failed detail:{}".format(traceback.format_exc()))
    return 0, None


# 检验生产还是停机状态
# if CG_Sheeting.CG_Sheeting.Variables.rGumExtruderExitGumTemp >= 40 and CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rGumEntranceTemperature >= 32 and CG_Sheeting.CG_Sheeting.dbHMI.Scoring.SRV_CrossScore.rActualVelocityRPM > 100:
#     return '1' # 在生产
# else:
#     return '2' # 在停机
def check_product_status():
    last_dict = {}
    try:
        tag_datas = get_multi_ts_last_value([TAG_EXTRUDER_EXIT_GUM_TEMP, TAG_GUM_ENTRANCE_TEMPERATURE, TAG_CROSS_CUTTER_SPEED])
        last_dict = {item['map_tb_field_name']: item['value'] for item in tag_datas}
        d1 = last_dict.get(TAG_EXTRUDER_EXIT_GUM_TEMP)
        d2 = last_dict.get(TAG_GUM_ENTRANCE_TEMPERATURE)
        d3 = last_dict.get(TAG_CROSS_CUTTER_SPEED)
        if d1 and d2 and d3 and float(d1) >= 40 and float(d2) >= 32 and float(d3) > 100:
            return '1'
    except Exception as e:
        logger.error("check_product_status failed detail:{}".format(str(e)))
        logger.error("check_product_status failed detail:{}".format(traceback.format_exc()))

    logger.debug("check_product_status:{},{},{}".format(last_dict.get(TAG_EXTRUDER_EXIT_GUM_TEMP),
                                                        last_dict.get(TAG_GUM_ENTRANCE_TEMPERATURE),
                                                        last_dict.get(TAG_CROSS_CUTTER_SPEED)))
    return '2'


# 回写普通点位数据
def write_back_normal_point(req_normal, write_req_param, data_obj):
    status, respJson = call_write_back_httpApi(req_normal)
    logger.info(f"normal point write back:{status},{respJson}")
    # 记录保存到事件表
    saveWriteBackEventLog(req_normal, respJson, write_req_param, data_obj)
    return status


# 回写特殊点位数据  WRITE_TAG_WRITE_TO_PLC_ENABLE 0是关闭状态, 回写前要变成1 回写完成后再变回0
def write_back_extruder_temperature_point(req_extruder_temperature, write_req_param, data_obj):
    # 第一步回写打开开关
    step1_status, resp1 = call_write_back_httpApi([{"Tag": WriteBackTagKey.WRITE_TAG_WRITE_TO_PLC_ENABLE, "Value": True}])
    # step1_status记录回写开关打开记录
    saveTemperatureWriteEnableEventLog(WriteBackTagKey.WRITE_TAG_WRITE_TO_PLC_ENABLE, True, step1_status, data_obj)
    step2_status = None
    resp2 = None
    step3_status = None
    resp3 = None
    # 回写成功在执行下一步  前两个都回写成功才算成功  事件记录里需要记录回写时间
    if step1_status == 1:
        # 第二步回写温度点位
        step2_status, resp2 = call_write_back_httpApi(req_extruder_temperature)
        # 记录保存到事件表
        saveWriteBackEventLog(req_extruder_temperature, resp2, write_req_param, data_obj)
        # 第三步关闭开关
        step3_status, resp3 = call_write_back_httpApi([{"Tag": WriteBackTagKey.WRITE_TAG_WRITE_TO_PLC_ENABLE, "Value": False}])
        # step2_status记录保存到事件表
        saveTemperatureWriteEnableEventLog(WriteBackTagKey.WRITE_TAG_WRITE_TO_PLC_ENABLE, False, step3_status, data_obj)

    logger.info(f"extruder_temperature point write back: step1:{step1_status}|{resp1},step2:{step2_status}|{resp2},step3:{step3_status}|{resp3}")

    return step2_status


# 解析回写接口返回的数据并记录到事件表
def saveWriteBackEventLog(req_param, respJson, dict_tag_value, data_obj):
    try:
        event_list = []
        if respJson:
            respJson = respJson.replace("{", "").replace("}", "")
            for obj in respJson.split(","):
                tag_value = obj.split(":")
                tag = str(tag_value[0]).strip()
                value = str(tag_value[1]).strip()
                # 保存 事件数据
                event_list.append(f"{WriteBackTagKey.TAG_MAP_ZN_NAME.get(tag)}的推荐值{dict_tag_value.get(tag)}回写{'成功' if value == 'OK' else '失败'}")
        else:
            for obj in req_param:
                event_list.append(f"{WriteBackTagKey.TAG_MAP_ZN_NAME.get(obj['Tag'])}的推荐值{dict_tag_value.get(obj['Tag'])}回写失败")

        # 保存 事件数据
        for item in event_list:
            insert_event_data_pre(type=5,
                                  type_name="推荐值回写记录",
                                  content=item,
                                  content_ext=f"recommend_weight_data_id:{data_obj['id']}",
                                  operator_user=data_obj['operator_user'],
                                  sku=data_obj['sku'],
                                  shift=data_obj['shift'],
                                  actual_weight=data_obj['actual_weight'])

    except Exception as e:
        logger.error("saveWriteBackEventLog failed detail:{}".format(str(e)))
        logger.error("saveWriteBackEventLog failed detail:{}".format(traceback.format_exc()))


# 挤压机温度回写开关的事件记录
def saveTemperatureWriteEnableEventLog(tag, value, status, data_obj):
    insert_event_data_pre(type=5,
                          type_name="推荐值回写记录",
                          content=f"{WriteBackTagKey.TAG_MAP_ZN_NAME.get(tag)}{'打开' if value else '关闭'}{'成功' if status == 1 else '失败'}",
                          content_ext=f"recommend_weight_data_id:{data_obj['id']}",
                          operator_user=data_obj['operator_user'],
                          sku=data_obj['sku'],
                          shift=data_obj['shift'],
                          actual_weight=data_obj['actual_weight'])


# 校验值是否满足上下限范围内 超出范围返回True,未超出false value校验过了不可能为空
def check_value_out_range(value, lower_limit, upper_limit):
    return value < lower_limit or value > upper_limit
