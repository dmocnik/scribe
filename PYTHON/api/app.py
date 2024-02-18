from .config import DevelopmentConfig
from .swagger.swagger_setup import setup_swagger
from .pages.login import account
from flask_cors import CORS
from flask import Flask, session
from flask_session import Session
import json

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)
app.config['SESSION_TYPE'] = 'filesystem'
CORS(app)
Session(app)

# setup swagger
setup_swagger(app, app.config)

# add account routes
app.register_blueprint(account)

# add get swagger.json
@app.get('/swagger.json')
def get_swagger():
    with open('./swagger/swagger.json') as f:
        data = json.load(f)
        return data

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

# healthcheck to test if api is running
@app.route('/healthcheck')
def healthcheck():
    return 'ok'