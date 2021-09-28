import os


class Config(object):
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PROPAGATE_EXCEPTIONS = True
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']


class ProductionConfig(Config):
    SECRET_KEY = b'b\xf1\xb4\xfe\x95\xc9\xe0\xc6\xec?k\x15\xb6\x86i\xa5\xf6ih\xc5\xb3xa]'
    # 真正資料庫
    uri = os.environ.get("DATABASE_URL")  # or other relevant config var
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = uri


class DevelopmentConfig(Config):
    ENV = "development"
    SECRET_KEY = "Development_SECRET_KEY"
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = 開發用輕量資料庫(如SQLite)


class TestingConfig(Config):
    TESTING = True
    # SQLALCHEMY_DATABASE_URI = 測試用資料庫(如記憶體資料庫)


config = {
    'production': ProductionConfig,
    'development': DevelopmentConfig,
    'default': DevelopmentConfig,
    'testing': TestingConfig
}
