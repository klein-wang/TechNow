import time
import traceback

from marsproject.utils.db.db_factory import AzureDBFactory as azure_db_factory
from marsproject.utils.db.azure_utils import DBConnector
from marsproject.utils.time_utils import get_cst_time_formatter
from marsproject.utils.log_util import get_log
logger = get_log(__name__)


# 插入事件日志信息
def insert_event_data(obj):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        cur_time = get_cst_time_formatter('%Y-%m-%d %H:%M:%S')
        SQL = """   insert into dbo.yng_event_log (
                                                   sku,
                                                   shift,
                                                   actual_weight,
                                                   type,
                                                   type_name,
                                                   event_time,
                                                   content,
                                                   content_ext,
                                                   create_by,
                                                   update_by,
                                                   create_time,
                                                   update_time
                        ) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                      """
        logger.debug("insert_event_data SQL:{}".format(SQL))
        azuresql.execute_non_query_statement(SQL, (
                                 obj.get('sku', None),
                                 obj.get('shift', None),
                                 obj.get('actual_weight', None),
                                 obj['type'],
                                 obj['type_name'],
                                 cur_time,
                                 obj['content'],
                                 obj['content_ext'],
                                 obj['operator_user'],
                                 obj['operator_user'],
                                 cur_time,
                                 cur_time))
    except Exception as e:
        logger.error("insert_event_data failed detail: {}".format(str(e)))
        logger.error("insert_event_data failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 插入异常告警日志信息
def insert_alert_log_data(obj):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        cur_time = get_cst_time_formatter('%Y-%m-%d %H:%M:%S')
        SQL = """   insert into dbo.yng_alert_log (
                                                   sku,
                                                   shift,
                                                   actual_weight,
                                                   alert_time,
                                                   content,
                                                   create_by,
                                                   update_by,
                                                   create_time,
                                                   update_time
                        ) values(?, ?, ?, ?, ?, ?, ?, ?, ?)
                      """
        logger.debug("insert_son_alert_log_data SQL:{}".format(SQL))
        azuresql.execute_non_query_statement(SQL, (obj.get('sku', None),
                                                   obj.get('shift', None),
                                                   obj.get('actual_weight', None),
                                                   cur_time,
                                                   obj['content'],
                                                   obj['operator_user'],
                                                   obj['operator_user'],
                                                   cur_time,
                                                   cur_time))
    except Exception as e:
        logger.error("insert_son_alert_log_data failed detail: {}".format(str(e)))
        logger.error("insert_son_alert_log_data failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 查询事件数据
def get_event_data(lastTime, limit):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = "select TOP {} * from dbo.yng_event_log where create_time >= '{}' order by id desc".format(limit, lastTime)
        logger.debug("get_event_data SQL:{}".format(SQL))
        res = azuresql.execute_query_dict(SQL)
        return res
    except Exception as e:
        logger.error("get_event_data failed detail: {}".format(str(e)))
        logger.error("get_event_data failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 查询告警数据
def get_alert_data(lastTime):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = "select * from dbo.yng_alert_log where create_time >= '{}' order by id desc".format(lastTime)
        logger.debug("get_alert_data SQL:{}".format(SQL))
        res = azuresql.execute_query_dict(SQL)
        return res
    except Exception as e:
        logger.error("get_alert_data failed detail: {}".format(str(e)))
        logger.error("get_alert_data failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 分页查询历史数据
def get_history_page_list_data(pageNum, pageSize, sku, shift, start_time, end_time):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        WHERE = "WHERE 1=1 "
        if sku:
            WHERE = WHERE + "AND sku = N'{}' ".format(sku)
        if shift:
            WHERE = WHERE + "AND shift = N'{}' ".format(shift)
        if start_time:
            WHERE = WHERE + "AND data_time >= '{}' ".format(start_time)
        if end_time:
            WHERE = WHERE + "AND data_time <= '{}' ".format(end_time)

        SQL1 = "select COUNT(*) AS total from dbo.yng_recommend_weight_data "
        SQL1 = SQL1 + WHERE
        resCount = azuresql.execute_query_dict(SQL1)
        total = resCount[0]['total'] if resCount else 0

        SQL2 = "select * from dbo.yng_recommend_weight_data "
        Paginitor = """ OFFSET ({}-1)*{} ROWS FETCH NEXT {} ROWS ONLY """.format(pageNum, pageSize, pageSize)
        SORT = " order by id desc"
        SQL2 = SQL2 + WHERE + SORT + Paginitor
        logger.debug("get_history_page_list_data SQL:{}".format(SQL2))
        res = azuresql.execute_query_dict(SQL2)
        return total, res
    except Exception as e:
        logger.error("get_history_page_list_data failed detail: {}".format(str(e)))
        logger.error("get_history_page_list_data failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 分页查询事件数据
def get_event_data_page_list(pageNum, pageSize, sku, shift, start_time, end_time):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        WHERE = "WHERE 1=1 "
        if sku:
            WHERE = WHERE + "AND sku = N'{}' ".format(sku)
        if shift:
            WHERE = WHERE + "AND shift = N'{}' ".format(shift)
        if start_time:
            WHERE = WHERE + "AND create_time >= '{}' ".format(start_time)
        if end_time:
            WHERE = WHERE + "AND create_time <= '{}' ".format(end_time)

        SQL1 = "select COUNT(*) AS total from dbo.yng_event_log "
        SQL1 = SQL1 + WHERE
        resCount = azuresql.execute_query_dict(SQL1)
        total = resCount[0]['total'] if resCount else 0

        SQL2 = "select * from dbo.yng_event_log "
        Paginitor = """ OFFSET ({}-1)*{} ROWS FETCH NEXT {} ROWS ONLY """.format(pageNum, pageSize, pageSize)
        SORT = " order by id desc"
        SQL2 = SQL2 + WHERE + SORT + Paginitor
        logger.debug("get_event_data_page_list SQL:{}".format(SQL2))
        res = azuresql.execute_query_dict(SQL2)
        return total, res
    except Exception as e:
        logger.error("get_event_data_page_list failed detail: {}".format(str(e)))
        logger.error("get_event_data_page_list failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 分页查询告警数据
def get_alert_data_page_list(pageNum, pageSize, sku, shift, start_time, end_time):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        WHERE = "WHERE 1=1 "
        if sku:
            WHERE = WHERE + "AND sku = N'{}' ".format(sku)
        if shift:
            WHERE = WHERE + "AND shift = N'{}' ".format(shift)
        if start_time:
            WHERE = WHERE + "AND create_time >= '{}' ".format(start_time)
        if end_time:
            WHERE = WHERE + "AND create_time <= '{}' ".format(end_time)

        SQL1 = "select COUNT(*) AS total from dbo.yng_alert_log "
        SQL1 = SQL1 + WHERE
        resCount = azuresql.execute_query_dict(SQL1)
        total = resCount[0]['total'] if resCount else 0

        SQL2 = "select * from dbo.yng_alert_log "
        Paginitor = """ OFFSET ({}-1)*{} ROWS FETCH NEXT {} ROWS ONLY """.format(pageNum, pageSize, pageSize)
        SORT = " order by id desc"
        SQL2 = SQL2 + WHERE + SORT + Paginitor
        logger.debug("get_event_data_page_list SQL:{}".format(SQL2))
        res = azuresql.execute_query_dict(SQL2)
        return total, res
    except Exception as e:
        logger.error("get_event_data_page_list failed detail: {}".format(str(e)))
        logger.error("get_event_data_page_list failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 导出历史记录查询
def export_history_data_list(alias, sku, shift, start_time, end_time):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        WHERE = "WHERE 1=1 "
        if sku:
            WHERE = WHERE + "AND sku = N'{}' ".format(sku)
        if shift:
            WHERE = WHERE + "AND shift = N'{}' ".format(shift)
        if start_time:
            WHERE = WHERE + "AND data_time >= '{}' ".format(start_time)
        if end_time:
            WHERE = WHERE + "AND data_time <= '{}' ".format(end_time)

        SQL = """select  
                       data_time                          AS '{}',
                       sku                                AS '{}',
                       shift                              AS '{}',
                       actual_weight                      AS '{}',
                       recommend_3_roller_gap             AS '{}',
                       recommend_forming_roller_gap       AS '{}',
                       recommend_extruder_temperature_up  AS '{}',
                       recommend_cross_cutter_speed       AS '{}',
                       CASE 
                        WHEN predicted_weight IS NULL OR actual_weight IS NULL 
                        THEN NULL
                        ELSE predicted_weight - actual_weight
                       END                                             AS '{}',
                       CASE operator_status
                           when 1 then '接受' when 2 then '部分接受' 
                           when 3 then '拒绝'  ELSE '未操作' 
                       END                                             AS '{}',
                      CASE 
                            WHEN operator_status IS NULL OR operator_status = 0
                            THEN NULL
                            ELSE update_time
                      END                                               AS '{}'

                from dbo.yng_recommend_weight_data 
        """.format(alias[0], alias[1], alias[2], alias[3], alias[4], alias[5], alias[6], alias[7], alias[8], alias[9], alias[10])
        SQL = SQL + WHERE + "order by id desc"
        logger.debug("export_history_data_list SQL:{}".format(SQL))
        res = azuresql.execute_query_dict(SQL)
        return res
    except Exception as e:
        logger.error("export_history_data_list failed detail: {}".format(str(e)))
        logger.error("export_history_data_list failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 导出事件记录查询
def export_event_data_list(alias, sku, shift, start_time, end_time):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        WHERE = "WHERE 1=1 "
        if sku:
            WHERE = WHERE + "AND sku = N'{}' ".format(sku)
        if shift:
            WHERE = WHERE + "AND shift = N'{}' ".format(shift)
        if start_time:
            WHERE = WHERE + "AND create_time >= '{}' ".format(start_time)
        if end_time:
            WHERE = WHERE + "AND create_time <= '{}' ".format(end_time)

        SQL = """select  
                       event_time                 AS '{}',
                       sku                        AS '{}',
                       shift                      AS '{}',
                       actual_weight              AS '{}',
                       content                    AS '{}'
                from dbo.yng_event_log 
        """.format(alias[0], alias[1], alias[2], alias[3], alias[4])
        SQL = SQL + WHERE + "order by id desc"
        logger.debug("export_event_data_list SQL:{}".format(SQL))
        res = azuresql.execute_query_dict(SQL)
        return res
    except Exception as e:
        logger.error("export_event_data_list failed detail: {}".format(str(e)))
        logger.error("export_event_data_list failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 导出告警记录查询
def export_alert_data_list(alias, sku, shift, start_time, end_time):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        WHERE = "WHERE 1=1 "
        if sku:
            WHERE = WHERE + "AND sku = N'{}' ".format(sku)
        if shift:
            WHERE = WHERE + "AND shift = N'{}' ".format(shift)
        if start_time:
            WHERE = WHERE + "AND create_time >= '{}' ".format(start_time)
        if end_time:
            WHERE = WHERE + "AND create_time <= '{}' ".format(end_time)

        SQL = """select  
                       alert_time                 AS '{}',
                       sku                        AS '{}',
                       shift                      AS '{}',
                       actual_weight              AS '{}',
                       content                    AS '{}'
                from dbo.yng_alert_log 
        """.format(alias[0], alias[1], alias[2], alias[3], alias[4])
        SQL = SQL + WHERE + "order by id desc"
        logger.debug("export_alert_data_list SQL:{}".format(SQL))
        res = azuresql.execute_query_dict(SQL)
        return res
    except Exception as e:
        logger.error("export_alert_data_list failed detail: {}".format(str(e)))
        logger.error("export_alert_data_list failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()

