import pymssql
from dbutils.pooled_db import PooledDB


class SpcDBFactory:

    _db_pool = None

    # 初始化连接池
    @classmethod
    def init_pool(cls, config):
        if not cls._db_pool:
            cls._db_pool = PooledDB(
                creator=pymssql,  # 使用pymssql
                mincached=5,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
                maxcached=10,  # 链接池中最多闲置的链接，0和None不限制
                blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
                maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
                server=config.server2,
                port=config.port2,
                database=config.database2,
                user=config.user2,
                password=config.password2,
                # server='10.157.85.236',
                # port=1434,
                # database='spc-datadb',
                # user='spc_datauser',
                # password='Accenture@2024',
                charset='utf8'
            )

    # 有异常抛给上层
    @classmethod
    def create_conn(cls):
        if cls._db_pool is None:
            raise Exception("SPC Database connection pool is not initialized.")
        conn = cls._db_pool.connection()
        return conn
