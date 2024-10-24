from marsproject.utils.db.db_factory import AzureDBFactory as azure_db_factory
from marsproject.utils.db.azure_utils import DBConnector
import traceback
from marsproject.utils.time_utils import get_cst_time_formatter
from marsproject.utils.log_util import get_log

logger = get_log(__name__)


def get_user_pwd_by_id(id):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = """
            select 
                top(1) 
                user_name,
                pwd
            from dbo.yng_t_user 
            where id={}
        """.format(id)
        res = azuresql.execute_query_dict(SQL)
        if len(res) > 0:
            return res[0]
        return None
    except Exception as e:
        logger.error("get_user_pwd_by_id failed detail: {}".format(str(e)))
        logger.error("get_user_pwd_by_id failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def update_user_pwd_by_id(id, new_pwd):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        cur_time = get_cst_time_formatter('%Y-%m-%d %H:%M:%S')
        SQL = """
            update dbo.yng_t_user set pwd='{}', update_time='{}' where id={}
        """.format(new_pwd, cur_time, id)
        azuresql.execute_non_query(SQL)
    except Exception as e:
        logger.error("update_user_pwd_by_id failed detail: {}".format(str(e)))
        logger.error("update_user_pwd_by_id failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def get_user_by_name_or_user_number(name):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = "select top(1) * from dbo.yng_t_user where activate=1 and user_name= N'{}'".format(name)
        res = azuresql.execute_query_dict(SQL)
        if len(res) > 0:
            return res[0]
        return None
    except Exception as e:
        logger.error("get_user_by_name_or_user_number failed detail: {}".format(str(e)))
        logger.error("get_user_by_name_or_user_number failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def get_user_by_name(name):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = "select top(1) * from dbo.yng_t_user where activate=1 and user_name= N'{}'".format(name)
        res = azuresql.execute_query_dict(SQL)
        if len(res) > 0:
            return res[0]
        return None
    except Exception as e:
        logger.error("get_user_by_name failed detail: {}".format(str(e)))
        logger.error("get_user_by_name failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def get_user_by_user_number(user_no):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = "select top(1) * from dbo.yng_t_user where activate=1 and user_no= '{}'".format(user_no)
        res = azuresql.execute_query_dict(SQL)
        if len(res) > 0:
            return res[0]
        return None
    except Exception as e:
        logger.error("get_user_by_user_number failed detail: {}".format(str(e)))
        logger.error("get_user_by_user_number failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def get_user_by_id(id):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = """
            select 
                top(1) 
                    id
                  ,user_no
                  ,user_name
                  ,name
                  ,email
                  ,department
                  ,phone
                  ,create_time
                  ,update_time 
            from dbo.yng_t_user 
            where id={}
        """.format(id)
        res = azuresql.execute_query_dict(SQL)
        if len(res) > 0:
            return res[0]
        return None
    except Exception as e:
        logger.error("get_user_by_id failed detail: {}".format(str(e)))
        logger.error("get_user_by_id failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def get_roles_by_user_id(id):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = """
            select 
                c.role_name
            from dbo.yng_t_user a 
            left join dbo.yng_t_user_role b
            on a.id = b.uid 
            left join dbo.yng_t_role c 
            on b.rid = c.id
            where a.id = {}
        """.format(id)
        res = azuresql.execute_query_dict(SQL)
        if len(res) > 0:
            return [r['role_name'] for r in res]
        return []
    except Exception as e:
        logger.error("get_roles_by_user_id failed detail: {}".format(str(e)))
        logger.error("get_roles_by_user_id failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def get_permissions_by_user_id(id):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        MENU_SQL = """
            select 
                distinct 
                e.id as id ,
                e.name as name,
                e.parent_id as parent_id,
                e.icon as icon,
                e.pre as pre,
                e.path as path,
                e.type as type
            from dbo.yng_t_user a 
            LEFT JOIN dbo.yng_t_user_role b on a.id = b.uid
            LEFT JOIN dbo.yng_t_role c ON b.rid = c.id 
            LEFT JOIN dbo.yng_t_role_permission d on c.id = d.rid
            LEFT JOIN dbo.yng_t_permission e on d.pid = e.id
            WHERE a.id = {}
            and e.type=0 -- 0:菜单 1：按钮
        """.format(id)
        menu_res = azuresql.execute_query_dict(MENU_SQL)

        BUTTION_SQL = """
            select 
                distinct 
                e.id as id ,
                e.name as name,
                e.parent_id as parent_id,
                e.icon as icon,
                e.pre as pre,
                e.path as path,
                e.type as type
            from dbo.yng_t_user a 
            LEFT JOIN dbo.yng_t_user_role b on a.id = b.uid
            LEFT JOIN dbo.yng_t_role c ON b.rid = c.id 
            LEFT JOIN dbo.yng_t_role_permission d on c.id = d.rid
            LEFT JOIN dbo.yng_t_permission e on d.pid = e.id
            WHERE a.id = {}
            and e.type=1 -- 0:菜单 1：按钮
               """.format(id)
        button_res = azuresql.execute_query_dict(BUTTION_SQL)
        button_res = [r['name'] for r in button_res] if len(button_res) > 0 else []
        return menu_res, button_res
    except Exception as e:
        logger.error("get_permissions_by_user_id failed detail: {}".format(str(e)))
        logger.error("get_permissions_by_user_id failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def update_user_by_id(id, user):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        cur_time = get_cst_time_formatter('%Y-%m-%d %H:%M:%S')
        SQL = """
            update dbo.yng_t_user set user_name=N'{}',name= N'{}' ,phone='{}',email='{}',department=N'{}', update_time='{}' where id={}
        """.format(user['user_name'], user['name'], user['phone'], user['email'], user['department'], cur_time, id)
        azuresql.execute_non_query(SQL)
    except Exception as e:
        logger.error("update_user_by_id failed detail: {}".format(str(e)))
        logger.error("update_user_by_id failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def delete_user_by_id(id):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = """delete dbo.yng_t_user where id={}""".format(id)
        azuresql.execute_non_query(SQL)
    except Exception as e:
        logger.error("delete_user_by_id failed detail: {}".format(str(e)))
        logger.error("delete_user_by_id failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def delete_user_roles_by_uid(uid):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = """delete dbo.yng_t_user_role where uid={}""".format(uid)
        azuresql.execute_non_query(SQL)
    except Exception as e:
        logger.error("delete_user_roles_by_uid failed detail: {}".format(str(e)))
        logger.error("delete_user_roles_by_uid failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def init_password_by_id(id, pwd):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        cur_time = get_cst_time_formatter('%Y-%m-%d %H:%M:%S')
        SQL = "update dbo.yng_t_user set pwd='{}' , update_time='{}' where id={}".format(pwd, cur_time, id)
        azuresql.execute_non_query(SQL)
    except Exception as e:
        logger.error("init_password_by_id failed detail: {}".format(str(e)))
        logger.error("init_password_by_id failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def create_user(user_name, name, pwd, email, department, phone):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        cur_time = get_cst_time_formatter('%Y-%m-%d %H:%M:%S')
        SQL = """INSERT INTO dbo.yng_t_user(user_name,
                                            name,
                                            pwd,
                                            email,
                                            department,
                                            phone,
                                            create_time,
                                            update_time
                                            ) OUTPUT INSERTED.ID VALUES (
                                            N'{}',
                                            N'{}',
                                            '{}',
                                            '{}',
                                            N'{}',
                                            '{}',
                                            '{}',
                                            '{}') """.format(user_name, name, pwd, email, department, phone, cur_time, cur_time)
        res = azuresql.execute_save_result_lastId(SQL)
        return res
    except Exception as e:
        logger.error("create_user failed detail: {}".format(str(e)))
        logger.error("create_user failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def create_user_role(uid, rids):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        cur_time = get_cst_time_formatter('%Y-%m-%d %H:%M:%S')
        SQL = "insert into dbo.yng_t_user_role(uid,rid, create_time, update_time)  values " + ','.join(
                ["('{}','{}','{}','{}')".format(uid, rid, cur_time, cur_time) for rid in rids])
        azuresql.execute_non_query(SQL)
    except Exception as e:
        logger.error("create_user_role failed detail: {}".format(str(e)))
        logger.error("create_user_role failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def get_user_list_with_like(name, pnum, psize):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = """select    id
                          ,user_no
                          ,user_name
                          ,name
                          ,email
                          ,department
                          ,phone
                          ,create_time
                          ,update_time 
                from dbo.yng_t_user where activate=1 and user_name like N'%{}%' order by id desc """.format(name)
        res1 = azuresql.execute_query_dict(SQL)
        total = len(res1)
        Paginitor = """
              OFFSET ({}-1)*{} ROWS -- 计算偏移量，获取指定页数的起始行
              FETCH NEXT {} ROWS ONLY 
        """.format(pnum, psize, psize)
        res = azuresql.execute_query_dict(SQL + Paginitor)

        return total, res
    except Exception as e:
        logger.error("get_user_list_with_like failed detail: {}".format(str(e)))
        logger.error("get_user_list_with_like failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def get_user_list_all(pnum, psize):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = """
           select 
                   id
                  ,user_no
                  ,user_name
                  ,name
                  ,email
                  ,department
                  ,phone
                  ,create_time
                  ,update_time 
           from dbo.yng_t_user 
           where activate=1
           order by id desc 
        """
        res1 = azuresql.execute_query_dict(SQL)
        total = len(res1)

        Paginitor = """
           OFFSET ({}-1)*{} ROWS -- 计算偏移量，获取指定页数的起始行
           FETCH NEXT {} ROWS ONLY 
        """.format(pnum, psize, psize)
        res = azuresql.execute_query_dict(SQL + Paginitor)
        return total, res
    except Exception as e:
        logger.error("get_user_list_all failed detail: {}".format(str(e)))
        logger.error("get_user_list_all failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def get_roles_for_users(user_list):
    if len(user_list) < 1:
        return 0
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = """
          select 
              c.role_name,
              c.id
          from dbo.yng_t_user a 
          left join dbo.yng_t_user_role b on a.id = b.uid 
          left join dbo.yng_t_role c on b.rid = c.id
          where a.id ={}
          """
        for user in user_list:
            res = azuresql.execute_query_dict(SQL.format(user['id']))
            user['roles'] = [r['id'] for r in res]
    except Exception as e:
        logger.error("get_roles_for_users failed detail: {}".format(str(e)))
        logger.error("get_roles_for_users failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def get_permission_list_all():
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL="""
            select 
                id as id ,
                name as name,
                parent_id as parent_id,
                icon as icon,
                pre as pre,
                path as path,
                type as type
            from dbo.yng_t_permission
        """
        res = azuresql.execute_query_dict(SQL)
        return res
    except Exception as e:
        logger.error("get_permission_list_all failed detail: {}".format(str(e)))
        logger.error("get_permission_list_all failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def get_roles_list_all():
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL="""select *from dbo.yng_t_role"""
        res = azuresql.execute_query_dict(SQL)
        return res
    except Exception as e:
        logger.error("get_roles_list_all failed detail: {}".format(str(e)))
        logger.error("get_roles_list_all failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def create_role(role_name, info, permissions):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        cur_time = get_cst_time_formatter('%Y-%m-%d %H:%M:%S')
        ROLE_SQL = """insert into dbo.yng_t_role(role_name,info,create_time,update_time) values (N'{}',N'{}','{}','{}')""".format(role_name, info, cur_time, cur_time)
        azuresql.execute_non_query(ROLE_SQL)
        ROLE_ID_SQL = """select top(1) id from dbo.yng_t_role where role_name=N'{}'""".format(role_name)
        res = azuresql.execute_query_dict(ROLE_ID_SQL)
        role_id = res[0]['id']
        PERMISSION_SQL = "insert into dbo.yng_t_role_permission(rid,pid, create_time, update_time)  values " + ','.join(
            ["('{}','{}','{}','{}')".format(role_id, pid, cur_time, cur_time) for pid in permissions])
        azuresql.execute_non_query(PERMISSION_SQL)
    except Exception as e:
        logger.error("create_role failed detail: {}".format(str(e)))
        logger.error("create_role failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def get_user_count_by_name(name, id):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = "select count(*) as total from dbo.yng_t_user where activate=1 and user_name= N'{}' and id !={} ".format(name, id)
        res = azuresql.execute_query_dict(SQL)
        total = res[0]['total'] if res else 0
        return total
    except Exception as e:
        logger.error("get_user_count_by_name failed detail: {}".format(str(e)))
        logger.error("get_user_count_by_name failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def get_user_count_by_user_number(user_no, id):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = "select count(*) as total from dbo.yng_t_user where activate=1 and user_no= '{}' and id !={} ".format(user_no, id)
        res = azuresql.execute_query_dict(SQL)
        total = res[0]['total'] if res else 0
        return total
    except Exception as e:
        logger.error("get_user_count_by_user_number failed detail: {}".format(str(e)))
        logger.error("get_user_count_by_user_number failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def get_single_role_by_id(id):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL="""select TOP(1) * from dbo.yng_t_role where id = {}""".format(id)
        res = azuresql.execute_query_dict(SQL)
        if len(res) > 0:
            return res[0]
        return None
    except Exception as e:
        logger.error("get_single_role_by_id failed detail: {}".format(str(e)))
        logger.error("get_single_role_by_id failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def delete_user_roles_by_rid(rid):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = """delete dbo.yng_t_user_role where rid={}""".format(rid)
        azuresql.execute_non_query(SQL)
    except Exception as e:
        logger.error("delete_user_roles_by_rid failed detail: {}".format(str(e)))
        logger.error("delete_user_roles_by_rid failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def delete_roles_by_id(id):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = """delete dbo.yng_t_role where id={}""".format(id)
        azuresql.execute_non_query(SQL)
    except Exception as e:
        logger.error("delete_roles_by_id failed detail: {}".format(str(e)))
        logger.error("delete_roles_by_id failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def update_role_by_id(id, role_name, info):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        cur_time = get_cst_time_formatter('%Y-%m-%d %H:%M:%S')
        SQL = """
            update dbo.yng_t_role set role_name=N'{}',info=N'{}', update_time='{}' where id={}""".format(role_name, info, cur_time, id)
        azuresql.execute_non_query(SQL)
    except Exception as e:
        logger.error("update_role_by_id failed detail: {}".format(str(e)))
        logger.error("update_role_by_id failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def delete_role_premission_by_rid(rid):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = """delete dbo.yng_t_role_permission where rid={}""".format(rid)
        azuresql.execute_non_query(SQL)
    except Exception as e:
        logger.error("delete_role_premission_by_rid failed detail: {}".format(str(e)))
        logger.error("delete_role_premission_by_rid failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def create_role_premission(role_id, permissions):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        cur_time = get_cst_time_formatter('%Y-%m-%d %H:%M:%S')
        PERMISSION_SQL = "insert into dbo.yng_t_role_permission(rid,pid, create_time, update_time)  values " + ','.join(
            ["('{}','{}','{}','{}')".format(role_id, pid, cur_time, cur_time) for pid in permissions])
        azuresql.execute_non_query(PERMISSION_SQL)
    except Exception as e:
        logger.error("create_role_premission failed detail: {}".format(str(e)))
        logger.error("create_role_premission failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def get_roles_by_userId(ids):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = """
          select 
              c.role_name,
              c.id as rid,
              a.id as uid
          from dbo.yng_t_user a 
          left join dbo.yng_t_user_role b on a.id = b.uid 
          left join dbo.yng_t_role c on b.rid = c.id
          where a.id in ({})
          """.format(ids)
        res = azuresql.execute_query_dict(SQL)
        return res
    except Exception as e:
        logger.error("get_roles_by_userId failed detail: {}".format(str(e)))
        logger.error("get_roles_by_userId failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def get_roles_by_single_userId(id):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = """
          select 
              c.role_name,
              c.id as rid,
              a.id as uid
          from dbo.yng_t_user a 
          left join dbo.yng_t_user_role b on a.id = b.uid 
          left join dbo.yng_t_role c on b.rid = c.id
          where a.id = {}
          """.format(id)
        res = azuresql.execute_query_dict(SQL)
        return res
    except Exception as e:
        logger.error("get_roles_by_single_userId failed detail: {}".format(str(e)))
        logger.error("get_roles_by_single_userId failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def create_role_ext(role_name, info):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        cur_time = get_cst_time_formatter('%Y-%m-%d %H:%M:%S')
        ROLE_SQL = """insert into dbo.yng_t_role(role_name,
                                                info,
                                                create_time,
                                                update_time) OUTPUT INSERTED.ID values (N'{}',N'{}','{}','{}')""".format(role_name, info, cur_time, cur_time)
        res = azuresql.execute_save_result_lastId(ROLE_SQL)
        return res
    except Exception as e:
        logger.error("create_role failed detail: {}".format(str(e)))
        logger.error("create_role failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def get_role_by_name(role_name):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = "select top(1) * from dbo.yng_t_role where role_name= N'{}'".format(role_name)
        res = azuresql.execute_query_dict(SQL)
        if len(res) > 0:
            return res[0]
        return None
    except Exception as e:
        logger.error("get_role_by_name failed detail: {}".format(str(e)))
        logger.error("get_role_by_name failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()


def get_role_count_by_name(role_name, id):
    conn = azure_db_factory.create_conn()
    azuresql = DBConnector(conn)
    try:
        SQL = "select count(*) as total from dbo.yng_t_role where role_name= N'{}' and id !={} ".format(role_name, id)
        res = azuresql.execute_query_dict(SQL)
        total = res[0]['total'] if res else 0
        return total
    except Exception as e:
        logger.error("get_role_count_by_name failed detail: {}".format(str(e)))
        logger.error("get_role_count_by_name failed detail: {}".format(traceback.format_exc()))
    finally:
        azuresql.close()