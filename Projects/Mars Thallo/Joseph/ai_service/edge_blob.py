import string
import sys
import pytz
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, BlobClient
import io
import os
import configparser
import warnings


def read_csv_blob_to_dataframe(blob_name):
    """
    从Azure Blob存储中读取CSV文件并将其转换为Pandas DataFrame。

    参数:
    - connect_str: Azure Blob存储的连接字符串。
    - container_name: 包含CSV文件的容器名称。
    - blob_name: CSV文件的名称（包括扩展名）。

    返回:
    - DataFrame: 包含CSV文件数据的Pandas DataFrame。
    """

    config = configparser.ConfigParser()
    config_filename = 'settings.ini'
    config.read(config_filename, 'UTF-8')
    connect_str = config.get('blob', 'connect_str')
    container_name = config.get('blob', 'container_name_curateddata')

    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    # 检查Blob是否存在
    if blob_client.exists():
        blob_data = blob_client.download_blob().content_as_bytes()
        csv_data = blob_data.decode('utf-8')
        df = pd.read_csv(io.StringIO(csv_data))
        return df
    else:
        # 如果文件不存在，返回一个指定的空的DataFrame
        return pd.DataFrame()


def save_dataframe_to_csv_blob(blob_name, df, index=False):
    """
    将Pandas DataFrame保存为Azure Blob存储中的CSV文件。

    参数:
    - connect_str: Azure Blob存储的连接字符串。
    - container_name: 要保存CSV文件的容器名称。
    - blob_name: CSV文件的名称（包括扩展名）。
    - df: 要保存的Pandas DataFrame。
    - index: 是否将DataFrame的索引也写入CSV文件，默认为False。

    无返回值（但会创建或覆盖Blob存储中的文件）。
    """
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=index, encoding='utf-8')
    blob_client.upload_blob(csv_buffer.getvalue(), blob_type="BlockBlob", overwrite=True)
