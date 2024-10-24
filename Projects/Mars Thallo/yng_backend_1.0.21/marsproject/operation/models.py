import time
import traceback

from marsproject.utils.db.db_factory import AzureDBFactory as azure_db_factory
from marsproject.utils.db.db2_factory import AzureDB2Factory as azure_db2_factory
from marsproject.utils.db.azure_utils import DBConnector
import uuid
from marsproject.utils.time_utils import get_cst_time_formatter
from marsproject.utils.log_util import get_log
from marsproject.utils.string_utils import arrToSplString, coverNoValueToNone

logger = get_log(__name__)


# 保存实时数据最新的一条
def insert_ts_raw_last_data(obj):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        cur_time = get_cst_time_formatter('%Y-%m-%d %H:%M:%S')
        uid = str(uuid.uuid4()).replace("-", "")
        SQL = """
               insert into dbo.yng_ts_raw_last_data(
                       id,
                       ts,
                       name,
                       value,
                       create_time,
                       update_time)
               values ('{}','{}', N'{}', N'{}','{}','{}')
           """.format(uid,
                      obj['ts'],
                      obj['name'],
                      obj['value'],
                      cur_time,
                      cur_time)
        logger.debug("insert_ts_raw_last_data SQL:{}".format(SQL))
        azuresql.execute_non_query(SQL)
        return uid
    except Exception as e:
        logger.error("insert_ts_raw_last_data failed detail: {}".format(str(e)))
        logger.error("insert_ts_raw_last_data failed detail: {}".format(traceback.format_exc()))
        return None
    finally:
        azuresql.close()


