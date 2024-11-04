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

    config = configparser.ConfigParser()
    config_filename = 'settings.ini'
    config.read(config_filename, 'UTF-8')
    connect_str = config.get('blob', 'connect_str')
    container_name = config.get('blob', 'container_name_curateddata')

    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=index, encoding='utf-8')
    blob_client.upload_blob(csv_buffer.getvalue(), blob_type="BlockBlob", overwrite=True)



class AzureBlobStorage:

    def __init__(self, connection_string):
        """
        创建 Azure Blob 存储客户端
        """
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    def upload_blob(self, container_name, blob_name, data):
        """
        上传数据到 Blob
        """
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.upload_blob(data, overwrite=True)

    def download_blob(self, container_name, blob_name):
        """
        下载 Blob 中的数据
        """
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        data = blob_client.download_blob().readall()
        return data

    def list_blobs(self, container_name):
        """
        列出 Blob 容器中的所有 Blob
        """
        container_client = self.blob_service_client.get_container_client(container_name)
        blobs = []
        try:
            for blob in container_client.list_blobs():
                blobs.append(blob.name)
        except Exception as e:
            print("error", e)
        return blobs

    def list_blobs(self, container_name, blob_name):
        """
        列出 Blob 容器中的所有 Blob
        """
        container_client = self.blob_service_client.get_container_client(container_name)
        blobs = []
        try:
            for blob in container_client.list_blobs(name_starts_with=blob_name):
                blobs.append(blob.name)
        except Exception as e:
            print("error", e)
        return blobs

    def list_container(self):
        container_list = []
        for container in self.blob_service_client.list_containers():
            container_list.append(container.name)
            return container_list

    def create_container(self, container_name):
        """
        创建 Blob 容器
        """
        container_client = self.blob_service_client.create_container(container_name)
        return container_client

    def delete_container(self, container_name):
        """
        删除 Blob 容器
        """
        container_client = self.blob_service_client.get_container_client(container_name)
        container_client.delete_container()

    def delete_blob(self, container_name, blob_name):
        """
        删除 Blob
        """
        blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        blob_client.delete_blob()


class BlobConfig:

    source_conn_str = "DefaultEndpointsProtocol=https;AccountName=devce2iotcoreadls01;AccountKey=r6kwbfAFw8XGYrzn4HprzHmeF9F62veBFy4PPN0rEiWiMGEBLhIEd2k7iiTrJLyoXREouMGN1HED+AStW05bwA==;EndpointSuffix=core.chinacloudapi.cn"
    source_container_name = "devce2iotcoreadls01"

    # target_conn_str = "DefaultEndpointsProtocol=https;AccountName=devce2iotcoreadls02;AccountKey=1ni1XJ3eZpXLMvLjtPcz8x489HajofT1USgdFeGNuzaS2XXCBZiS8tyQu5zisMpAobhVA4LW5oTv+ASt5ufs2A==;EndpointSuffix=core.chinacloudapi.cn"
    # target_container_name = "devce2iotcoreadls02"

    target_conn_str = "DefaultEndpointsProtocol=https;AccountName=dlsmwcoredevcn301;AccountKey=uPpb1b6CMNLLLF0jaAsLmtRM427nfDhLXaMtFP2bSzsja8ch1Qp5+jHXD9KOc3+tWsYgXbsBwBZj+AStm69Kfw==;EndpointSuffix=core.chinacloudapi.cn"
    target_container_name = "yngblob"

