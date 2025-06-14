import os


class Config:
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///2CommunityApp.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET = os.getenv('SECRET_KEY', 'default_secret_key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'default_jwt_secret_key')
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = 604800  # 7 days


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///2CommunityApp_dev.db'
    SECRET = os.getenv('DEV_SECRET_KEY', 'dev_default_secret_key')
    JWT_SECRET_KEY = os.getenv('DEV_JWT_SECRET_KEY', 'dev_default_jwt_secret_key')
    JWT_ACCESS_TOKEN_EXPIRES = 300 # 5 minutes
    JWT_REFRESH_TOKEN_EXPIRES = 660 # 11 minutes

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///2CommunityApp_test.db'
    SECRET = os.getenv('TEST_SECRET_KEY', 'test_default_secret_key')
