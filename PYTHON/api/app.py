from .config import DevelopmentConfig
from .swagger.swagger_setup import setup_swagger
from .pages.login import account
from flask_cors import CORS
from flask import Flask, session
from flask_session import Session

from flask import request, current_app
import sqlalchemy
from .models import User


app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
app.config['SESSION_TYPE'] = 'filesystem'
CORS(app)
Session(app)

# setup swagger
setup_swagger(app, app.config)

# add routes
app.register_blueprint(account)

# test session headers and whatnot
@app.route('/set/')
def set():
    print(f'session: {session}')
    session['key'] = session.sid
    return 'ok'

# test session headers
@app.route('/get/')
def get():
    return session.get('key', 'not set')