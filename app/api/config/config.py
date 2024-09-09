from decouple import config

class Config:
    SECRET_KEY = config('SECRET_KEY', 'secret')

class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = config('DATABASE_URL')
    SQLALCHEMY_ECHO = True
    DEBUG = True


config_dict = {
    'dev': DevConfig
}
