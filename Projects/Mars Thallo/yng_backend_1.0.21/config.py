

# 示例用法


"""
mssql+pyodbc://<username>:<password>@<server_name>.database.windows.net/<database_name>?driver=ODBC+Driver+17+for+SQL+Server

"""


class AzureDBPoolConfig:
    driver = None
    server = None
    database = None
    user = None
    password = None

    @classmethod
    def init(cls, config):
        cls.driver = config['PORTAL_DB_DRIVER']
        cls.server = config['PORTAL_DB_SERVER']
        cls.database = config['PORTAL_DB_DATABASE']
        cls.user = config['PORTAL_DB_USERNAME']
        cls.password = config['PORTAL_DB_PASSWORD']


class AzureDB2PoolConfig:
    driver2 = None
    server2 = None
    database2 = None
    user2 = None
    password2 = None

    @classmethod
    def init(cls, config):
        cls.driver2 = config['SPC_DB_DRIVER']
        cls.server2 = config['SPC_DB_SERVER']
        cls.database2 = config['SPC_DB_DATABASE']
        cls.user2 = config['SPC_DB_USERNAME']
        cls.password2 = config['SPC_DB_PASSWORD']


class Config:
    SECRET_KEY = None
    REDIS = None
    CALL_AML_URL = None
    WRITE_BACK_URL = None
    WRITE_BACK_AUTH_KEY = None
    BLOB_SOURCE_CONN_STR = None
    BLOB_SOURCE_CONTAINER_NAME = None

    @classmethod
    def init(cls, config):
        cls.SECRET_KEY = config['SECRET_KEY']
        cls.REDIS = {
            'host': config['REDIS_HOST'],
            'port': config['REDIS_PORT'],
            'db': config['REDIS_DB'],
            'decode_responses': config['REDIS_DECODE_RESPONSES'],
            'password': config['REDIS_PASSWORD']
        }
        cls.CALL_AML_URL = config['CALL_AML_URL']
        cls.WRITE_BACK_URL = config['WRITE_BACK_URL']
        cls.WRITE_BACK_AUTH_KEY = config['WRITE_BACK_AUTH_KEY']
        cls.BLOB_SOURCE_CONN_STR = config['BLOB_SOURCE_CONN_STR']
        cls.BLOB_SOURCE_CONTAINER_NAME = config['BLOB_SOURCE_CONTAINER_NAME']


class RabbitMQConfig:
    username = None
    password = None
    host = None
    port = None
    vhost = None
    queue_etl_msg_out = None
    queue_data_to_backend = None

    @classmethod
    def init(cls, config):
        cls.username = config['RABBITMQ_USERNAME']
        cls.password = config['RABBITMQ_PASSWORD']
        cls.host = config['RABBITMQ_HOST']
        cls.port = config['RABBITMQ_PORT']
        cls.vhost = config['RABBITMQ_VHOST']
        cls.queue_etl_msg_out = config['RABBITMQ_QUEUE_ETL_MSG_OUT']
        cls.queue_data_to_backend = config['RABBITMQ_QUEUE_DATA_TO_BACKEND']



