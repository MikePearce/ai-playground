import os 

class Config(object):
    DEBUG = True
    TESTING = False

class DevelopmentConfig(Config):
    SECRET_KEY = "asdasd23d23d23dasffaerg43yserthasdfvawt"

config = {
    'development': DevelopmentConfig,
    'testing': DevelopmentConfig,
    'production': DevelopmentConfig
}


UPLOAD_FOLDER = 'uploads'



## Enter your Open API Key here
OPENAI_API_KEY = os.environ.get('OPENAI_KEY')
