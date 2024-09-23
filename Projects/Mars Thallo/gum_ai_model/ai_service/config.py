class SpcDBPoolConfig:
    server2 = None
    port2 = None
    database2 = None
    user2 = None
    password2 = None

    @classmethod
    def init(cls, config):
        cls.server2 = config['SPC_DB_SERVER']
        cls.port2 = config['SPC_DB_PORT']
        cls.database2 = config['SPC_DB_DATABASE']
        cls.user2 = config['SPC_DB_USERNAME']
        cls.password2 = config['SPC_DB_PASSWORD']
