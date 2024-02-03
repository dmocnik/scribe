from flask import Blueprint, request, session, current_app
from passlib.hash import sha256_crypt
from ..models import User
import sqlalchemy

# set account as Blueprint object
account = Blueprint('account', __name__)

# login with username and password
@account.post('/login')
def login():

    # get creds from login form
    email = request.json["email"]
    password = request.json["password"]

    # create database engine
    engine = sqlalchemy.create_engine(current_app.config["DATABASE_URI"])

    # hash password
    password_hash = sha256_crypt.encrypt(password)

    # Database connection session
    Session = sqlalchemy.orm.sessionmaker()
    Session.configure(bind=engine)
    Session = Session()

    # Select password hash with matching email
    row = Session.query(User).where(User.Email == email)

    # if email exists in db and password hash matches, 
    if row.count() > 0 and sha256_crypt.verify(password, row[0].__dict__['PasswordHash']):

        # initialize session and return ok
        session['email'] = email
        return 'ok'

    # otherwise return 400 if invalid creds
    else:    
        return "Bad Request", 400
    
# get email of current session
@account.get('/email')
def get_email():

    return session.get('email', '')