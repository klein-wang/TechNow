import datetime
import json
from flask import request, g
from marsproject.operation import operation_bp
from marsproject.utils.http_resp_util import Status, Message
from .models import *
import traceback
from marsproject.utils.redis_util import RedisUtils
from marsproject.utils.string_utils import *
import time
from marsproject.utils.http_resp_util import http_resp
from marsproject.utils.constant_value import *
import json
from marsproject.utils.log_util import get_log
from .service import get_common_header_last_data, update_recommend_weight_data_pre, check_product_status, \
    check_value_out_range
from ..dim_sku.models import get_single_data_by_sku_name
from ..recordlog.service import insert_event_data_pre, insert_alert_log_data_pre, unusual_service_condition_write_back
from ..utils.iam.token import login_required
from ..utils.time_utils import get_cst_time

logger = get_log(__name__)


# 获取最新的表头数据
@operation_bp.route('/getLastHeaderCommonValue', methods=['GET'])
@login_required
def getLastHeaderCommonValue():
    res = {'code': Status.SUCCESS, 'msg': Message.SUCCESS, 'data': None}
    try:
        common_data = {}
        # 查询当前推荐数据最新的一条
        common_header_last_data = get_common_header_last_data()
        if common_header_last_data:
            common_data['running_status'] = common_header_last_data[TAG_RUNNING_STATUS]
            common_data['sku'] = common_header_last_data[TAG_SKU]
            common_data['formula'] = common_header_last_data[TAG_FORMULA]
            common_data['extruder_temperature'] = common_header_last_data[TAG_EXTRUDER_TEMPERATURE]
            if common_data['extruder_temperature'] and is_number_by_str(common_data['extruder_temperature']):
                common_data['extruder_temperature'] = effectiveDigitToFixed(common_data['extruder_temperature'], 4, None)
            common_data['extruder_exit_gum_temp'] = common_header_last_data[TAG_EXTRUDER_EXIT_GUM_TEMP]
            if common_data['extruder_exit_gum_temp'] and is_number_by_str(common_data['extruder_exit_gum_temp']):
                common_data['extruder_exit_gum_temp'] = effectiveDigitToFixed(common_data['extruder_exit_gum_temp'], 4, None)
            common_data['slice_product_line_speed'] = common_header_last_data[TAG_SLICE_PRODUCT_LINE_SPEED]
            if common_data['slice_product_line_speed'] and is_number_by_str(common_data['slice_product_line_speed']):
                common_data['slice_product_line_speed'] = effectiveDigitToFixed(common_data['slice_product_line_speed'], 4, None)
            common_data['target_weight'] = common_header_last_data['target_weight']
            common_data['big_roller_gap'] = substringToFixed(getDictStrValue(common_header_last_data, TAG_BIG_ROLLER_GAP), 4, None)
            common_data['n1_roller_gap'] = substringToFixed(getDictStrValue(common_header_last_data, TAG_N1_ROLLER_GAP), 4, None)
            common_data['n2_roller_gap'] = substringToFixed(getDictStrValue(common_header_last_data, TAG_N2_ROLLER_GAP), 4, None)
            common_data['n3_roller_gap'] = substringToFixed(getDictStrValue(common_header_last_data, TAG_N3_ROLLER_GAP), 4, None)
            common_data['forming_roller_gap'] = substringToFixed(getDictStrValue(common_header_last_data, TAG_FORMING_ROLLER_GAP), 4, None)
            common_data['extruder_temperature_up'] = substringToFixed(getDictStrValue(common_header_last_data, TAG_EXTRUDER_TEMPERATURE_UP), 4, None)
            common_data['cross_cutter_speed'] = substringToFixed(getDictStrValue(common_header_last_data, TAG_CROSS_CUTTER_SPEED), 2, None)

        res['data'] = common_data
    except Exception as e:
        insert_alert_log_data_pre(content=f'getLastHeaderCommonValue error:{str(e)}', operator_user=SYSTEM_OPERATOR_NAME)
        logger.error("getLastHeaderCommonValue failed detail: {}".format(traceback.format_exc()))
        res['code'] = Status.EXCEPTION_ERROR
        res['msg'] = str(e)
    return http_resp(res)


