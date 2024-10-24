import json
import re

import numpy as np
from flask import request, g, send_file

from config import Config
from marsproject.recordlog.service import insert_event_data_pre
from marsproject.utils.constant_value import *
from marsproject.dim_sku import sku_bp
from marsproject.utils.iam.token import login_required
from marsproject.utils.time_utils import get_cst_time_formatter
import traceback
from marsproject.dim_sku.models import *
from marsproject.utils.http_resp_util import Status, Message
import io
import pandas as pd
from marsproject.utils.http_resp_util import http_resp
from marsproject.utils.redis_util import RedisUtils
import uuid
from marsproject.utils.string_utils import numberToFixedStr, substringToFixed, getDictStrValue, coverDecimalToFloat
from marsproject.utils.log_util import get_log
from marsproject.utils.azure_storage.AzureStorage import AzureBlobStorage

logger = get_log(__name__)


# 新增接口
@sku_bp.route('/add', methods=['POST'])
@login_required
def create_sku():
    req_data = request.json
    logger.info("create_sku  param={}".format(req_data))
    res = {'code': Status.SUCCESS, 'msg': Message.SUCCESS, 'data': None}
    lock_key = RedisKey.YNG_SKU_VIEW_VALUE_LOCK
    lock_value = str(uuid.uuid4())
    try:
        if not RedisUtils.set_lock(lock_key, lock_value):
            res['code'] = Status.DATA_ERROR
            res['msg'] = Message.OPERATOR_REPEAT_ERROR
            return http_resp(res)
        if not req_data.get('sku_name'):
            res['code'] = Status.DATA_ERROR
            res['msg'] = Message.SKU_NAME_NOT_NULL
            return http_resp(res)
        if not bool(re.match(r'^[a-zA-Z]{3,4}$', req_data.get('sku_name'))):
            res['code'] = Status.DATA_ERROR
            res['msg'] = Message.SKU_NAME_ILLEGAL
            return http_resp(res)
        # 查询是否存在 sku 或 skuName 有一个存在
        count = get_sku_count_by_unique_key(req_data['sku_name'])
        if count > 0:
            res['code'] = Status.DATA_ERROR
            res['msg'] = Message.SKU_REPEAT_DATA
            return http_resp(res)

        cur_time = get_cst_time_formatter('%Y-%m-%d %H:%M:%S')
        sku_name = getDictStrValue(req_data, 'sku_name')
        fz_std = substringToFixed(getDictStrValue(req_data, 'fz_std'), 2, None)
        fz_top_limit = substringToFixed(getDictStrValue(req_data, 'fz_top_limit'), 2, None)
        fz_bottom_limit = substringToFixed(getDictStrValue(req_data, 'fz_bottom_limit'), 2, None)
        fh_std = substringToFixed(getDictStrValue(req_data, 'fh_std'), 2, None)
        fh_top_limit = substringToFixed(getDictStrValue(req_data, 'fh_top_limit'), 2, None)
        fh_bottom_limit = substringToFixed(getDictStrValue(req_data, 'fh_bottom_limit'), 2, None)
        fs_std = substringToFixed(getDictStrValue(req_data, 'fs_std'), 2, None)
        fs_top_limit = substringToFixed(getDictStrValue(req_data, 'fs_top_limit'), 2, None)
        fs_bottom_limit = substringToFixed(getDictStrValue(req_data, 'fs_bottom_limit'), 2, None)
        fc_std = substringToFixed(getDictStrValue(req_data, 'fc_std'), 2, None)
        fc_top_limit = substringToFixed(getDictStrValue(req_data, 'fc_top_limit'), 2, None)
        fc_bottom_limit = substringToFixed(getDictStrValue(req_data, 'fc_bottom_limit'), 2, None)
        fk_std = substringToFixed(getDictStrValue(req_data, 'fk_std'), 2, None)
        fk_top_limit = substringToFixed(getDictStrValue(req_data, 'fk_top_limit'), 2, None)
        fk_bottom_limit = substringToFixed(getDictStrValue(req_data, 'fk_bottom_limit'), 2, None)
        n1_roller_std = substringToFixed(getDictStrValue(req_data, 'n1_roller_std'), 4, None)
        n1_roller_top_limit = substringToFixed(getDictStrValue(req_data, 'n1_roller_top_limit'), 4, None)
        n1_roller_bottom_limit = substringToFixed(getDictStrValue(req_data, 'n1_roller_bottom_limit'), 4, None)
        n2_roller_std = substringToFixed(getDictStrValue(req_data, 'n2_roller_std'), 4, None)
        n2_roller_top_limit = substringToFixed(getDictStrValue(req_data, 'n2_roller_top_limit'), 4, None)
        n2_roller_bottom_limit = substringToFixed(getDictStrValue(req_data, 'n2_roller_bottom_limit'), 4, None)
        n3_roller_std = substringToFixed(getDictStrValue(req_data, 'n3_roller_std'), 4, None)
        n3_roller_top_limit = substringToFixed(getDictStrValue(req_data, 'n3_roller_top_limit'), 4, None)
        n3_roller_bottom_limit = substringToFixed(getDictStrValue(req_data, 'n3_roller_bottom_limit'), 4, None)
        forming_roller_std = substringToFixed(getDictStrValue(req_data, 'forming_roller_std'), 4, None)
        forming_roller_top_limit = substringToFixed(getDictStrValue(req_data, 'forming_roller_top_limit'), 4, None)
        forming_roller_bottom_limit = substringToFixed(getDictStrValue(req_data, 'forming_roller_bottom_limit'), 4, None)
        cross_cutter_speed_std = substringToFixed(getDictStrValue(req_data, 'cross_cutter_speed_std'), 2, None)
        cross_cutter_speed_top_limit = substringToFixed(getDictStrValue(req_data, 'cross_cutter_speed_top_limit'), 2, None)
        cross_cutter_speed_bottom_limit = substringToFixed(getDictStrValue(req_data, 'cross_cutter_speed_bottom_limit'), 2, None)
        extruder_temperature_std = substringToFixed(getDictStrValue(req_data, 'extruder_temperature_std'), 4, None)
        extruder_temperature_top_limit = substringToFixed(getDictStrValue(req_data, 'extruder_temperature_top_limit'), 4, None)
        extruder_temperature_bottom_limit = substringToFixed(getDictStrValue(req_data, 'extruder_temperature_bottom_limit'), 4, None)

        # 备份当前数据同步到log表一份
        insert_yng_dim_sku_log(g.user, cur_time)

        insert_yng_dim_sku((sku_name, fz_std, fz_top_limit, fz_bottom_limit, fh_std,
                            fh_top_limit, fh_bottom_limit, fs_std, fs_top_limit,
                            fs_bottom_limit, fc_std, fc_top_limit, fc_bottom_limit,
                            fk_std, fk_top_limit, fk_bottom_limit, n1_roller_std, n1_roller_top_limit,
                            n1_roller_bottom_limit, n2_roller_std, n2_roller_top_limit, n2_roller_bottom_limit,
                            n3_roller_std, n3_roller_top_limit, n3_roller_bottom_limit, forming_roller_std,
                            forming_roller_top_limit, forming_roller_bottom_limit, cross_cutter_speed_std,
                            cross_cutter_speed_top_limit, cross_cutter_speed_bottom_limit, extruder_temperature_std,
                            extruder_temperature_top_limit, extruder_temperature_bottom_limit,
                            g.user, g.user, cur_time, cur_time))

        # 记录日志
        insert_event_data_pre(type=2, type_name="参数配置", content="模型配置新增数据", operator_user=g.user)
        # 同步到数据湖
        sync_data_once_db_updates()
    except Exception as e:
        logger.error("create_sku failed detail: {}".format(traceback.format_exc()))
        res['code'] = Status.EXCEPTION_ERROR
        res['msg'] = str(e)
    finally:
        RedisUtils.release_lock(lock_key, lock_value)

    logger.debug("create_sku response: {}".format(res))
    return http_resp(res)


