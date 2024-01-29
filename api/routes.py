from flask import Blueprint
import sqlalchemy
import json
# from ..config import DevelopmentConfig as config
from .config import DevelopmentConfig
from .models import Employee

# set routes as a Blueprint object
routes = Blueprint('routes', __name__)

# set config
config = DevelopmentConfig()

# route for swagger to get the json
@routes.route('/swagger.json')
def get_swagger():

    f = open('./swagger/swagger.json')

    data = json.load(f)

    return data

# test route
@routes.route("/")
def hello_world():
    return {
        "field1": 0,
        "field2": 1,
        "field3": 2
    }

# database test route
@routes.route('/dbtest')
def dbtest():

    # idk engine or smth
    engine = sqlalchemy.create_engine(config.DATABASE_URI)

    # session or smth
    Session = sqlalchemy.orm.sessionmaker()
    Session.configure(bind=engine)
    Session = Session()

    # query or smth
    employees = Session.query(Employee).all()

    # return as json serializable objects
    return [x.as_dict() for x in employees]