# 获取最新的推荐数据
@operation_bp.route('/getLastRecommendValue', methods=['GET'])
@login_required
def getLastRecommendValue():
    res = {'code': Status.SUCCESS, 'msg': Message.SUCCESS, 'data': None}
    try:
        recommend_data = {}
        # 查询表头最新的一条数据
        last_recommend_data = get_single_recommend_weight_last_data()
        if last_recommend_data:
            recommend_data['id'] = last_recommend_data['id']
            recommend_data['data_time'] = last_recommend_data['data_time'].strftime("%Y-%m-%d %H:%M:%S")
            recommend_data['shift'] = last_recommend_data['shift']
            recommend_data['actual_weight'] = last_recommend_data['actual_weight']
            recommend_data['recommend_1_roller_gap'] = last_recommend_data['recommend_1_roller_gap']
            recommend_data['recommend_2_roller_gap'] = last_recommend_data['recommend_2_roller_gap']
            recommend_data['recommend_3_roller_gap'] = last_recommend_data['recommend_3_roller_gap']
            recommend_data['recommend_forming_roller_gap'] = last_recommend_data['recommend_forming_roller_gap']
            recommend_data['recommend_extruder_temperature_up'] = last_recommend_data['recommend_extruder_temperature_up']
            recommend_data['recommend_cross_cutter_speed'] = last_recommend_data['recommend_cross_cutter_speed']
            recommend_data['predicted_weight'] = last_recommend_data['predicted_weight']
            if last_recommend_data['predicted_weight'] is not None and last_recommend_data['actual_weight'] is not None:
                recommend_data['diff_weight_value'] = decimalSubValue(last_recommend_data['predicted_weight'], last_recommend_data['actual_weight'], 2, None)
            else:
                recommend_data['diff_weight_value'] = None
            recommend_data['operator_status'] = last_recommend_data['operator_status']
            recommend_data['operator_reason'] = last_recommend_data['operator_reason']

            # 获取实时数据
            common_header_last_data = get_common_header_last_data([TAG_N1_ROLLER_GAP, TAG_N2_ROLLER_GAP,
                                                                   TAG_N3_ROLLER_GAP, TAG_FORMING_ROLLER_GAP,
                                                                   TAG_EXTRUDER_TEMPERATURE_UP_SV,
                                                                   TAG_CROSS_CUTTER_SPEED_SV])
            if not common_header_last_data:
                common_header_last_data = {}
            ts_n1_roller_gap = substringToFixed(getDictStrValue(common_header_last_data, TAG_N1_ROLLER_GAP), 4, None)
            ts_n2_roller_gap = substringToFixed(getDictStrValue(common_header_last_data, TAG_N2_ROLLER_GAP), 4, None)
            ts_n3_roller_gap = substringToFixed(getDictStrValue(common_header_last_data, TAG_N3_ROLLER_GAP), 4, None)
            ts_forming_roller_gap = substringToFixed(getDictStrValue(common_header_last_data, TAG_FORMING_ROLLER_GAP),4, None)
            ts_extruder_temperature_up_sv = substringToFixed(getDictStrValue(common_header_last_data, TAG_EXTRUDER_TEMPERATURE_UP_SV), 4, None)
            ts_cross_cutter_speed_sv = substringToFixed(getDictStrValue(common_header_last_data, TAG_CROSS_CUTTER_SPEED_SV),2, None)
            # 0 否 1 是
            recommend_data['is_adjust_n1_roller'] = 1 if recommend_data['recommend_1_roller_gap'] != ts_n1_roller_gap else 0
            recommend_data['is_adjust_n2_roller'] = 1 if recommend_data['recommend_2_roller_gap'] != ts_n2_roller_gap else 0
            recommend_data['is_adjust_n3_roller'] = 1 if recommend_data['recommend_3_roller_gap'] != ts_n3_roller_gap else 0
            recommend_data['is_adjust_forming_roller'] = 1 if recommend_data['recommend_forming_roller_gap'] != ts_forming_roller_gap else 0
            recommend_data['is_adjust_extruder_temperature_up'] = 1 if recommend_data['recommend_extruder_temperature_up'] != ts_extruder_temperature_up_sv else 0
            recommend_data['is_adjust_cross_cutter_speed'] = 1 if recommend_data['recommend_cross_cutter_speed'] != ts_cross_cutter_speed_sv else 0

        res['data'] = recommend_data
    except Exception as e:
        insert_alert_log_data_pre(content=f'getLastRecommendValue error:{str(e)}', operator_user=SYSTEM_OPERATOR_NAME)
        logger.error("getLastRecommendValue failed detail: {}".format(traceback.format_exc()))
        res['code'] = Status.EXCEPTION_ERROR
        res['msg'] = str(e)
    return http_resp(res)


