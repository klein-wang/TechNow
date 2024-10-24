
from flask import Flask

from config import RabbitMQConfig
from marsproject.mq.consumer import RabbitMQConsumer, start_consumer
from marsproject.operation.service import receiveRealTimeData, recommended_value_job
from marsproject.utils.db.db2_factory import AzureDB2Factory
from marsproject.utils.db.db_factory import AzureDBFactory

from concurrent.futures import ThreadPoolExecutor
from marsproject.utils.redis_util import RedisUtils
import os
from marsproject.utils.log_util import get_log
import json
from marsproject.utils.constant_value import *
from marsproject.utils.scheduler_utils import SchedulerUtils

logger = get_log(__name__)


# 创建线程池执行器
executor = ThreadPoolExecutor(20)


def get_unique_id():
    unique_id_file = '/app/marsproject/unique_id'
    if os.path.exists(unique_id_file):
        with open(unique_id_file, 'r') as file:
            return file.read().strip()
    return None


# 根据cpu核数和gun配置,至少2核
def check_lock(key, init_flag, expire_time):
    timestamp = get_unique_id()
    logger.info(f"get_unique_id:{timestamp}")
    if timestamp is None:
        return False
    timestamp1 = RedisUtils.get_value(key)
    if timestamp1 is not None:
        timestamp1 = str(timestamp1, 'utf-8')
    if timestamp1 and timestamp1 != str(timestamp):
        RedisUtils.release_lock(key, timestamp1)
    if not init_flag and RedisUtils.set_lock(key, str(timestamp), expire_time):
        return True
    return False


def create_app():

    # 创建一个Flask实例
    app = Flask(__name__)
    # 在创建 Flask 应用时设置 strict_slashes 参数为 False
    app.url_map.strict_slashes = False

    # 2.根据环境变量MY_ENV判断加载不同环境再在不同配置文件
    if os.getenv("MY_ENV") == 'LOCAL':
        app.config.from_pyfile('../config_local.py')
    elif os.getenv("MY_ENV") == 'DEV':
        app.config.from_pyfile('../config_dev.py')
    elif os.getenv("MY_ENV") == 'TEST':
        app.config.from_pyfile('../config_test.py')
    elif os.getenv("MY_ENV") == 'PROD':
        app.config.from_pyfile('../config_prod.py')
    else:
        logger.error("MY_ENV no config, not init config.")

    from config import AzureDBPoolConfig, Config, AzureDB2PoolConfig

    # 3 初始化相关配置文件
    AzureDBPoolConfig.init(app.config)
    AzureDB2PoolConfig.init(app.config)
    Config.init(app.config)
    RabbitMQConfig.init(app.config)

    # 4. 初始化db连接池资源
    AzureDBFactory.init_pool(AzureDBPoolConfig)
    # 4. 初始化db2连接池资源
    AzureDB2Factory.init_pool(AzureDB2PoolConfig)

    # 5. 初始化redis客户端
    RedisUtils.init_clinet(Config.REDIS)
    # 获取当前进程id
    cur_pid = os.getpid()
    # 一个进程只初始化一次程序
    init_flag = False

    from marsproject.operation.task import exception_alert_job
    job_id = "yng_check_exception_job"

    # 本次运行初始化一次用于debug
    if os.getenv("MY_ENV") == 'LOCAL':
        executor.submit(start_consumer, {"username": RabbitMQConfig.username,
                                         "password": RabbitMQConfig.password,
                                         "host": RabbitMQConfig.host,
                                         "port": int(RabbitMQConfig.port),
                                         "vhost": RabbitMQConfig.vhost,
                                         "queue_name": RabbitMQConfig.queue_etl_msg_out
                                         }, recommended_value_job)
        executor.submit(start_consumer, {"username": RabbitMQConfig.username,
                                         "password": RabbitMQConfig.password,
                                         "host": RabbitMQConfig.host,
                                         "port": int(RabbitMQConfig.port),
                                         "vhost": RabbitMQConfig.vhost,
                                         "queue_name": RabbitMQConfig.queue_data_to_backend
                                         }, receiveRealTimeData)
        # 初始化定时任务
        SchedulerUtils.init_scheduler(Config.REDIS)
        if not SchedulerUtils.get_job(job_id):
            SchedulerUtils.add_job(func=exception_alert_job, trigger='interval', seconds=60, id=job_id, jobstore='redis', replace_existing=True)
            logger.info('add job: {}'.format(job_id))
    else:
        # 进程来争抢锁,获取锁的可以启动一个进程来启动定时任务
        if check_lock(RedisKey.YNG_CONSUMER_ETL_MSG_LOCK, init_flag, 120):
            init_flag = True
            executor.submit(start_consumer, {"username": RabbitMQConfig.username,
                                              "password": RabbitMQConfig.password,
                                              "host": RabbitMQConfig.host,
                                              "port": int(RabbitMQConfig.port),
                                              "vhost": RabbitMQConfig.vhost,
                                              "queue_name": RabbitMQConfig.queue_etl_msg_out
                                              }, recommended_value_job)
            logger.info(f"{RedisKey.YNG_CONSUMER_ETL_MSG_LOCK} cur pid:{cur_pid}抢到消费者锁")

        # 进程来争抢锁,获取锁的可以启动一个进程来启动定时任务
        if check_lock(RedisKey.YNG_CONSUMER_TIME_DATA_LOCK, init_flag, 120):
            init_flag = True
            executor.submit(start_consumer, {"username": RabbitMQConfig.username,
                                             "password": RabbitMQConfig.password,
                                             "host": RabbitMQConfig.host,
                                             "port": int(RabbitMQConfig.port),
                                             "vhost": RabbitMQConfig.vhost,
                                             "queue_name": RabbitMQConfig.queue_data_to_backend
                                             }, receiveRealTimeData)
            logger.info(f"{RedisKey.YNG_CONSUMER_TIME_DATA_LOCK} cur pid:{cur_pid}抢到消费者锁")

        # 进程来争抢锁,获取锁的可以启动一个进程来启动定时任务
        if check_lock(RedisKey.YNG_SCHEDULER_LOCK, init_flag, 120):
            init_flag = True
            # 初始化定时任务
            SchedulerUtils.init_scheduler(Config.REDIS)
            if not SchedulerUtils.get_job(job_id):
                SchedulerUtils.add_job(func=exception_alert_job, trigger='interval', seconds=60, id=job_id, jobstore='redis', replace_existing=True)
                logger.info('add job: {}'.format(job_id))
            logger.info(f"{RedisKey.YNG_SCHEDULER_LOCK} cur pid:{cur_pid}抢到定时任务锁")

    # 获取操作页面的蓝图对象
    from marsproject.operation import operation_bp
    # 注册蓝图
    app.register_blueprint(operation_bp)

    # 获取历史记录的蓝图对象
    from marsproject.recordlog import recordLog_bp
    # 注册蓝图
    app.register_blueprint(recordLog_bp)

    # 获取iam蓝图对象
    from marsproject.iam import user_bp
    # 注册蓝图
    app.register_blueprint(user_bp)

    # 获取sku配置蓝图对象
    from marsproject.dim_sku import sku_bp
    # 注册蓝图
    app.register_blueprint(sku_bp)

    return app

