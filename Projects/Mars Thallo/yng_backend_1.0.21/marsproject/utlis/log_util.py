import logging
from logging.handlers import RotatingFileHandler
import os

my_log_level = os.getenv("MY_LOG_LEVEL")


def get_log(name=__name__):
    # 设置日志
    # 创建自定义的日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    # 创建日志处理器，可以选择不同的处理器来处理不同的日志级别
    # 这里使用控制台处理器和文件处理器作为示例
    console_handler = logging.StreamHandler()
    file_handler = RotatingFileHandler("marsproject/logs/app.log", maxBytes=1024 * 1024 * 10, backupCount=50, encoding="UTF-8")

    # 设置日志处理器的日志级别，这里分别设置控制台处理器和文件处理器的级别
    console_handler.setLevel(my_log_level if my_log_level else logging.INFO)
    file_handler.setLevel(my_log_level if my_log_level else logging.INFO)

    # 创建日志格式器，用于定义日志输出的格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [PID: %(process)d] - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 将处理器添加到日志记录器
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
