class Config(object):
    TESTING = False

class DevelopmentConfig(Config):
    DATABASE_URI = "mariadb+mariadbconnector://rob@localhost:3306/scribe"
    API_URL = 'http://localhost:5000/swagger.json'
    SWAGGER_URL = '/api/docs'

class ProductionConfig(Config):
    DATABASE_URI = ""

class TestingConfig(Config):
    DATABASE_URI = ""
    TESTING = True