from marsproject import get_log, RedisUtils, RedisKey
from marsproject.recordlog.service import unusual_service_condition_1, unusual_service_condition_4
logger = get_log(__name__)


# 异常工况定时任务 1分钟执行一次
def exception_alert_job():
    logger.info("===========exception_alert_job start===========")
    sys_st = RedisUtils.get_value(RedisKey.SYSTEM_STATUS_KEY)
    if sys_st is not None and '1' == str(sys_st, 'utf-8'):
        res1 = unusual_service_condition_1()
        logger.info("exception_alert_job exception1 result:{}".format(res1))
        res4 = unusual_service_condition_4()
        logger.info("exception_alert_job exception4 result:{}".format(res4))
    else:
        logger.info("system status is stop, exception_alert_job no calc")
    logger.info("===========exception_alert_job end===========")
