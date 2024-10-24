import json
import time

import pika
from marsproject.utils.log_util import get_log
logger = get_log(__name__)


class RabbitMQConsumer:

    def __init__(self, **args_in):

        self.username = args_in["username"]  # RabbitMQ用户名
        self.password = args_in["password"]  # RabbitMQ密码
        self.host = args_in["host"]  # RabbitMQ主机
        self.port = args_in["port"]  # RabbitMQ端口
        self.vhost = args_in["vhost"]
        self.queue_name = args_in["queue_name"]  # 队列名
        self.connection = None
        self.user_defined_func = None

    def set_user_defined_func(self, user_defined_func):
        self.user_defined_func = user_defined_func

    def connect(self):
        """作为接收端"""
        try:
            self.connectExt()
        except Exception as ex:
            logger.error("RabbitMQConsumer queueName:{} exception: {}".format(self.queue_name, ex))
            logger.info("sleep 5 second try connection start....")
            time.sleep(5)  # 等待 5 秒后再尝试重新连接
            self.connectExt()

    def connectExt(self):
        logger.info("RabbitMQConsumer init => queue_name: {}".format(self.queue_name))
        credentials = pika.PlainCredentials(self.username, self.password)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.host,
                                      port=self.port,
                                      virtual_host=self.vhost,
                                      credentials=credentials))
        channel = self.connection.channel()

        # 声明消息队列，如果不存在将创建；并设置成永久类型。
        channel.queue_declare(self.queue_name, durable=True)
        # 定义回调函数，当消息队列中有新的通知时调用callback函数
        channel.basic_consume(self.queue_name, on_message_callback=self.message_callback)
        channel.start_consuming()

    def message_callback(self, ch, method, properties, body):
        """回调函数：在新消息来的时候执行"""
        try:
            body_decode = body.decode()
            logger.debug("RabbitMQConsumer Received => {} -> {}".format(self.queue_name, body_decode))
            self.user_defined_func(json.loads(body_decode))
        except Exception as ex:
            logger.error("RabbitMQConsumer message_callback:{} exception: {}, msg: {}".format(self.queue_name, ex, body_decode))
        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)


def start_consumer(consumer_args, user_defined_func):
    rabbit_consumer = RabbitMQConsumer(**consumer_args)
    rabbit_consumer.set_user_defined_func(user_defined_func)
    rabbit_consumer.connect()

