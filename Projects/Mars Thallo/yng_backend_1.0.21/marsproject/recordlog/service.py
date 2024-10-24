import traceback

import pytz

from marsproject.utils.log_util import get_log
from marsproject.utils.constant_value import SYSTEM_OPERATOR_NAME, TAG_DRUM2_INLET_TEMP, TAG_DRUM1_INLET_TEMP, \
    TAG_CHILLER_SET_POINT, TAG_RUNNING_STATUS, CheckWriteBackBefore
from marsproject.operation.models import get_single_recommend_weight_last_data, get_multi_ts_last_value, \
    get_spc_weight_limit_data
from marsproject.recordlog.models import insert_event_data, insert_alert_log_data
from marsproject.utils.time_utils import get_cst_time

logger = get_log(__name__)


# 异常工况:冷辊入口温度异常-1min一次
# 识别方法:  监控冷辊的设定温度 & 实际入口温度 UI = “冷辊实际温度偏差过大，请及时检查冷冻机”.若取不到近5s的数据 UI = “数据异常: 最近5秒的冷辊数据为空”
# 异常判定信号源：
# 1---CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum1InletTemp [S1]  drum1_inlet_temp
# 2---CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum2InletTemp [S2]  drum2_inlet_temp
# 3---CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rChillerSetpoint [S3] chiller_setpoint
# 判断逻辑: abs(S1-S3) > 1 or abs(S2-S3) > 1，触发报警 ,出口 有糖22-24； 无糖24.5-26.5
def unusual_service_condition_1():
    try:
        cur_time = get_cst_time()
        tag_datas = get_multi_ts_last_value([TAG_DRUM1_INLET_TEMP, TAG_DRUM2_INLET_TEMP, TAG_CHILLER_SET_POINT])
        last_dict = {item['map_tb_field_name']: item for item in tag_datas}
        if not last_dict.get(TAG_DRUM1_INLET_TEMP) or not last_dict.get(TAG_DRUM2_INLET_TEMP) or not last_dict.get(TAG_CHILLER_SET_POINT):
            return False
        s1_v = last_dict[TAG_DRUM1_INLET_TEMP]['value']
        s2_v = last_dict[TAG_DRUM2_INLET_TEMP]['value']
        s3_v = last_dict[TAG_CHILLER_SET_POINT]['value']
        if not s1_v or not s2_v or not s3_v \
                or (cur_time - pytz.timezone('Asia/Shanghai').localize(last_dict[TAG_DRUM1_INLET_TEMP]['tag_time'])).total_seconds() > 5 \
                or (cur_time - pytz.timezone('Asia/Shanghai').localize(last_dict[TAG_DRUM2_INLET_TEMP]['tag_time'])).total_seconds() > 5 \
                or (cur_time - pytz.timezone('Asia/Shanghai').localize(last_dict[TAG_CHILLER_SET_POINT]['tag_time'])).total_seconds() > 5:
            insert_alert_log_data_pre(content='数据异常: 最近5秒的冷辊数据为空', operator_user=SYSTEM_OPERATOR_NAME)
            return True

        # 判断逻辑
        if abs(float(s1_v) - float(s3_v)) > 1 or abs(float(s2_v) - float(s3_v)) > 1:
            insert_alert_log_data_pre(content='冷辊实际温度偏差过大，请及时检查冷冻机', operator_user=SYSTEM_OPERATOR_NAME)
            return True
    except Exception as e:
        logger.error("unusual_service_condition_1 failed detail:{}".format(str(e)))
        logger.error("unusual_service_condition_1 failed detail:{}".format(traceback.format_exc()))
    return False


# 异常工况:口香糖尺寸异常-AI给数据
# 识别方法:  监控口香糖的长度，若实际测量尺寸超出建议的上下限阈值，给出预警 UI = “口香糖长度异常，请及时参考调参建议”
# 异常判定信号源：
# AI Model -> Latest SPC Length Data [S1]
# AI返回Error Code / SPC长度
# 判断逻辑: S1 > 72.2 or S1 < 71.2，触发报警
def unusual_service_condition_3(length):
    try:
        if not length or length > 72.2 or length < 71.2:
            insert_alert_log_data_pre(content='口香糖长度异常，请及时参考调参建议', operator_user=SYSTEM_OPERATOR_NAME)
            return True
    except Exception as e:
        logger.error("unusual_service_condition_3 failed detail:{}".format(str(e)))
        logger.error("unusual_service_condition_3 failed detail:{}".format(traceback.format_exc()))
    return False