# 获取spc相关的折线图
@operation_bp.route('/getSpcLineChart', methods=['GET'])
@login_required
def getSpcLineChart():
    res = {'code': Status.SUCCESS, 'msg': Message.SUCCESS, 'data': None}
    try:
        weight_data = []
        length_or_thickness_data = []
        width_or_depth = []
        # 查询spc最新的数据 entry_type 1 厚深 2 长宽  , 3是重量
        spc_data1 = get_spc_weight_limit_data(50, 2)
        for item in list(reversed(spc_data1)):
            length_or_thickness_data.append({"data_time": item['data_time'].strftime("%Y-%m-%d %H:%M:%S"),
                                             "length_value": item['length_or_thickness'],
                                             "width_value": item['width_or_depth']
                                             })
        spc_data2 = get_spc_weight_limit_data(50, 1)
        for item in list(reversed(spc_data2)):
            width_or_depth.append({"data_time": item['data_time'].strftime("%Y-%m-%d %H:%M:%S"),
                                   "thickness_value": item['length_or_thickness'],
                                   "depth_value": item['width_or_depth']
                                   })
        # 重量 SPC重量展示 显示最近4小时，去掉预测查询
        cur_time = get_cst_time()
        start_time = cur_time + datetime.timedelta(hours=-4)
        spc_data3 = get_spc_weight_data_by_time(3, start_time.strftime("%Y-%m-%d %H:%M:%S"), cur_time.strftime("%Y-%m-%d %H:%M:%S"))
        # data3_dict = {item['data_time'].strftime("%Y-%m-%d %H:%M:%S"): item for item in list(reversed(spc_data3))}
        # sug_weight_data3 = get_recommend_weight_limit_data(50)
        # sug_weight_dict = {item['data_time'].strftime("%Y-%m-%d %H:%M:%S"): item for item in list(reversed(sug_weight_data3))}
        # sort_time = sorted(set(list(data3_dict.keys()) + list(sug_weight_dict.keys())), key=lambda x: datetime.datetime.strptime(x, "%Y-%m-%d %H:%M:%S"))
        for item in spc_data3:
            weight_data.append({"data_time": item['data_time'].strftime("%Y-%m-%d %H:%M:%S"),
                                "actual_weight": getDictStrValue(item, 'actual', None)})

        res['data'] = {"weight_data": weight_data, "length_or_thickness_data": length_or_thickness_data, "width_or_depth": width_or_depth}
    except Exception as e:
        insert_alert_log_data_pre(content=f'getSpcLineChart error:{str(e)}', operator_user=SYSTEM_OPERATOR_NAME)
        logger.error("getSpcLineChart failed detail: {}".format(traceback.format_exc()))
        res['code'] = Status.EXCEPTION_ERROR
        res['msg'] = str(e)
    return http_resp(res)