# 更新接口
@sku_bp.route('/update', methods=['POST'])
@login_required
def update_sku():
    req_data = request.json
    logger.info("update_sku  param={}".format(req_data))
    res = {'code': Status.SUCCESS, 'msg': Message.SUCCESS, 'data': None}
    lock_key = RedisKey.YNG_SKU_VIEW_VALUE_LOCK
    lock_value = str(uuid.uuid4())
    try:
        if not RedisUtils.set_lock(lock_key, lock_value):
            res['code'] = Status.DATA_ERROR
            res['msg'] = Message.OPERATOR_REPEAT_ERROR
            return http_resp(res)
        id = req_data.get('id')
        if not id:
            res['code'] = Status.DATA_ERROR
            res['msg'] = Message.PARAMS_LOSS
        cur_time = get_cst_time_formatter('%Y-%m-%d %H:%M:%S')
        fz_std = substringToFixed(getDictStrValue(req_data, 'fz_std'), 2, None)
        fz_top_limit = substringToFixed(getDictStrValue(req_data, 'fz_top_limit'), 2, None)
        fz_bottom_limit = substringToFixed(getDictStrValue(req_data, 'fz_bottom_limit'), 2, None)
        fh_std = substringToFixed(getDictStrValue(req_data, 'fh_std'), 2, None)
        fh_top_limit = substringToFixed(getDictStrValue(req_data, 'fh_top_limit'), 2, None)
        fh_bottom_limit = substringToFixed(getDictStrValue(req_data, 'fh_bottom_limit'), 2, None)
        fs_std = substringToFixed(getDictStrValue(req_data, 'fs_std'), 2, None)
        fs_top_limit = substringToFixed(getDictStrValue(req_data, 'fs_top_limit'), 2, None)
        fs_bottom_limit = substringToFixed(getDictStrValue(req_data, 'fs_bottom_limit'), 2, None)
        fc_std = substringToFixed(getDictStrValue(req_data, 'fc_std'), 2, None)
        fc_top_limit = substringToFixed(getDictStrValue(req_data, 'fc_top_limit'), 2, None)
        fc_bottom_limit = substringToFixed(getDictStrValue(req_data, 'fc_bottom_limit'), 2, None)
        fk_std = substringToFixed(getDictStrValue(req_data, 'fk_std'), 2, None)
        fk_top_limit = substringToFixed(getDictStrValue(req_data, 'fk_top_limit'), 2, None)
        fk_bottom_limit = substringToFixed(getDictStrValue(req_data, 'fk_bottom_limit'), 2, None)
        n1_roller_std = substringToFixed(getDictStrValue(req_data, 'n1_roller_std'), 4, None)
        n1_roller_top_limit = substringToFixed(getDictStrValue(req_data, 'n1_roller_top_limit'), 4, None)
        n1_roller_bottom_limit = substringToFixed(getDictStrValue(req_data, 'n1_roller_bottom_limit'), 4, None)
        n2_roller_std = substringToFixed(getDictStrValue(req_data, 'n2_roller_std'), 4, None)
        n2_roller_top_limit = substringToFixed(getDictStrValue(req_data, 'n2_roller_top_limit'), 4, None)
        n2_roller_bottom_limit = substringToFixed(getDictStrValue(req_data, 'n2_roller_bottom_limit'), 4, None)
        n3_roller_std = substringToFixed(getDictStrValue(req_data, 'n3_roller_std'), 4, None)
        n3_roller_top_limit = substringToFixed(getDictStrValue(req_data, 'n3_roller_top_limit'), 4, None)
        n3_roller_bottom_limit = substringToFixed(getDictStrValue(req_data, 'n3_roller_bottom_limit'), 4, None)
        forming_roller_std = substringToFixed(getDictStrValue(req_data, 'forming_roller_std'), 4, None)
        forming_roller_top_limit = substringToFixed(getDictStrValue(req_data, 'forming_roller_top_limit'), 4, None)
        forming_roller_bottom_limit = substringToFixed(getDictStrValue(req_data, 'forming_roller_bottom_limit'), 4, None)
        cross_cutter_speed_std = substringToFixed(getDictStrValue(req_data, 'cross_cutter_speed_std'), 2, None)
        cross_cutter_speed_top_limit = substringToFixed(getDictStrValue(req_data, 'cross_cutter_speed_top_limit'), 2, None)
        cross_cutter_speed_bottom_limit = substringToFixed(getDictStrValue(req_data, 'cross_cutter_speed_bottom_limit'),2, None)
        extruder_temperature_std = substringToFixed(getDictStrValue(req_data, 'extruder_temperature_std'), 4, None)
        extruder_temperature_top_limit = substringToFixed(getDictStrValue(req_data, 'extruder_temperature_top_limit'), 4, None)
        extruder_temperature_bottom_limit = substringToFixed(getDictStrValue(req_data, 'extruder_temperature_bottom_limit'), 4, None)

        # 备份当前数据同步到log表一份
        insert_yng_dim_sku_log(g.user, cur_time)
        # 更新
        update_yng_dim_sku((fz_std, fz_top_limit, fz_bottom_limit, fh_std,
                            fh_top_limit, fh_bottom_limit, fs_std, fs_top_limit,
                            fs_bottom_limit, fc_std, fc_top_limit, fc_bottom_limit,
                            fk_std, fk_top_limit, fk_bottom_limit, n1_roller_std, n1_roller_top_limit,
                            n1_roller_bottom_limit, n2_roller_std, n2_roller_top_limit, n2_roller_bottom_limit,
                            n3_roller_std, n3_roller_top_limit, n3_roller_bottom_limit, forming_roller_std,
                            forming_roller_top_limit, forming_roller_bottom_limit, cross_cutter_speed_std,
                            cross_cutter_speed_top_limit, cross_cutter_speed_bottom_limit, extruder_temperature_std,
                            extruder_temperature_top_limit, extruder_temperature_bottom_limit, g.user, cur_time, id))
        # 记录日志
        insert_event_data_pre(type=2, type_name="参数配置", content="模型配置修改数据", operator_user=g.user)
        # 同步到数据湖
        sync_data_once_db_updates()
    except Exception as e:
        logger.error("update_sku failed detail: {}".format(traceback.format_exc()))
        res['code'] = Status.EXCEPTION_ERROR
        res['msg'] = str(e)
    finally:
        RedisUtils.release_lock(lock_key, lock_value)

    logger.debug("update_sku response: {}".format(res))
    return http_resp(res)


