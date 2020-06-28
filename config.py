#! /usr/bin/python3

class BaseConfig:
    """
    Basic config file for Flask application
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret'
    INTERVAL_TIME = 5

class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    APP_PROD_SERVER = '172.17.0.2:1433'
    APP_PROD_DB = 'prod_db'
    APP_PROD_USER = 'sa'
    APP_PROD_PWD = 'test2_db'

class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    DATABASE_URI = os.environ.get('DEV_DATABASE_URI')
    APP_PROD_DB = 'prod.db'
    APP_QUALITY_DB = 'quality.db'

config = {
    'production' : ProductionConfig,
    'testing' : TestingConfig,
    'development' : DevelopmentConfig
}