# 获取最新开始和停止状态
#  生产/停机 -> 开始/结束 需要变化 ->
# -	从开始 要变为 结束：事件通知——“检测到当前为停机状态，结束模型推荐”
# -	从结束 要变为 开始：事件通知——“检测到当前为生产状态，开启模型推荐”
# 定义 1 人工开始 2 人工结束  3 系统开始 4 系统结束
@operation_bp.route('/getSystemStatus', methods=['GET'])
@login_required
def getSystemStatus():
    res = {'code': Status.SUCCESS, 'msg': Message.SUCCESS, 'data': None}
    lock_key = RedisKey.YNG_UPDATE_SYSTEM_STATUS_LOCK
    lock_value = str(uuid.uuid4())
    try:
        if not RedisUtils.set_lock(lock_key, lock_value):
            res['code'] = Status.DATA_ERROR
            res['msg'] = Message.OPERATOR_ERROR
            return http_resp(res)
        # 1 生产 2 停机
        check_sys_status = check_product_status()
        old_sys_status = RedisUtils.get_value(RedisKey.SYSTEM_STATUS_KEY)
        # 如果第一次为空则都初始化位人工开始或者人工结束的状态
        if not old_sys_status:
            RedisUtils.set_value_no_ex(RedisKey.SYSTEM_STATUS_KEY, check_sys_status)
            RedisUtils.set_value_no_ex(RedisKey.SYSTEM_STATUS_KEY_LOG, check_sys_status)
            res['data'] = {"system_status": check_sys_status}
            return http_resp(res)
        # systemStatusLog第一次初始化先和系统状态保持一致
        old_sys_status_log = RedisUtils.get_value(RedisKey.SYSTEM_STATUS_KEY_LOG)
        if not old_sys_status_log:
            RedisUtils.set_value_no_ex(RedisKey.SYSTEM_STATUS_KEY_LOG, str(old_sys_status, 'utf-8'))
        # 校验逻辑
        if check_sys_status != str(old_sys_status, 'utf-8'):
            # 当前实际状态是生产,但是系统状态是人工停机,则不处理,等系统检测到停机状态后,下个周期在开始生产
            if check_sys_status == '1' and str(old_sys_status_log, 'utf-8') == '2':
                res['data'] = {"system_status": str(old_sys_status, 'utf-8')}
                return http_resp(res)
            # 走其他正常逻辑
            insert_event_data_pre(type=4,
                                  type_name="运行状态",
                                  content="检测到当前为生产状态,开启模型推荐" if check_sys_status == "1" else "检测到当前为停机状态,结束模型推荐",
                                  operator_user=SYSTEM_OPERATOR_NAME)
        # 保存到缓存中
        RedisUtils.set_value_no_ex(RedisKey.SYSTEM_STATUS_KEY, check_sys_status)
        # 1 人工开始 2 人工结束  3 系统开始 4 系统结束
        RedisUtils.set_value_no_ex(RedisKey.SYSTEM_STATUS_KEY_LOG, str(int(check_sys_status) + 2))
        res['data'] = {"system_status": check_sys_status}
    except Exception as e:
        insert_alert_log_data_pre(content=f'getSystemStatus error:{str(e)}', operator_user=SYSTEM_OPERATOR_NAME)
        logger.error("getSystemStatus failed detail: {}".format(traceback.format_exc()))
        res['code'] = Status.EXCEPTION_ERROR
        res['msg'] = str(e)
    finally:
        RedisUtils.release_lock(lock_key, lock_value)

    return http_resp(res)