# 删除数据
@sku_bp.route('/delete', methods=['POST'])
@login_required
def delete_sku():
    req_data = request.json
    logger.info("delete_sku  param={}".format(req_data))
    res = {'code': Status.SUCCESS, 'msg': Message.SUCCESS, 'data': None}
    lock_key = RedisKey.YNG_SKU_VIEW_VALUE_LOCK
    lock_value = str(uuid.uuid4())
    try:
        if not RedisUtils.set_lock(lock_key, lock_value):
            res['code'] = Status.DATA_ERROR
            res['msg'] = Message.OPERATOR_REPEAT_ERROR
            return http_resp(res)
        id = req_data.get('id')
        # 备份当前数据同步到log表一份
        insert_yng_dim_sku_log(g.user, get_cst_time_formatter('%Y-%m-%d %H:%M:%S'))
        # 删除数据
        delete_yng_dim_sku_by_id(id)
        # 记录日志
        insert_event_data_pre(type=2, type_name="参数配置", content="模型配置删除数据", operator_user=g.user)
        # 同步到数据湖
        sync_data_once_db_updates()
    except Exception as e:
        logger.error("delete_sku failed detail: {}".format(traceback.format_exc()))
        res['code'] = Status.EXCEPTION_ERROR
        res['msg'] = str(e)
    finally:
        RedisUtils.release_lock(lock_key, lock_value)

    logger.debug("delete_sku response: {}".format(res))
    return http_resp(res)