# 异常工况:SPC称重数据异常-1min一次
# 识别方法:  监控上一次SPC称重时间，若半小时内没有记录且已开机30min以上，给出预警 UI = “生产中，请尽快进行SPC称重”
# 异常判定信号源：
# 条件1：生产时间 = (datetime.now() - 上一次产线状态从”false”到”true”的时间) > 30mins
# 条件2：上一次SPC称重时间 > datetime.now() – 30min
# 判断逻辑: 若生产时间 > 30min & 上一次SPC称重时间> datetime.now() – 30min，触发异常报警
def unusual_service_condition_4():
    try:
        cur_time = get_cst_time()
        tag_datas = get_multi_ts_last_value([TAG_RUNNING_STATUS])
        if tag_datas and tag_datas[0]['value'] == 'true':
            last_spc_data = get_spc_weight_limit_data(1, 3)
            d1 = (cur_time - pytz.timezone('Asia/Shanghai').localize(tag_datas[0]['tag_time'])).total_seconds()/60
            d2 = (cur_time - pytz.timezone('Asia/Shanghai').localize(last_spc_data[0]['data_time'])).total_seconds()/60
            if d1 > 30 and (not last_spc_data or d2 > 30):
                insert_alert_log_data_pre(content='生产中，请尽快进行SPC称重', operator_user=SYSTEM_OPERATOR_NAME)
                return True
    except Exception as e:
        logger.error("unusual_service_condition_4 failed detail:{}".format(str(e)))
        logger.error("unusual_service_condition_4 failed detail:{}".format(traceback.format_exc()))
    return False


# 判断回写的点位是否有故障
def unusual_service_condition_write_back():
    try:
        tag_datas = get_multi_ts_last_value([CheckWriteBackBefore.TAG_N1_ROLLER_UPDATE_CHECK,
                                             CheckWriteBackBefore.TAG_N2_ROLLER_UPDATE_CHECK,
                                             CheckWriteBackBefore.TAG_N3_ROLLER_UPDATE_CHECK,
                                             CheckWriteBackBefore.TAG_FORMING_ROLLER_UPDATE_CHECK])
        alerts = [CheckWriteBackBefore.TAG_EVENT_MSG.get(item['map_tb_field_name']) for item in tag_datas if item['value'] != 'false']
        if alerts:
            # 保存 事件数据
            batch_insert_alert_log_data_pre(contents=alerts, operator_user=SYSTEM_OPERATOR_NAME)
            return True
    except Exception as e:
        logger.error("unusual_service_condition_write_back failed detail:{}".format(str(e)))
        logger.error("unusual_service_condition_write_back failed detail:{}".format(traceback.format_exc()))
    return False


# 插入事件之前的预处理方法
def insert_event_data_pre(type, type_name, content, operator_user, content_ext=None, sku=None, shift=None, actual_weight=None):
    # sku, shift, actual_weight就判断一个sku就可以了
    if not sku:
        last_data = get_single_recommend_weight_last_data()
        if last_data:
            sku = last_data['sku']
            shift = last_data['shift']
            actual_weight = last_data['actual_weight']
    # 插入到事件表中
    insert_event_data({"type": type,
                       "type_name": type_name,
                       "content": content,
                       "operator_user": operator_user,
                       "content_ext": content_ext,
                       "sku": sku,
                       "shift": shift,
                       "actual_weight": actual_weight})


# 插入告警之前的预处理方法
def insert_alert_log_data_pre(content, operator_user, sku=None, shift=None, actual_weight=None):
    # sku, shift, actual_weight就判断一个sku就可以了
    if not sku:
        last_data = get_single_recommend_weight_last_data()
        if last_data:
            sku = last_data['sku']
            shift = last_data['shift']
            actual_weight = last_data['actual_weight']
    # 插入到告警表中
    insert_alert_log_data({
        "content": content,
        "operator_user": operator_user,
        "sku": sku,
        "shift": shift,
        "actual_weight": actual_weight
    })


# 批量写入插入告警之前的预处理方法
def batch_insert_alert_log_data_pre(contents, operator_user, sku=None, shift=None, actual_weight=None):
    # sku, shift, actual_weight就判断一个sku就可以了
    if not sku:
        last_data = get_single_recommend_weight_last_data()
        if last_data:
            sku = last_data['sku']
            shift = last_data['shift']
            actual_weight = last_data['actual_weight']
    # 插入到告警表中
    for item in contents:
        insert_alert_log_data({
            "content": item,
            "operator_user": operator_user,
            "sku": sku,
            "shift": shift,
            "actual_weight": actual_weight
        })

