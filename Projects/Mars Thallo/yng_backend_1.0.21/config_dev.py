

# 基础业务库
PORTAL_DB_DRIVER = '{ODBC Driver 18 for SQL Server}'
PORTAL_DB_SERVER = 'tcp:10.157.85.236,1434'
PORTAL_DB_DATABASE = 'dev-portaldb'
PORTAL_DB_USERNAME = 'portaluser'
PORTAL_DB_PASSWORD = 'Accenture@2024'

# SPC数据库 这个在单独配置出来一个数据源,后面spc的库要拆出来
SPC_DB_DRIVER = '{ODBC Driver 18 for SQL Server}'
SPC_DB_SERVER = 'tcp:10.157.85.236,1434'
SPC_DB_DATABASE = 'spc-datadb'
SPC_DB_USERNAME = 'spc_datauser'
SPC_DB_PASSWORD = 'Accenture@2024'


# jwt 加密秘钥
SECRET_KEY = "05db643647d6d1f5b5caa63452a9b72d8172847796f9af958f9b2596da7ea4be"

# redis配置
REDIS_HOST = '10.157.85.237'
REDIS_PORT = '6379'
REDIS_DB = 1
REDIS_DECODE_RESPONSES = False
REDIS_PASSWORD = None


RABBITMQ_USERNAME = "guest"
RABBITMQ_PASSWORD = "guest"
RABBITMQ_HOST = "10.157.85.237"
RABBITMQ_PORT = 6672
RABBITMQ_VHOST = "/"
RABBITMQ_QUEUE_ETL_MSG_OUT = "etl-msg-out"
RABBITMQ_QUEUE_DATA_TO_BACKEND = "data-to-backend"

# 调用aml接口的url
CALL_AML_URL = "http://10.157.85.237:5002/api/v1/gum-sheeting"

# 回写地址
WRITE_BACK_URL = "http://10.157.85.237:5080/v1/api/opcTagWrite"
WRITE_BACK_AUTH_KEY = "SEb92Y8GfdBrwmf6rZ51eZeAskXOJWjNEb1iZqSkY799DHri4G92GTAf5hyYqRoD"

# BLOB
BLOB_SOURCE_CONN_STR = "DefaultEndpointsProtocol=http;BlobEndpoint=http://10.157.85.237:11002/yngiotedgeblob;AccountName=yngiotedgeblob;AccountKey=ORmPAba6sb7Ku19pjm8yIsnjiFDdCR0rrOM3sCcZU+LwPnL9wd/3Ls3ykW1qXQvcacw2xjfihDh0VDEJAgaQuw=="
BLOB_SOURCE_CONTAINER_NAME = "yng"



