import json
import os
import string
import logging
import sys
import time
import pytz
from datetime import datetime
import pika
from concurrent.futures import wait, ALL_COMPLETED
from concurrent.futures.thread import ThreadPoolExecutor

import etl_main_new

RUN_ENV_DEV = "dev"
RUN_ENV_PROD = "prod"
RUN_ENV_DEV_LOCAL_CC = "dev_local_cc"

# dev / prod / dev_local_cc
curr_env = os.getenv("RUN_ENV")
print(f"get curr_env from environment = {curr_env}")
if not curr_env:
    curr_env = RUN_ENV_DEV

# 创建线程池执行器
executor = ThreadPoolExecutor(20)

# 设置日志
logger = logging.getLogger(__name__)
# 创建自定义的日志记录器
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler(stream=sys.stdout)  # output to standard output
console_handler.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s")
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


class RabbitMQProducer:

    def __init__(self, **args_in):

        self.username = args_in["username"]  # RabbitMQ用户名
        self.password = args_in["password"]  # RabbitMQ密码
        self.host = args_in["host"]  # RabbitMQ主机
        self.port = args_in["port"]  # RabbitMQ端口
        self.vhost = args_in["vhost"]
        self.queue_input = args_in["queue_input"]  # RabbitMQ指令队列
        self.queue_output = args_in["queue_output"]  # RabbitMQ指令计算结果反馈队列
        self.connection = None
        self.channel = None
        self.user_defined_func = None
        self.connect()
        self.index = 0

    def set_user_defined_func(self, user_defined_func):
        self.user_defined_func = user_defined_func

    def close_connection(self):
        if self.connection and self.connection.is_open:
            logger.info("RabbitMQProducer shutdown ")
            self.connection.close()

    def connect(self):
        """作为发送端"""
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host,
                                        port=self.port,
                                        virtual_host=self.vhost,
                                        heartbeat=0,
                                        credentials=credentials))

            self.channel = self.connection.channel()
            # 声明消息队列，如果不存在将创建；并设置成永久类型。
            self.channel.queue_declare(self.queue_output, durable=True)
        except Exception as ex:
            logger.error("RabbitMQProducer exception: {}".format(ex))
            self.close_connection()
            time.sleep(30)
            self.connect()

    # 定义回调函数，当消息队列中有新的通知时调用callback函数
    def message_callback(self, args) -> bool:
        try:
            result_data = self.user_defined_func(args["message"])
            # data = {"code": 200, "message": result_data}
            jsonify = json.dumps(result_data)
            # 接下来对计算的结果，反馈到MQ消息队列中
            self.channel.basic_publish(exchange='',
                                       routing_key=self.queue_output,
                                       body=jsonify,
                                       properties=pika.BasicProperties(delivery_mode=2))
            logger.info("RabbitMQProducer Sent => {} -> {}".format(self.queue_output, jsonify))
            return True
        except Exception as ex:
            logger.error("RabbitMQProducer exception: {}".format(ex))
            #self.close_connection()
            #time.sleep(30)
            #self.connect()
            #raise ex


class RabbitMQConsumer:

    def __init__(self, **args_in):

        self.username = args_in["username"]  # RabbitMQ用户名
        self.password = args_in["password"]  # RabbitMQ密码
        self.host = args_in["host"]  # RabbitMQ主机
        self.port = args_in["port"]  # RabbitMQ端口
        self.vhost = args_in["vhost"]
        self.queue_input = args_in["queue_input"]  # RabbitMQ指令队列
        self.queue_output = args_in["queue_output"]  # RabbitMQ指令计算结果反馈队列
        self.connection = None
        self.user_defined_func = None

    def close_connection(self):
        if self.connection and self.connection.is_open:
            logger.info("RabbitMQConsumer shutdown ")
            self.connection.close()

    def set_user_defined_func(self, user_defined_func):
        self.user_defined_func = user_defined_func

    def connect(self):
        """作为接收端"""
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host,
                                          port=self.port,
                                          virtual_host=self.vhost,
                                          heartbeat=0,
                                          credentials=credentials))
            channel = self.connection.channel()

            # 声明消息队列，如果不存在将创建；并设置成永久类型。
            channel.queue_declare(self.queue_input, durable=True)
            # 定义回调函数，当消息队列中有新的通知时调用callback函数
            channel.basic_consume(self.queue_input, on_message_callback=self.message_callback)
            channel.start_consuming()
        except Exception as ex:
            logger.error("RabbitMQConsumer exception: {}".format(ex))
            self.close_connection()
            time.sleep(30)
            self.connect()
            #raise ex

    def message_callback(self, ch, method, properties, body):
        """回调函数：在新消息来的时候执行"""
        try:
            body_decode = body.decode()
            logger.info("RabbitMQConsumer Received => {} -> {}".format(self.queue_input, body_decode))
            # 将任务提交到进程池里执行，user_defined_func是用户定义的函数，args_in 入参
            task = [executor.submit(self.user_defined_func, {"index": 1, "message": body_decode})]
            # self.user_defined_func()
            wait(task, return_when=ALL_COMPLETED)
            if task[0].result():
                ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as ex:
            logger.error("RabbitMQConsumer exception: {}".format(ex))
            #self.close_connection()
            #time.sleep(30)
            #self.connect()

def execute_etl(input_jsonify: string) -> string:
    logger.info("execute_etl get input jsonify => {}".format(input_jsonify))
    result_data = etl_main_new.do_etl_process(input_jsonify)
    return json.dumps(result_data)


def main():
    username = os.getenv("RABBIT_USER", "guest")
    password = os.getenv("RABBIT_PASS", "guest")
    host = os.getenv("RABBIT_HOST", "10.157.85.237")
    port = os.getenv("RABBIT_PORT", "6672")
    vhost = os.getenv("RABBIT_VHOST", "/")
    qname_in = os.getenv("RABBIT_QNAME_IN", "etl-msg-in")
    qname_out = os.getenv("RABBIT_QNAME_OUT", "etl-msg-out")

    args = {
        "username": username,
        "password": password,
        "host": host,
        "port": int(port),
        "vhost": vhost,
        "queue_input": qname_in,
        "queue_output": qname_out
    }
    # 开启线程池，并且定义线程池里线程总数为10个
    with ThreadPoolExecutor(max_workers=3) as executor:
        rabbit_producer = RabbitMQProducer(**args)
        rabbit_consumer = RabbitMQConsumer(**args)
        rabbit_producer.set_user_defined_func(execute_etl)
        rabbit_consumer.set_user_defined_func(rabbit_producer.message_callback)
        rabbit_consumer.connect()
    logger.info("completed!")


if __name__ == "__main__":
    main()
