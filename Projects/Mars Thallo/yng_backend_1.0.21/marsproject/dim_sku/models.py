import traceback

from marsproject.utils.db.db_factory import AzureDBFactory as azure_db_factory
from marsproject.utils.db.azure_utils import DBConnector
from marsproject.utils.log_util import get_log

logger = get_log(__name__)


# 保存sku数据
def insert_yng_dim_sku(obj):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = """
                insert into dbo.yng_dim_sku_data (
                                                sku_name,
                                                fz_std,
                                                fz_top_limit,
                                                fz_bottom_limit,
                                                fh_std,
                                                fh_top_limit,
                                                fh_bottom_limit,
                                                fs_std,
                                                fs_top_limit,
                                                fs_bottom_limit,
                                                fc_std,
                                                fc_top_limit,
                                                fc_bottom_limit,
                                                fk_std,
                                                fk_top_limit,
                                                fk_bottom_limit,
                                                n1_roller_std,
                                                n1_roller_top_limit,
                                                n1_roller_bottom_limit,
                                                n2_roller_std,
                                                n2_roller_top_limit,
                                                n2_roller_bottom_limit,
                                                n3_roller_std,
                                                n3_roller_top_limit,
                                                n3_roller_bottom_limit,
                                                forming_roller_std,
                                                forming_roller_top_limit,
                                                forming_roller_bottom_limit,
                                                cross_cutter_speed_std,
                                                cross_cutter_speed_top_limit,
                                                cross_cutter_speed_bottom_limit,
                                                extruder_temperature_std,
                                                extruder_temperature_top_limit,
                                                extruder_temperature_bottom_limit,
                                                create_by, 
                                                update_by, 
                                                create_time,
                                                update_time
                                        ) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                                         ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        logger.debug("insert_yng_dim_sku SQL:{}".format(SQL))
        azuresql.execute_non_query_statement(SQL, obj)
    except Exception as e:
        logger.error("insert_yng_dim_sku failed detail: {}".format(str(e)))
        logger.error("insert_yng_dim_sku failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 判断sku是否存在
def get_sku_count_by_unique_key(sku_name):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = "select count(*) AS total from dbo.yng_dim_sku_data where sku_name = N'{}'".format(sku_name)
        logger.debug("get_sku_count_by_unique_key SQL:{}".format(SQL))
        res = azuresql.execute_query_dict(SQL)
        total = res[0]['total'] if res else 0
        return total
    except Exception as e:
        logger.error("get_sku_count_by_unique_key failed detail: {}".format(str(e)))
        logger.error("get_sku_count_by_unique_key failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 根据id获取sku数据
def get_sku_by_id(id):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = "select TOP 1 * from dbo.yng_dim_sku_data where id = {}".format(id)
        logger.debug("get_sku_by_id SQL:{}".format(SQL))
        res = azuresql.execute_query_dict(SQL)
        if len(res) > 0:
            return res[0]
        return None
    except Exception as e:
        logger.error("get_sku_by_id failed detail: {}".format(str(e)))
        logger.error("get_sku_by_id failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 更新sku数据
def update_yng_dim_sku(obj):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = """
                    update dbo.yng_dim_sku_data set fz_std = ?, fz_top_limit = ?, fz_bottom_limit = ?, fh_std = ?, 
                                                    fh_top_limit = ?, fh_bottom_limit = ?, fs_std = ?, fs_top_limit = ?, 
                                                    fs_bottom_limit = ?, fc_std = ?, fc_top_limit = ?, fc_bottom_limit = ?, 
                                                    fk_std = ?, fk_top_limit = ?, fk_bottom_limit = ?, n1_roller_std = ?, 
                                                    n1_roller_top_limit = ?, n1_roller_bottom_limit = ?,  n2_roller_std = ?, 
                                                    n2_roller_top_limit= ?, n2_roller_bottom_limit= ?, n3_roller_std = ?,
                                                    n3_roller_top_limit = ?, n3_roller_bottom_limit = ?, forming_roller_std = ?,
                                                    forming_roller_top_limit = ?, forming_roller_bottom_limit = ?,
                                                    cross_cutter_speed_std = ?, cross_cutter_speed_top_limit = ?,
                                                    cross_cutter_speed_bottom_limit = ?, extruder_temperature_std = ?,
                                                    extruder_temperature_top_limit = ?, extruder_temperature_bottom_limit = ?,
                                                    update_by = ?, update_time = ?
                                        where id = ? 
              """
        logger.debug("update_yng_dim_sku SQL:{}".format(SQL))
        azuresql.execute_non_query_statement(SQL, obj)
    except Exception as e:
        logger.error("update_yng_dim_sku failed detail: {}".format(str(e)))
        logger.error("update_yng_dim_sku failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 删除sku数据
def delete_yng_dim_sku_by_id(id):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = "delete from dbo.yng_dim_sku_data where id = {} ".format(id)
        logger.debug("delete_yng_dim_sku_by_id SQL:{}".format(SQL))
        azuresql.execute_non_query(SQL)
    except Exception as e:
        logger.error("delete_yng_dim_sku_by_id failed detail: {}".format(str(e)))
        logger.error("delete_yng_dim_sku_by_id failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 分页查询sku数据
def get_sku_page_list(pageNum, pageSize):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL1 = "select COUNT(*) AS total from dbo.yng_dim_sku_data "
        resCount = azuresql.execute_query_dict(SQL1)
        total = resCount[0]['total'] if resCount else 0

        SQL2 = "select * from dbo.yng_dim_sku_data"
        SORT = " order by id"
        Paginitor = """ OFFSET ({}-1)*{} ROWS FETCH NEXT {} ROWS ONLY """.format(pageNum, pageSize, pageSize)
        SQL2 = SQL2 + SORT + Paginitor
        logger.debug("get_sku_page_list SQL:{}".format(SQL2))
        res = azuresql.execute_query_dict(SQL2)
        return total, res
    except Exception as e:
        logger.error("get_sku_page_list failed detail: {}".format(str(e)))
        logger.error("get_sku_page_list failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 查询需要导出的sku数据
def get_export_sku_list(alias):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SORT = " order by id"
        SQL = """
                select                     
                        sku_name          AS '{}',
                        fz_std            AS '{}',
                        fz_top_limit      AS '{}',
                        fz_bottom_limit   AS '{}',
                        fh_std            AS '{}',
                        fh_top_limit      AS '{}',
                        fh_bottom_limit   AS '{}',
                        fs_std            AS '{}',
                        fs_top_limit      AS '{}',
                        fs_bottom_limit   AS '{}',
                        fc_std            AS '{}',
                        fc_top_limit      AS '{}',
                        fc_bottom_limit   AS '{}',
                        fk_std            AS '{}',
                        fk_top_limit      AS '{}',
                        fk_bottom_limit   AS '{}',
                        n1_roller_std     AS '{}',
                        n1_roller_top_limit     AS '{}',
                        n1_roller_bottom_limit  AS '{}',
                        n2_roller_std           AS '{}',
                        n2_roller_top_limit     AS '{}',
                        n2_roller_bottom_limit  AS '{}',
                        n3_roller_std           AS '{}',
                        n3_roller_top_limit     AS '{}',
                        n3_roller_bottom_limit  AS '{}',
                        forming_roller_std      AS '{}',
                        forming_roller_top_limit AS '{}',
                        forming_roller_bottom_limit AS '{}',
                        cross_cutter_speed_std      AS '{}',
                        cross_cutter_speed_top_limit    AS '{}',
                        cross_cutter_speed_bottom_limit AS '{}',
                        extruder_temperature_std        AS '{}',
                        extruder_temperature_top_limit  AS '{}',
                        extruder_temperature_bottom_limit AS '{}'
                    from dbo.yng_dim_sku_data 
               """
        SQL = SQL.format(alias[0], alias[1], alias[2], alias[3], alias[4], alias[5], alias[6], alias[7],
                         alias[8], alias[9], alias[10], alias[11], alias[12], alias[13], alias[14], alias[15]
                         , alias[16], alias[17], alias[18], alias[19], alias[20], alias[21], alias[22], alias[23]
                         , alias[24], alias[25], alias[26], alias[27], alias[28], alias[29], alias[30], alias[31]
                         , alias[32], alias[33]) + SORT
        logger.debug("get_export_sku_list SQL:{}".format(SQL))
        res = azuresql.execute_query_dict(SQL)
        return res
    except Exception as e:
        logger.error("get_export_sku_list failed detail: {}".format(str(e)))
        logger.error("get_export_sku_list failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 查询sku全量数据
def get_all_sku_list():
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = "select * from dbo.yng_dim_sku_data order by id "
        logger.debug("get_all_sku_list SQL:{}".format(SQL))
        res = azuresql.execute_query_dict(SQL)
        return res
    except Exception as e:
        logger.error("get_all_sku_list failed detail: {}".format(str(e)))
        logger.error("get_all_sku_list failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 根据sku查询sku信息
def get_single_data_by_sku_name(sku_name):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = "SELECT TOP 1 * FROM dbo.yng_dim_sku_data WHERE sku_name =N'{}' ORDER BY id desc".format(sku_name)
        logger.debug("get_single_data_by_sku_name SQL:{}".format(SQL))
        res = azuresql.execute_query_dict(SQL)
        if len(res) > 0:
            return res[0]
        return None
    except Exception as e:
        logger.error("get_single_data_by_sku_name failed detail: {}".format(str(e)))
        logger.error("get_single_data_by_sku_name failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


# 备份当前数据同步到log表一份
def insert_yng_dim_sku_log(operator, operatorTime):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = """
                    insert into dbo.yng_dim_sku_data_log (
                                                    sourceId,
                                                    sku_name,
                                                    fz_std,
                                                    fz_top_limit,
                                                    fz_bottom_limit,
                                                    fh_std,
                                                    fh_top_limit,
                                                    fh_bottom_limit,
                                                    fs_std,
                                                    fs_top_limit,
                                                    fs_bottom_limit,
                                                    fc_std,
                                                    fc_top_limit,
                                                    fc_bottom_limit,
                                                    fk_std,
                                                    fk_top_limit,
                                                    fk_bottom_limit,
                                                    n1_roller_std,
                                                    n1_roller_top_limit,
                                                    n1_roller_bottom_limit,
                                                    n2_roller_std,
                                                    n2_roller_top_limit,
                                                    n2_roller_bottom_limit,
                                                    n3_roller_std,
                                                    n3_roller_top_limit,
                                                    n3_roller_bottom_limit,
                                                    forming_roller_std,
                                                    forming_roller_top_limit,
                                                    forming_roller_bottom_limit,
                                                    cross_cutter_speed_std,
                                                    cross_cutter_speed_top_limit,
                                                    cross_cutter_speed_bottom_limit,
                                                    extruder_temperature_std,
                                                    extruder_temperature_top_limit,
                                                    extruder_temperature_bottom_limit,
                                                    create_by, 
                                                    update_by, 
                                                    create_time,
                                                    update_time,
                                                    operator,
                                                    operatorTime
                                                )  select 
                                                    id,
                                                    sku_name,
                                                    fz_std,
                                                    fz_top_limit,
                                                    fz_bottom_limit,
                                                    fh_std,
                                                    fh_top_limit,
                                                    fh_bottom_limit,
                                                    fs_std,
                                                    fs_top_limit,
                                                    fs_bottom_limit,
                                                    fc_std,
                                                    fc_top_limit,
                                                    fc_bottom_limit,
                                                    fk_std,
                                                    fk_top_limit,
                                                    fk_bottom_limit,
                                                    n1_roller_std,
                                                    n1_roller_top_limit,
                                                    n1_roller_bottom_limit,
                                                    n2_roller_std,
                                                    n2_roller_top_limit,
                                                    n2_roller_bottom_limit,
                                                    n3_roller_std,
                                                    n3_roller_top_limit,
                                                    n3_roller_bottom_limit,
                                                    forming_roller_std,
                                                    forming_roller_top_limit,
                                                    forming_roller_bottom_limit,
                                                    cross_cutter_speed_std,
                                                    cross_cutter_speed_top_limit,
                                                    cross_cutter_speed_bottom_limit,
                                                    extruder_temperature_std,
                                                    extruder_temperature_top_limit,
                                                    extruder_temperature_bottom_limit,
                                                    create_by, 
                                                    update_by, 
                                                    create_time,
                                                    update_time,
                                                    '{}',
                                                    '{}'
                                                    from dbo.yng_dim_sku_data""".format(operator, operatorTime)
        logger.debug("insert_yng_dim_sku_log SQL:{}".format(SQL))
        azuresql.execute_non_query(SQL)
    except Exception as e:
        logger.error("insert_yng_dim_sku_log failed detail: {}".format(str(e)))
        logger.error("insert_yng_dim_sku_log failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()