# 修改运行状态
# 人机交互 -	T0时刻 生产中 -> 开始(后端) -> T1时刻 结束(人工)
# •	弹窗提醒“当前处于生产状态，请确认是否要关闭模型推荐”-> 确认则关闭 -> 等到下次生产中（T3时刻）再自动开启
# •	*T0生产中 -> T1时刻 结束(人工) -> T2停产中 ->下个批次 T3生产中
# -	T0时刻 停产中 -> 结束(后端) -> 开始(人工) -> 禁止修改 + 文案提醒“当前处于停机状态，无法进行模型推荐
# 定义 1 人工开始 2 人工结束  3 系统开始 4 系统结束
@operation_bp.route('/updateSystemStatus', methods=['POST'])
@login_required
def updateSystemStatus():
    logger.debug("updateSystemStatus param={}".format(request.json))
    res = {'code': Status.SUCCESS, 'msg': Message.SUCCESS, 'data': None}
    lock_key = RedisKey.YNG_UPDATE_SYSTEM_STATUS_LOCK
    lock_value = str(uuid.uuid4())
    try:
        if not RedisUtils.set_lock(lock_key, lock_value):
            res['code'] = Status.DATA_ERROR
            res['msg'] = Message.OPERATOR_ERROR
            return http_resp(res)

        systemStatus = request.json['system_status']
        if systemStatus not in ['1', '2']:
            res['code'] = Status.PARAMS_ERROR
            res['msg'] = Message.VALUE_ERROR
            return http_resp(res)

        if systemStatus == str(RedisUtils.get_value(RedisKey.SYSTEM_STATUS_KEY), 'utf-8'):
            res['code'] = Status.DATA_ERROR
            res['msg'] = Message.NO_REPEAT_OPERATOR
            return http_resp(res)

        # 检测当前生产状态  1 生产  2 停机
        if systemStatus == '1' and check_product_status() == '2':
            res['code'] = Status.DATA_ERROR
            res['msg'] = Message.SYS_NO_START_TEXT1
            return http_resp(res)

        # 保存倒缓存中
        RedisUtils.set_value_no_ex(RedisKey.SYSTEM_STATUS_KEY, systemStatus)
        # 保存最新一条log缓存中 定义 1 人工开始 2 人工结束  3 系统开始 4 系统结束
        RedisUtils.set_value_no_ex(RedisKey.SYSTEM_STATUS_KEY_LOG, systemStatus)
        # 4 常规事件
        insert_event_data_pre(type=4, type_name="运行状态", content="运行状态设置为开始" if systemStatus == '1' else "运行状态设置为停止", operator_user=g.user)
    except Exception as e:
        insert_alert_log_data_pre(content=f'updateSystemStatus error:{str(e)}', operator_user=SYSTEM_OPERATOR_NAME)
        logger.error("updateSystemStatus failed detail: {}".format(traceback.format_exc()))
        res['code'] = Status.EXCEPTION_ERROR
        res['msg'] = str(e)
    finally:
        RedisUtils.release_lock(lock_key, lock_value)

    return http_resp(res)


# 获取字段数据根据所传值
@operation_bp.route('/getDictData', methods=['POST'])
@login_required
def getDictItemData():
    logger.debug("getDictData param={}".format(request.json))
    res = {'data': None, 'code': Status.SUCCESS, 'msg': Message.SUCCESS}
    try:
        res['data'] = get_dict_item_data(request.json['code'])
    except Exception as e:
        insert_alert_log_data_pre(content=f'getDictItemData error:{str(e)}', operator_user=SYSTEM_OPERATOR_NAME)
        logger.error("getDictItemData failed detail: {}".format(traceback.format_exc()))
        res['code'] = Status.EXCEPTION_ERROR
        res['msg'] = str(e)

    logger.debug("getDictItemData response: {}".format(res))
    return http_resp(res)


