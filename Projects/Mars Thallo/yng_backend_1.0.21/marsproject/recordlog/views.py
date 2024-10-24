import io

import pandas as pd
from flask import request, make_response, jsonify, g, send_file
from marsproject.recordlog import recordLog_bp
from marsproject.utils.http_resp_util import Status, Message
from .models import *
from marsproject.utils.string_utils import *
import traceback
from marsproject.utils.time_utils import get_cst_second, get_cst_time_by_second
from datetime import datetime
from marsproject.utils.http_resp_util import http_resp
from marsproject.utils.log_util import get_log
from ..utils.iam.token import login_required

logger = get_log(__name__)


# 事件查询接口
@recordLog_bp.route('/event', methods=['POST'])
@login_required
def get_event_list():
    res = {}
    try:
        # 单位小时
        interval = int(request.json.get('interval', '24'))
        limit = int(request.json.get('limit', 20))
        lastTime = get_cst_time_by_second(get_cst_second(datetime.now()) - interval * 60 * 60)
        # 查询告警数据
        result = get_event_data(lastTime, limit)
        res['code'] = Status.SUCCESS
        res['msg'] = Message.SUCCESS
        res['data'] = result
    except Exception as e:
        logger.error("get_event_list failed detail: {}".format(traceback.format_exc()))
        res['code'] = Status.EXCEPTION_ERROR
        res['msg'] = str(e)
        res['data'] = None

    logger.debug("get_event_list response: {}".format(res))

    return http_resp(res)


@recordLog_bp.route('/alert', methods=['POST'])
@login_required
def get_alert_list():
    res = {}
    try:
        # 单位小时
        interval = int(request.json.get('interval', '24'))
        lastTime = get_cst_time_by_second(get_cst_second(datetime.now()) - interval * 60 * 60)
        # 查询告警数据
        result = get_alert_data(lastTime)
        res['code'] = Status.SUCCESS
        res['msg'] = Message.SUCCESS
        res['data'] = result
    except Exception as e:
        logger.error("get_alert_list failed detail: {}".format(traceback.format_exc()))
        res['code'] = Status.EXCEPTION_ERROR
        res['msg'] = str(e)
        res['data'] = None

    logger.debug("get_alert_list response: {}".format(res))

    return http_resp(res)


# 历史记录分页查询接口
@recordLog_bp.route('/historyPageList', methods=['POST'])
@login_required
def get_history_page_list():
    res = {}
    try:
        pageNum = request.json.get('pageNum', 1)
        pageSize = request.json.get('pageSize', 10)
        sku = request.json.get('sku')
        shift = request.json.get('shift')
        start_time = request.json.get('start_time')
        end_time = request.json.get('end_time')
        # 查询历史数据
        operator_status_arr = ['未操作', '接受', '部分接受', '拒绝']
        total, result = get_history_page_list_data(pageNum, pageSize, sku, shift, start_time, end_time)
        for item in result:
            operator_status = item['operator_status']
            item['operator_status_str'] = operator_status_arr[0] if operator_status is None else operator_status_arr[operator_status]
            if item['predicted_weight'] is not None and item['actual_weight'] is not None:
                item['diff_weight_value'] = decimalSubValue(item['predicted_weight'], item['actual_weight'], 2, None)
            else:
                item['diff_weight_value'] = None
            item['create_time'] = item['create_time'].strftime("%Y-%m-%d %H:%M:%S")
            item['update_time'] = item['update_time'].strftime("%Y-%m-%d %H:%M:%S")
            item['data_time'] = item['data_time'].strftime("%Y-%m-%d %H:%M:%S")

        res['code'] = Status.SUCCESS
        res['msg'] = Message.SUCCESS
        res['data'] = {'total': total, 'pageNum': pageNum, 'pageSize': pageSize, 'data': result}
    except Exception as e:
        logger.error("get_history_page_list failed detail: {}".format(traceback.format_exc()))
        res['code'] = Status.EXCEPTION_ERROR
        res['msg'] = str(e)
        res['data'] = None

    logger.debug("get_history_page_list response: {}".format(res))

    return http_resp(res)


# 事件分页查询接口
@recordLog_bp.route('/eventPageList', methods=['POST'])
@login_required
def get_event_page_list():
    res = {}
    try:
        pageNum = request.json.get('pageNum', 1)
        pageSize = request.json.get('pageSize', 10)
        sku = request.json.get('sku')
        shift = request.json.get('shift')
        start_time = request.json.get('start_time')
        end_time = request.json.get('end_time')
        # 查询事件数据
        total, result = get_event_data_page_list(pageNum, pageSize, sku, shift, start_time, end_time)
        res['code'] = Status.SUCCESS
        res['msg'] = Message.SUCCESS
        res['data'] = {'total': total, 'pageNum': pageNum, 'pageSize': pageSize, 'data': result}
    except Exception as e:
        logger.error("get_event_page_list failed detail: {}".format(traceback.format_exc()))
        res['code'] = Status.EXCEPTION_ERROR
        res['msg'] = str(e)
        res['data'] = None

    logger.debug("get_event_page_list response: {}".format(res))

    return http_resp(res)


