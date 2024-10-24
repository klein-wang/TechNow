from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.pool import ThreadPoolExecutor as TP
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

from marsproject import RedisUtils
from marsproject.utils.log_util import get_log

logger = get_log(__name__)


class SchedulerUtils:

    _scheduler = None

    @classmethod
    def init_scheduler(cls, REDIS):
        if not cls._scheduler:
            # 初始化RedisJobStore
            jobstore = RedisJobStore(**REDIS)

            cls.scheduler = BackgroundScheduler(jobstores={'redis': jobstore}, executors={'default': TP(10)})

            cls.scheduler.add_listener(cls._job_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

            cls.scheduler.start()

    # 创建定时任务调度器实例作为单例
    # 初始化 Redis 客户端
    @classmethod
    def _job_listener(cls, event):
        if event.exception:
            logger.error("定时任务 {} 执行出错：{}".format(event.job_id, event.exception))
        else:
            logger.debug("定时任务 {} 成功执行".format(event.job_id))

    @classmethod
    def add_job(cls, **kwargs):
        cls.scheduler.add_job(**kwargs)

    @classmethod
    def get_job(cls, jobId):
        return cls.scheduler.get_job(jobId)