# 更新接受或者拒绝逻辑 0 未操作 1 接受 2 部分接受 3 拒绝
@operation_bp.route('/updateStatus', methods=['POST'])
@login_required
def updateStatus():
    logger.debug("updateStatus param={}".format(request.json))
    res = {'code': Status.SUCCESS, 'msg': Message.SUCCESS, 'data': None}
    lock_key = RedisKey.YNG_UPDATE_STATUS_LOCK
    lock_value = str(uuid.uuid4())
    # 获取参数
    reqParam = request.json
    try:
        if not RedisUtils.set_lock(lock_key, lock_value):
            res['code'] = Status.DATA_ERROR
            res['msg'] = Message.OPERATOR_ERROR
            return http_resp(res)

        if reqParam.get('operator_status') not in [1, 2, 3]:
            res['code'] = Status.DATA_ERROR
            res['msg'] = Message.VALUE_ERROR
            return http_resp(res)

        # 获取更新的推荐值以及id
        id = reqParam['id']
        sku = reqParam.get('sku')
        shift = reqParam.get('shift')
        actual_weight = reqParam.get('actual_weight')
        data_time = reqParam.get('data_time')
        predicted_weight = reqParam.get('predicted_weight')
        operator_status = reqParam.get('operator_status')
        operator_reason = getDictStrValue(reqParam, 'operator_reason', None)
        recommend_1_roller_gap = substringToFixed(getDictStrValue(reqParam, 'recommend_1_roller_gap'), 4, None)
        recommend_2_roller_gap = substringToFixed(getDictStrValue(reqParam, 'recommend_2_roller_gap'), 4, None)
        recommend_3_roller_gap = substringToFixed(getDictStrValue(reqParam, 'recommend_3_roller_gap'), 4, None)
        recommend_forming_roller_gap = substringToFixed(getDictStrValue(reqParam, 'recommend_forming_roller_gap'), 4, None)
        recommend_extruder_temperature_up = substringToFixed(getDictStrValue(reqParam, 'recommend_extruder_temperature_up'), 4, None)
        recommend_cross_cutter_speed = substringToFixed(getDictStrValue(reqParam, 'recommend_cross_cutter_speed'), 2, None)

        # 只有在部分接受和接受的时候才会判断该逻辑
        if operator_status in [1, 2]:
            if not all([recommend_1_roller_gap, recommend_2_roller_gap, recommend_3_roller_gap,
                        recommend_forming_roller_gap, recommend_extruder_temperature_up, recommend_cross_cutter_speed]):
                res['code'] = Status.DATA_ERROR
                res['msg'] = Message.VALUE_NOT_NULL
                return http_resp(res)

            # 判断sku是否为空
            if not sku:
                res['code'] = Status.DATA_ERROR
                res['msg'] = Message.SKU_NAME_IS_NULL
                return http_resp(res)
            # 判断模型配置是否配置了sku
            sku_info = get_single_data_by_sku_name(sku)
            if not sku_info:
                res['code'] = Status.DATA_ERROR
                res['msg'] = Message.SKU_NAME_IS_NOT_CONFIG
                return http_resp(res)
            # 判断上下限是否配置全
            if not all([sku_info['n1_roller_bottom_limit'], sku_info['n1_roller_top_limit'],
                       sku_info['n2_roller_bottom_limit'], sku_info['n2_roller_top_limit'],
                       sku_info['n3_roller_bottom_limit'], sku_info['n3_roller_top_limit'],
                       sku_info['forming_roller_bottom_limit'], sku_info['forming_roller_top_limit'],
                       sku_info['cross_cutter_speed_bottom_limit'], sku_info['cross_cutter_speed_top_limit'],
                       sku_info['extruder_temperature_bottom_limit'], sku_info['extruder_temperature_top_limit']]):
                res['code'] = Status.DATA_ERROR
                res['msg'] = Message.SKU_PARAM_CONFIG_FULL
                return http_resp(res)

            # 校验值是否符合上下限
            if check_value_out_range(float(recommend_1_roller_gap),
                                     float(sku_info['n1_roller_bottom_limit']),
                                     float(sku_info['n1_roller_top_limit'])) \
                    or check_value_out_range(float(recommend_2_roller_gap),
                                             float(sku_info['n2_roller_bottom_limit']),
                                             float(sku_info['n2_roller_top_limit'])) \
                    or check_value_out_range(float(recommend_3_roller_gap),
                                             float(sku_info['n3_roller_bottom_limit']),
                                             float(sku_info['n3_roller_top_limit'])) \
                    or check_value_out_range(float(recommend_forming_roller_gap),
                                             float(sku_info['forming_roller_bottom_limit']),
                                             float(sku_info['forming_roller_top_limit'])) \
                    or check_value_out_range(float(recommend_cross_cutter_speed),
                                             float(sku_info['cross_cutter_speed_bottom_limit']),
                                             float(sku_info['cross_cutter_speed_top_limit'])) \
                    or check_value_out_range(float(recommend_extruder_temperature_up),
                                             float(sku_info['extruder_temperature_bottom_limit']),
                                             float(sku_info['extruder_temperature_top_limit'])):
                res['code'] = Status.DATA_ERROR
                res['msg'] = Message.VALUE_LIMIT_ERROR
                return http_resp(res)

            # 判断下回写点位有故障么
            check_bol = unusual_service_condition_write_back()
            if check_bol:
                res['code'] = Status.DATA_ERROR
                res['msg'] = Message.WRITE_BACK_TAG_FAULT
                return http_resp(res)

        # 获取数据库里面的值判断是否改变
        old_data = get_single_recommend_weight_data_by_id(id)
        # 如果库中状态为接受,部分接受,拒绝,则证明已经操作过了
        if old_data['operator_status'] in [1, 2, 3]:
            res['code'] = Status.DATA_ERROR
            res['msg'] = Message.NO_REPEAT_OPERATOR
            return http_resp(res)

        # 构造回写参数,只有接受和部分接受才需要
        write_req_param = {}
        if operator_status in [1, 2]:
            # 把符合回写的参数构造出来
            common_header_last_data = get_common_header_last_data([TAG_N1_ROLLER_GAP, TAG_N2_ROLLER_GAP,
                                                                   TAG_N3_ROLLER_GAP, TAG_FORMING_ROLLER_GAP,
                                                                   TAG_EXTRUDER_TEMPERATURE_UP_SV,
                                                                   TAG_CROSS_CUTTER_SPEED_SV])
            if not common_header_last_data:
                common_header_last_data = {}
            ts_n1_roller_gap = substringToFixed(getDictStrValue(common_header_last_data, TAG_N1_ROLLER_GAP), 4, None)
            ts_n2_roller_gap = substringToFixed(getDictStrValue(common_header_last_data, TAG_N2_ROLLER_GAP), 4, None)
            ts_n3_roller_gap = substringToFixed(getDictStrValue(common_header_last_data, TAG_N3_ROLLER_GAP), 4, None)
            ts_forming_roller_gap = substringToFixed(getDictStrValue(common_header_last_data, TAG_FORMING_ROLLER_GAP), 4, None)
            ts_extruder_temperature_up_sv = substringToFixed(getDictStrValue(common_header_last_data, TAG_EXTRUDER_TEMPERATURE_UP_SV), 4, None)
            ts_cross_cutter_speed_sv = substringToFixed(getDictStrValue(common_header_last_data, TAG_CROSS_CUTTER_SPEED_SV), 2, None)
            if recommend_1_roller_gap != ts_n1_roller_gap:
                write_req_param[WriteBackTagKey.WRITE_TAG_1_ROLLER] = recommend_1_roller_gap
            if recommend_2_roller_gap != ts_n2_roller_gap:
                write_req_param[WriteBackTagKey.WRITE_TAG_2_ROLLER] = recommend_2_roller_gap
            if recommend_3_roller_gap != ts_n3_roller_gap:
                write_req_param[WriteBackTagKey.WRITE_TAG_3_ROLLER] = recommend_3_roller_gap
            if recommend_forming_roller_gap != ts_forming_roller_gap:
                write_req_param[WriteBackTagKey.WRITE_TAG_FORMING_ROLLER] = recommend_forming_roller_gap
            if recommend_cross_cutter_speed != ts_cross_cutter_speed_sv:
                write_req_param[WriteBackTagKey.WRITE_TAG_CROSS_CUTTER_SPEED] = recommend_cross_cutter_speed
            if recommend_extruder_temperature_up != ts_extruder_temperature_up_sv:
                write_req_param[WriteBackTagKey.WRITE_TAG_EXT_LB_TEMP_SP_TO_PLC] = recommend_extruder_temperature_up
                write_req_param[WriteBackTagKey.WRITE_TAG_EXT_UB_TEMP_SP_TO_PLC] = recommend_extruder_temperature_up

        # 把更新参数构造出来
        update_param = {
                    "id": id,
                    "sku": sku,
                    "shift": shift,
                    "actual_weight": actual_weight,
                    "recommend_1_roller_gap": recommend_1_roller_gap,
                    "recommend_2_roller_gap": recommend_2_roller_gap,
                    "recommend_3_roller_gap": recommend_3_roller_gap,
                    "recommend_forming_roller_gap": recommend_forming_roller_gap,
                    "recommend_extruder_temperature_up": recommend_extruder_temperature_up,
                    "recommend_cross_cutter_speed": recommend_cross_cutter_speed,
                    "operator_status": operator_status,
                    "operator_user": g.user
            }

        # 如果是接受则回写并更新状态
        if operator_status == 1:
            # 回写并更新状态
            update_recommend_weight_data_pre(write_req_param, update_param, [])
        elif operator_status == 3:
            # 拒绝
            update_recommend_weight_data({"id": id, "operator_status": operator_status, "operator_reason": operator_reason, "operator_user": g.user})
        # 如果部分接受则更新推荐参数在回写数据以及记录修改值的变更
        elif operator_status == 2:
            old_recommend_1_roller_gap = getDictStrValue(old_data, 'recommend_1_roller_gap', None)
            old_recommend_2_roller_gap = getDictStrValue(old_data, 'recommend_2_roller_gap', None)
            old_recommend_3_roller_gap = getDictStrValue(old_data, 'recommend_3_roller_gap', None)
            old_recommend_forming_roller_gap = getDictStrValue(old_data, 'recommend_forming_roller_gap', None)
            old_recommend_extruder_temperature_up = getDictStrValue(old_data, 'recommend_extruder_temperature_up', None)
            old_recommend_cross_cutter_speed = getDictStrValue(old_data, 'recommend_cross_cutter_speed', None)
            # 有一个值变了都做更新, 没有则不更新
            event_list = []
            if old_recommend_1_roller_gap != recommend_1_roller_gap:
                event_list.append(f"User - 1号辊由{old_recommend_1_roller_gap}调整为{recommend_1_roller_gap}")
            if old_recommend_2_roller_gap != recommend_2_roller_gap:
                event_list.append(f"User - 2号辊由{old_recommend_2_roller_gap}调整为{recommend_2_roller_gap}")
            if old_recommend_3_roller_gap != recommend_3_roller_gap:
                event_list.append(f"User - 3号辊由{old_recommend_3_roller_gap}调整为{recommend_3_roller_gap}")
            if old_recommend_forming_roller_gap != recommend_forming_roller_gap:
                event_list.append(f"User - 定型辊由{old_recommend_forming_roller_gap}调整为{recommend_forming_roller_gap}")
            if old_recommend_extruder_temperature_up != recommend_extruder_temperature_up:
                event_list.append(f"User - 挤压机夹套温度由{old_recommend_extruder_temperature_up}调整为{recommend_extruder_temperature_up}")
            if old_recommend_cross_cutter_speed != recommend_cross_cutter_speed:
                event_list.append(f"User - 横刀速度由{old_recommend_cross_cutter_speed}调整为{recommend_cross_cutter_speed}")

            # 为空证明没有任何修改
            if not event_list:
                res['code'] = Status.DATA_ERROR
                res['msg'] = Message.VALUE_NO_CHANGE
                return http_resp(res)

            # 回写并更新状态
            update_recommend_weight_data_pre(write_req_param, update_param, event_list)

        # 将数据返回给前端
        res['data'] = {
            "id": id,
            "recommend_1_roller_gap": recommend_1_roller_gap,
            "recommend_2_roller_gap": recommend_2_roller_gap,
            "recommend_3_roller_gap": recommend_3_roller_gap,
            "recommend_forming_roller_gap": recommend_forming_roller_gap,
            "recommend_extruder_temperature_up": recommend_extruder_temperature_up,
            "recommend_cross_cutter_speed": recommend_cross_cutter_speed,
            "operator_status": operator_status,
            "operator_reason": operator_reason,
            "sku": sku,
            "shift": shift,
            "actual_weight": actual_weight,
            "data_time": data_time,
            "diff_weight_value": decimalSubValue(predicted_weight, actual_weight, 2, None),
            "predicted_weight": predicted_weight
        }
        return http_resp(res)

    except Exception as e:
        insert_alert_log_data_pre(content=f'updateStatus error:{str(e)}', operator_user=SYSTEM_OPERATOR_NAME)
        logger.error("updateStatus failed detail: {}".format(traceback.format_exc()))
        res['code'] = Status.EXCEPTION_ERROR
        res['msg'] = str(e)
    finally:
        RedisUtils.release_lock(lock_key, lock_value)
    return http_resp(res)


# 获取最新生产状态
@operation_bp.route('/getCurrentProductionStatus', methods=['GET'])
@login_required
def getCurrentProductionStatus():
    return http_resp({'code': Status.SUCCESS, 'msg': Message.SUCCESS, 'data': check_product_status()})



