import time
import redis
from marsproject.utils.log_util import get_log

logger = get_log(__name__)


class RedisUtils:

    _redis_client = None

    @classmethod
    def init_clinet(cls, REDIS):
        if not cls._redis_client:
            redis_pool = redis.ConnectionPool(**REDIS)
            cls._redis_client = redis.StrictRedis(connection_pool=redis_pool)

    # 获取 Redis 分布式锁
    @classmethod
    def acquire_lock(cls, lock_key, lock_value, acquire_timeout=30):
        end_time = time.time() + acquire_timeout
        while time.time() < end_time:
            if cls._redis_client.set(lock_key, lock_value, nx=True, ex=acquire_timeout):
                logger.debug("set {} locked!".format(lock_key))
                return True
            time.sleep(0.1)
        return False

    @classmethod
    def set_lock(cls, lock_key, lock_value, timeout=15):
        return cls._redis_client.set(lock_key, lock_value, nx=True, ex=timeout)

    # 释放 Redis 分布式锁
    @classmethod
    def release_lock(cls, lock_key, lock_value):
        del_script = """
           if redis.call('get', KEYS[1]) == ARGV[1] then
               return redis.call('del', KEYS[1])
           else
               return 0
           end
           """
        cls._redis_client.eval(del_script, 1, lock_key, lock_value)
        logger.debug("{} locked released!".format(lock_key))

    @classmethod
    def set_value(cls, key, value, timeout=10):
        return cls._redis_client.set(key, value, ex=timeout)

    @classmethod
    def get_value(cls, key):
        return cls._redis_client.get(key)

    @classmethod
    def delete_value(cls, key):
        return cls._redis_client.delete(key)

    @classmethod
    def set_value_no_ex(cls, key, value):
        return cls._redis_client.set(key, value)