# 更新数据
def update_ts_raw_last_data(ts, value, id):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        cur_time = get_cst_time_formatter('%Y-%m-%d %H:%M:%S')
        SQL = """update dbo.yng_ts_raw_last_data
                    set ts = '{}', 
                        value = N'{}', 
                        update_time = '{}' 
                        where id = '{}'  
               """.format(ts, value, cur_time, id)
        logger.debug("update_ts_raw_last_data SQL:{}".format(SQL))
        azuresql.execute_non_query(SQL)
    except Exception as e:
        logger.error("update_ts_raw_last_data failed detail: {}".format(str(e)))
        logger.error("update_ts_raw_last_data failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 删除数据
def delete_ts_raw_last_data(name):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = "delete from dbo.yng_ts_raw_last_data  where name = N'{}' ".format(name)
        logger.debug("delete_ts_raw_last_data SQL:{}".format(SQL))
        azuresql.execute_non_query(SQL)
    except Exception as e:
        logger.error("delete_ts_raw_last_data failed detail: {}".format(str(e)))
        logger.error("delete_ts_raw_last_data failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 查询 实时数据最新的一条
def get_single_ts_raw_last_data(name):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        FILTER = " where name = N'{}' order by create_time desc".format(name)
        SQL = "select TOP 1 * from dbo.yng_ts_raw_last_data"
        SQL = SQL + FILTER
        logger.debug("get_single_ts_raw_last_data SQL:{}".format(SQL))
        res = azuresql.execute_query_dict(SQL)
        if len(res) > 0:
            return res[0]
        return None
    except Exception as e:
        logger.error("get_single_ts_raw_last_data failed detail: {}".format(str(e)))
        logger.error("get_single_ts_raw_last_data failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 根据多个name查询 实时数据
def get_ts_raw_last_data(arr_name):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        FILTER = " where name in ({}) order by create_time desc".format(arrToSplString(arr_name, 'N'))
        SQL = "select TOP {} * from dbo.yng_ts_raw_last_data".format(len(arr_name))
        SQL = SQL + FILTER
        logger.debug("get_ts_raw_last_data SQL:{}".format(SQL))
        res = azuresql.execute_query_dict(SQL)
        return res
    except Exception as e:
        logger.error("get_ts_raw_last_data failed detail: {}".format(str(e)))
        logger.error("get_ts_raw_last_data failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 获取字段数据
def get_dict_item_data(code):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = """
                select b.item_value from dbo.yng_dict_item a 
                inner join dbo.yng_dict_item_detail b on a.id = b.dict_item_id 
                where a.code = '{}'
                order by b.seq
              """.format(code)
        logger.debug("get_dict_item_data SQL:{}".format(SQL))
        res = azuresql.execute_query(SQL)
        return [item[0] for item in res] if res else []
    except Exception as e:
        logger.error("get_dict_item_data failed detail: {}".format(str(e)))
        logger.error("get_dict_item_data failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 查询 表头数据最新一条
def get_single_spc_weight_last_data(entryType, endTime):
    conn = azure_db2_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = """
                select    TOP (1)
                          a.ID    AS id
                         ,a.FDate AS data_time
                         ,a.FItemCode AS item_code
                         ,b.fItemName AS item
                         ,a.FHoudu AS length_or_thickness
                         ,a.FShendu AS width_or_depth
                         ,a.FUser AS operator
                         ,a.FbanCode AS shift
                         ,a.FHStd AS length_or_thickness_std
                         ,a.FSStd AS width_or_depth_std
                         ,a.FStatus AS status
                         ,a.FLoad AS load
                         ,a.FXJType AS entry_type
                         ,a.FZStd AS target
                         ,a.FZhong AS actual
                FROM dbo.TReceive a LEFT JOIN dbo.TItem b ON a.FItemCode = b.fItemCode
                WHERE a.FXJType = {} and a.FDate < '{}' ORDER BY a.FDate DESC
        """.format(entryType, endTime)
        logger.debug("get_single_spc_weight_last_data SQL:{}".format(SQL))
        res = azuresql.execute_query_dict(SQL)
        if len(res) > 0:
            return res[0]
        return None
    except Exception as e:
        logger.error("get_single_spc_weight_last_data failed detail: {}".format(str(e)))
        logger.error("get_single_spc_weight_last_data failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 查询 spc数据
def get_spc_weight_limit_data(num, entryType):
    conn = azure_db2_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = """
                  select  TOP ({})
                          a.ID  AS id
                         ,a.FDate AS data_time
                         ,a.FItemCode AS item_code
                         ,b.fItemName AS item
                         ,a.FHoudu AS length_or_thickness
                         ,a.FShendu AS width_or_depth
                         ,a.FUser AS operator
                         ,a.FbanCode AS shift
                         ,a.FHStd AS length_or_thickness_std
                         ,a.FSStd AS width_or_depth_std
                         ,a.FStatus AS status
                         ,a.FLoad AS load
                         ,a.FXJType AS entry_type
                         ,a.FZStd AS target
                         ,a.FZhong AS actual
                FROM dbo.TReceive a LEFT JOIN dbo.TItem b ON a.FItemCode = b.fItemCode
                WHERE a.FXJType = {} ORDER BY a.FDate DESC
        """.format(num, entryType)
        logger.debug("get_spc_weight_limit_data SQL:{}".format(SQL))
        res = azuresql.execute_query_dict(SQL)
        return res
    except Exception as e:
        logger.error("get_spc_weight_limit_data failed detail: {}".format(str(e)))
        logger.error("get_spc_weight_limit_data failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 根据时间查询 spc数据
def get_spc_weight_data_by_time(entryType, startTime, endTime):
    conn = azure_db2_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = """
                  select  a.ID  AS id
                         ,a.FDate AS data_time
                         ,a.FItemCode AS item_code
                         ,b.fItemName AS item
                         ,a.FHoudu AS length_or_thickness
                         ,a.FShendu AS width_or_depth
                         ,a.FUser AS operator
                         ,a.FbanCode AS shift
                         ,a.FHStd AS length_or_thickness_std
                         ,a.FSStd AS width_or_depth_std
                         ,a.FStatus AS status
                         ,a.FLoad AS load
                         ,a.FXJType AS entry_type
                         ,a.FZStd AS target
                         ,a.FZhong AS actual
                FROM dbo.TReceive a LEFT JOIN dbo.TItem b ON a.FItemCode = b.fItemCode
                WHERE a.FXJType = {} and a.FDate >= '{}' AND a.FDate <= '{}' ORDER BY a.FDate
        """.format(entryType, startTime, endTime)
        logger.debug("get_spc_weight_data_by_time SQL:{}".format(SQL))
        res = azuresql.execute_query_dict(SQL)
        return res
    except Exception as e:
        logger.error("get_spc_weight_data_by_time failed detail: {}".format(str(e)))
        logger.error("get_spc_weight_data_by_time failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def insert_recommend_weight_data(obj):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = """
                insert into dbo.yng_recommend_weight_data (
                                                    sku, 
                                                    formula,
                                                    extruder_temperature,
                                                    extruder_exit_gum_temp,
                                                    slice_product_line_speed,
                                                    n1_roller_gap,
                                                    n2_roller_gap,
                                                    n3_roller_gap,
                                                    forming_roller_gap,
                                                    extruder_temperature_up,
                                                    cross_cutter_speed,
                                                    target_weight,
                                                    data_time,
                                                    weight_ts,
                                                    shift,
                                                    actual_weight,
                                                    recommend_1_roller_gap,
                                                    recommend_2_roller_gap,
                                                    recommend_3_roller_gap,
                                                    recommend_forming_roller_gap,
                                                    recommend_extruder_temperature_up,
                                                    recommend_cross_cutter_speed,
                                                    predicted_weight,
                                                    operator_status,
                                                    operator_reason,
                                                    write_back_status,
                                                    create_by,
                                                    update_by,
                                                    create_time,
                                                    update_time
                                        ) OUTPUT INSERTED.ID values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
        logger.debug("insert_recommend_weight_data SQL:{}".format(SQL))
        res = azuresql.execute_pre_save_result_lastId(SQL, obj)
        return res
    except Exception as e:
        logger.error("insert_recommend_weight_data failed detail: {}".format(str(e)))
        logger.error("insert_recommend_weight_data failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def insert_recommend_weight_data_log(obj):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = """
                insert into dbo.yng_recommend_weight_data_log (
                                                    is_change, 
                                                    sku, 
                                                    formula, 
                                                    extruder_temperature,
                                                    extruder_exit_gum_temp,
                                                    slice_product_line_speed, 
                                                    n1_roller_gap,
                                                    n2_roller_gap,
                                                    n3_roller_gap, 
                                                    forming_roller_gap,
                                                    extruder_temperature_up,
                                                    cross_cutter_speed,
                                                    target_weight, 
                                                    data_time,  
                                                    weight_ts,  
                                                    shift, 
                                                    actual_weight,
                                                    ai_res_actual_weight, 
                                                    recommend_1_roller_gap, 
                                                    recommend_2_roller_gap, 
                                                    recommend_3_roller_gap, 
                                                    recommend_forming_roller_gap, 
                                                    recommend_extruder_temperature_up,
                                                    recommend_cross_cutter_speed,
                                                    predicted_weight_before_change, 
                                                    predicted_weight_after_change, 
                                                    recommend_weight_data_id, 
                                                    create_by, 
                                                    update_by, 
                                                    create_time,
                                                    update_time
                                        ) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """
        logger.debug("insert_recommend_weight_data_log SQL:{}".format(SQL))
        azuresql.execute_non_query_statement(SQL, obj)
    except Exception as e:
        logger.error("insert_recommend_weight_data_log failed detail: {}".format(str(e)))
        logger.error("insert_recommend_weight_data_log failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 根据id查询 推荐数据
def get_single_recommend_weight_data_by_id(id):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = "select TOP 1 * from dbo.yng_recommend_weight_data where id={}".format(id)
        logger.debug("get_single_recommend_weight_data_by_id SQL:{}".format(SQL))
        res = azuresql.execute_query_dict(SQL)
        return res[0]
    except Exception as e:
        logger.error("get_single_recommend_weight_data_by_id failed detail: {}".format(str(e)))
        logger.error("get_single_recommend_weight_data_by_id failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 根据id查询 推荐数据
def get_single_recommend_weight_last_data():
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = "select TOP 1 * from dbo.yng_recommend_weight_data order by id desc"
        logger.debug("get_single_recommend_weight_last_data SQL:{}".format(SQL))
        res = azuresql.execute_query_dict(SQL)
        if len(res) > 0:
            return res[0]
        return None
    except Exception as e:
        logger.error("get_single_recommend_weight_last_data failed detail: {}".format(str(e)))
        logger.error("get_single_recommend_weight_last_data failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 查询 推荐数据
def get_recommend_weight_limit_data(num):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = "select TOP {} * from dbo.yng_recommend_weight_data order by id desc".format(num)
        logger.debug("get_recommend_weight_limit_data SQL:{}".format(SQL))
        res = azuresql.execute_query_dict(SQL)
        return res
    except Exception as e:
        logger.error("get_recommend_weight_limit_data failed detail: {}".format(str(e)))
        logger.error("get_recommend_weight_limit_data failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 更新推荐数据
def update_recommend_weight_data(obj):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        FILTER = " where id = {} ".format(obj['id'])
        SQL = " update dbo.yng_recommend_weight_data set "
        if "recommend_1_roller_gap" in obj:
            SQL = SQL + " recommend_1_roller_gap ={},".format(coverNoValueToNone(obj, 'recommend_1_roller_gap'))
        if "recommend_2_roller_gap" in obj:
            SQL = SQL + " recommend_2_roller_gap ={},".format(coverNoValueToNone(obj, 'recommend_2_roller_gap'))
        if "recommend_3_roller_gap" in obj:
            SQL = SQL + " recommend_3_roller_gap ={},".format(coverNoValueToNone(obj, 'recommend_3_roller_gap'))
        if "recommend_forming_roller_gap" in obj:
            SQL = SQL + " recommend_forming_roller_gap = {},".format(coverNoValueToNone(obj, 'recommend_forming_roller_gap'))
        if "recommend_extruder_temperature_up" in obj:
            SQL = SQL + " recommend_extruder_temperature_up ={},".format(coverNoValueToNone(obj, 'recommend_extruder_temperature_up'))
        if "recommend_cross_cutter_speed" in obj:
            SQL = SQL + " recommend_cross_cutter_speed ={},".format(coverNoValueToNone(obj, 'recommend_cross_cutter_speed'))
        if "operator_status" in obj and obj.get('operator_status') is not None:
            SQL = SQL + " operator_status = {},".format(obj.get('operator_status'))
        if "write_back_status" in obj and obj.get('write_back_status') is not None:
            SQL = SQL + " write_back_status = {},".format(obj.get('write_back_status'))
        if "operator_reason" in obj and obj.get('operator_reason'):
            SQL = SQL + " operator_reason = N'{}',".format(obj.get('operator_reason'))
        SQL = SQL + " update_by = N'{}',".format(obj.get('operator_user'))
        SQL = SQL + " update_time = '{}'".format(get_cst_time_formatter('%Y-%m-%d %H:%M:%S'))
        SQL = SQL + FILTER
        logger.debug("update_recommend_weight_data SQL:{}".format(SQL))
        azuresql.execute_non_query(SQL)
    except Exception as e:
        logger.error("update_recommend_weight_data failed detail: {}".format(str(e)))
        logger.error("update_recommend_weight_data failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 根据多个name查询 实时数据
def get_single_ts_data_action_and_value(en_name):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = """
                select TOP(1) a.cn_name, a.action_code, b.id as ts_data_id, b.value,b.ts from dbo.yng_ts_raw_data_action_config  a 
                left join dbo.yng_ts_raw_last_data b on a.en_name = b.name
                where a.en_name = '{}' ORDER BY b.create_time DESC
                """.format(en_name)
        logger.debug("get_single_ts_data_action_and_value SQL:{}".format(SQL))
        res = azuresql.execute_query_dict(SQL)
        if len(res) > 0:
            return res[0]
        return None
    except Exception as e:
        logger.error("get_single_ts_data_action_and_value failed detail: {}".format(str(e)))
        logger.error("get_single_ts_data_action_and_value failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 根据多个表字段名查询每个tag点位的最新的时序数据值
def get_multi_ts_last_value(arr_name):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = """
                select a.*, b.value, b.update_time as tag_time from dbo.yng_ts_raw_data_action_config  a 
                left join dbo.yng_ts_raw_last_data b on a.en_name = b.name
                where a.map_tb_field_name  in ({}) ORDER BY b.create_time DESC
                """.format(arrToSplString(arr_name, 'N'))
        logger.debug("get_multi_ts_last_value SQL:{}".format(SQL))
        res = azuresql.execute_query_dict(SQL)
        return res
    except Exception as e:
        logger.error("get_multi_ts_last_value failed detail: {}".format(str(e)))
        logger.error("get_multi_ts_last_value failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 根据id查询 根据状态查询推荐数据
def get_single_recommend_weight_data_by_status(operator_status):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = "select TOP 1 * from dbo.yng_recommend_weight_data where operator_status = {} order by id desc".format(operator_status)
        logger.debug("get_single_recommend_weight_data_by_status SQL:{}".format(SQL))
        res = azuresql.execute_query_dict(SQL)
        if len(res) > 0:
            return res[0]
        return None
    except Exception as e:
        logger.error("get_single_recommend_weight_data_by_status failed detail: {}".format(str(e)))
        logger.error("get_single_recommend_weight_data_by_status failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()