# 告警分页查询接口
@recordLog_bp.route('/alertPageList', methods=['POST'])
@login_required
def get_alert_page_list():
    res = {}
    try:
        pageNum = request.json.get('pageNum', 1)
        pageSize = request.json.get('pageSize', 10)
        sku = request.json.get('sku')
        shift = request.json.get('shift')
        start_time = request.json.get('start_time')
        end_time = request.json.get('end_time')
        # 查询告警数据
        total, result = get_alert_data_page_list(pageNum, pageSize, sku, shift, start_time, end_time)
        res['code'] = Status.SUCCESS
        res['msg'] = Message.SUCCESS
        res['data'] = {'total': total, 'pageNum': pageNum, 'pageSize': pageSize, 'data': result}
    except Exception as e:
        logger.error("get_alert_page_list failed detail: {}".format(traceback.format_exc()))
        res['code'] = Status.EXCEPTION_ERROR
        res['msg'] = str(e)
        res['data'] = None

    logger.debug("get_alert_page_list response: {}".format(res))

    return http_resp(res)


# 导出历史记录接口
@recordLog_bp.route('/exportHistoryList', methods=['POST'])
@login_required
def export_history_list():
    # 导出列名
    alias = ['时间', 'sku(香型)', '班次', '当前重量(g)', '3号辊间隙', '定型辊间隙', '挤压机温度', '横刀速度', '预期重量变化', '动作', '操作时间']

    sku = request.json.get('sku')
    shift = request.json.get('shift')
    start_time = request.json.get('start_time')
    end_time = request.json.get('end_time')
    # 获取数据
    dataList = export_history_data_list(alias, sku, shift, start_time, end_time)
    logger.debug("export_history_list export_data:{}".format(dataList))
    df = pd.DataFrame.from_dict({
        alias[0]: [],
        alias[1]: [],
        alias[2]: [],
        alias[3]: [],
        alias[4]: [],
        alias[5]: [],
        alias[6]: [],
        alias[7]: [],
        alias[8]: [],
        alias[9]: [],
        alias[10]: []
    })
    if dataList:
        df = pd.DataFrame(dataList)
    # 执行数据下载操作
    bio = io.BytesIO()
    with pd.ExcelWriter(bio, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='sheet1')
        wb = writer.book
        ws = writer.sheets['sheet1']
        styles1 = wb.add_format({'align': 'center', 'valign': 'vcenter'})
        styles2 = wb.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True})
        for col_num, value in enumerate(df.columns.values):
            ws.write(0, col_num, value, styles2)
        ws.set_column(0, len(df.columns)-1, cell_format=styles1, width=15)
        ws.set_default_row(20)
    bio.seek(0)  # 文件指针
    return send_file(bio,
                     download_name='{}_{}.xlsx'.format("historyData", get_cst_time_formatter("%Y%m%d%H%M%S")),
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True
                     )


# 导出事件记录接口
@recordLog_bp.route('/exportEventList', methods=['POST'])
@login_required
def export_event_list():
    # 导出列名
    alias = ['时间', 'sku(香型)', '班次', '当前重量(g)', '事件描述']

    sku = request.json.get('sku')
    shift = request.json.get('shift')
    start_time = request.json.get('start_time')
    end_time = request.json.get('end_time')
    # 获取数据
    dataList = export_event_data_list(alias, sku, shift, start_time, end_time)
    logger.debug("export_event_list export_data:{}".format(dataList))
    df = pd.DataFrame.from_dict({
        alias[0]: [],
        alias[1]: [],
        alias[2]: [],
        alias[3]: [],
        alias[4]: []
    })
    if dataList:
        df = pd.DataFrame(dataList)
    # 执行数据下载操作
    bio = io.BytesIO()
    with pd.ExcelWriter(bio, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='sheet1')
        wb = writer.book
        ws = writer.sheets['sheet1']
        styles1 = wb.add_format({'align': 'center', 'valign': 'vcenter'})
        styles2 = wb.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True})
        for col_num, value in enumerate(df.columns.values):
            ws.write(0, col_num, value, styles2)
        ws.set_column(0, len(df.columns)-1, cell_format=styles1, width=15)
        ws.set_default_row(20)
    bio.seek(0)  # 文件指针
    return send_file(bio,
                     download_name='{}_{}.xlsx'.format("eventData", get_cst_time_formatter("%Y%m%d%H%M%S")),
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True
                     )


# 导出告警记录接口
@recordLog_bp.route('/exportAlertList', methods=['POST'])
@login_required
def export_alert_list():
    # 导出列名
    alias = ['时间', 'sku(香型)', '班次', '当前重量(g)', '告警描述']

    sku = request.json.get('sku')
    shift = request.json.get('shift')
    start_time = request.json.get('start_time')
    end_time = request.json.get('end_time')
    # 获取数据
    dataList = export_alert_data_list(alias, sku, shift, start_time, end_time)
    logger.debug("export_alert_list export_data:{}".format(dataList))
    df = pd.DataFrame.from_dict({
        alias[0]: [],
        alias[1]: [],
        alias[2]: [],
        alias[3]: [],
        alias[4]: []
    })
    if dataList:
        df = pd.DataFrame(dataList)
    # 执行数据下载操作
    bio = io.BytesIO()
    with pd.ExcelWriter(bio, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='sheet1')
        wb = writer.book
        ws = writer.sheets['sheet1']
        styles1 = wb.add_format({'align': 'center', 'valign': 'vcenter'})
        styles2 = wb.add_format({'align': 'center', 'valign': 'vcenter', 'bold': True})
        for col_num, value in enumerate(df.columns.values):
            ws.write(0, col_num, value, styles2)
        ws.set_column(0, len(df.columns)-1, cell_format=styles1, width=15)
        ws.set_default_row(20)
    bio.seek(0)  # 文件指针
    return send_file(bio,
                     download_name='{}_{}.xlsx'.format("alertData", get_cst_time_formatter("%Y%m%d%H%M%S")),
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True
                     )
