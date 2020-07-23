#! /usr/bin/python3

from os import environ as env

class BaseConfig:
    """
    Basic config file for Flask application
    """
    SECRET_KEY = env.get('SECRET_KEY') or 'secret'
    INTERVAL_TIME = 5
    TBL_SENSOR = 'tbl_sensor'
    TBL_TEMPERATURE = 'tbl_temperature'
    TBL_USER = 'tbl_user'
    TBL_TEMP_MAX = 10000

class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False
    DATABASE_URI = env.get('DEV_DATABASE_URI')
    APP_DATABASE = 'temperature_db.db'

class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True
    DATABASE_URI = env.get('DEV_DATABASE_URI')
    APP_DATABASE = 'temperature_db.db'

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    DATABASE_URI = env.get('DEV_DATABASE_URI')
    APP_DATABASE = 'temperature_db.db'

config = {
    'production' : ProductionConfig,
    'testing' : TestingConfig,
    'development' : DevelopmentConfig
}