# 查询接口
@sku_bp.route('/pageList', methods=['POST'])
@login_required
def get_sku_pageList():
    logger.debug("get_sku_pageList  param={}".format(request.json))
    res = {}
    try:
        pageNum = request.json.get('pageNum', 1)
        pageSize = request.json.get('pageSize', 10)
        total, result = get_sku_page_list(pageNum, pageSize)
        res['code'] = Status.SUCCESS
        res['msg'] = Message.SUCCESS
        res['data'] = {'total': total, 'pageNum': pageNum, 'pageSize': pageSize, 'data': result}
    except Exception as e:
        logger.error("get_sku_pageList failed detail: {}".format(traceback.format_exc()))
        res['code'] = Status.EXCEPTION_ERROR
        res['msg'] = str(e)
        res['data'] = None

    logger.debug("get_sku_pageList response: {}".format(res))
    return http_resp(res)


# 导出接口
@sku_bp.route('/export', methods=['GET'])
@login_required
def export_data():
    # 导出列名
    alias = ['skuName', '重量_STD', '重量_UB', '重量_LB', '厚度_STD', '厚度_UB', '厚度_LB', '深度_STD',
             '深度_UB', '深度_LB', '长度_STD', '长度_UB', '长度_LB', '宽度_STD', '宽度_UB', '宽度_LB',
             '1号辊_Step_UB', '1号辊_UB', '1号辊_LB', '2号辊_Step_UB', '2号辊_UB', '2号辊_LB', '3号辊_Step_UB',
             '3号辊_UB', '3号辊_LB', '定型辊_Step_UB', '定型辊_UB', '定型辊_LB', '横刀_Step_UB', '横刀_UB', '横刀_LB',
             '挤压机_Step_UB', '挤压机_UB', '挤压机_LB']
    # 获取数据
    dataList = get_export_sku_list(alias)
    logger.debug("sku export_data:{}".format(dataList))
    df = pd.DataFrame.from_dict({alias[i]: [] for i in range(len(alias))})
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
                     download_name='{}_{}.xlsx'.format("sku", get_cst_time_formatter("%Y%m%d%H%M%S")),
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True
                     )


