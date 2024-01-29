from .config import DevelopmentConfig
from .swagger.swagger_setup import setup_swagger
from .routes import routes
from flask_cors import CORS
from flask import Flask

app = Flask(__name__)
CORS(app)

# Set config
config = DevelopmentConfig()

# setup swagger
setup_swagger(app, config)

# add routes
app.register_blueprint(routes)