# 同步配方表到数据湖
#     '重量_UB': 'Weight_UB',
#     '重量_LB': 'Weight_LB',
#     '厚度_UB': 'Thickness_UB',
#     '厚度_LB': 'Thickness_LB',
#     '深度_UB': 'Depth_UB',
#     '深度_LB': 'Depth_LB',
#     '长度_UB': 'Length_UB',
#     '长度_LB': 'Length_LB',
#     '宽度_UB': 'Width_UB',
#     '宽度_LB': 'Width_LB',
#     '1号辊_Step_UB': 'Gap1_Step_UB',
#     '1号辊_UB': 'Gap1_UB',
#     '1号辊_LB': 'Gap1_LB',
#     '2号辊_Step_UB': 'Gap2_Step_UB',
#     '2号辊_UB': 'Gap2_UB',
#     '2号辊_LB': 'Gap2_LB',
#     '3号辊_Step_UB': 'Gap3_Step_UB',
#     '3号辊_UB': 'Gap3_UB',
#     '3号辊_LB': 'Gap3_LB',
#     '定型辊_Step_UB': 'GapFS_Step_UB',
#     '定型辊_UB': 'GapFS_UB',
#     '定型辊_LB': 'GapFS_LB',
#     '横刀_Step_UB': 'CS_Step_UB',
#     '横刀_UB': 'CS_UB',
#     '横刀_LB': 'CS_LB',
#     '挤压机_Step_UB': 'Temp_Step_UB',
#     '挤压机_UB': 'Temp_UB',
#     '挤压机_LB': 'Temp_LB'
def sync_data_once_db_updates():
    try:
        all_list = get_all_sku_list()
        res_dict = {
            item['sku_name']: {
                "fz_std": coverDecimalToFloat(item, "fz_std"),
                "Weight_UB": coverDecimalToFloat(item, "fz_top_limit"),
                "Weight_LB": coverDecimalToFloat(item, "fz_bottom_limit"),
                "fh_std": coverDecimalToFloat(item, "fh_std"),
                "Thickness_UB": coverDecimalToFloat(item, "fh_top_limit"),
                "Thickness_LB": coverDecimalToFloat(item, "fh_bottom_limit"),
                "fs_std": coverDecimalToFloat(item, "fs_std"),
                "Depth_UB": coverDecimalToFloat(item, "fs_top_limit"),
                "Depth_LB": coverDecimalToFloat(item, "fs_bottom_limit"),
                "fc_std": coverDecimalToFloat(item, "fc_std"),
                "Length_UB": coverDecimalToFloat(item, "fc_top_limit"),
                "Length_LB": coverDecimalToFloat(item, "fc_bottom_limit"),
                "fk_std": coverDecimalToFloat(item, "fk_std"),
                "Width_UB": coverDecimalToFloat(item, "fk_top_limit"),
                "Width_LB": coverDecimalToFloat(item, "fk_bottom_limit"),
                "Gap1_Step_UB": coverDecimalToFloat(item, "n1_roller_std"),
                "Gap1_UB": coverDecimalToFloat(item, "n1_roller_top_limit"),
                "Gap1_LB": coverDecimalToFloat(item, "n1_roller_bottom_limit"),
                "Gap2_Step_UB": coverDecimalToFloat(item, "n2_roller_std"),
                "Gap2_UB": coverDecimalToFloat(item, "n2_roller_top_limit"),
                "Gap2_LB": coverDecimalToFloat(item, "n2_roller_bottom_limit"),
                "Gap3_Step_UB": coverDecimalToFloat(item, "n3_roller_std"),
                "Gap3_UB": coverDecimalToFloat(item, "n3_roller_top_limit"),
                "Gap3_LB": coverDecimalToFloat(item, "n3_roller_bottom_limit"),
                "GapFS_Step_UB": coverDecimalToFloat(item, "forming_roller_std"),
                "GapFS_UB": coverDecimalToFloat(item, "forming_roller_top_limit"),
                "GapFS_LB": coverDecimalToFloat(item, "forming_roller_bottom_limit"),
                "CS_Step_UB": coverDecimalToFloat(item, "cross_cutter_speed_std"),
                "CS_UB": coverDecimalToFloat(item, "cross_cutter_speed_top_limit"),
                "CS_LB": coverDecimalToFloat(item, "cross_cutter_speed_bottom_limit"),
                "Temp_Step_UB": coverDecimalToFloat(item, "extruder_temperature_std"),
                "Temp_UB": coverDecimalToFloat(item, "extruder_temperature_top_limit"),
                "Temp_LB": coverDecimalToFloat(item, "extruder_temperature_bottom_limit")
        } for item in all_list}

        if res_dict:
            Blob_Target = AzureBlobStorage(connection_string=Config.BLOB_SOURCE_CONN_STR)
            Blob_Target.upload_blob(Config.BLOB_SOURCE_CONTAINER_NAME,
                                    'productionConfigYNG/sku_config.json',
                                    json.dumps(res_dict))
    except Exception as e:
        logger.error("sync_data_once_db_updates failed detail: {}".format(str(e)))
        logger.error("sync_data_once_db_updates failed detail: {}".format(traceback.format_exc()))