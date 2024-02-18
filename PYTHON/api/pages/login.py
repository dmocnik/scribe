from flask import Blueprint, request, session, current_app
from passlib.hash import sha256_crypt
from ..models import User, Codes
import sqlalchemy
from sqlalchemy import update, select, insert, and_
import random
from datetime import datetime, timedelta

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

    # make statement and execute
    stmt = select(User.password_hash).where(User.email == email)
    with engine.connect() as conn:
        row = conn.execute(stmt).first()

    # if email exists in db and password hash matches, 
    if row is not None and sha256_crypt.verify(password, row[0]):

        # initialize session and return ok
        session['email'] = email
        return 'ok'

    # otherwise return 401 if invalid creds
    else:    
        return "Unauthorized", 401
    
# get email of current session
@account.get('/email')
def get_email():

    return session.get('email', '')

# given email address, send reset password link
# adds entry to Codes table and send email
@account.post('/password/reset/request')
def password_request_reset():

    # get email from form
    email = request.json["email"]

    # connect to db
    engine = sqlalchemy.create_engine(current_app.config["DATABASE_URI"])

    # generate random code
    code = sha256_crypt.encrypt(str(random.random()))

    # hash the code
    code_hash = sha256_crypt.encrypt(code)

    # set expiration to 15 minutes
    expiration = datetime.utcnow() + timedelta(minutes=15)

    # get user id from matching email
    stmt = select(User.id).where(User.email == email)
    with engine.connect() as conn:
        user_id = conn.execute(stmt).first()[0]

    # add code to db
    stmt = insert(Codes).values(user_ID=user_id, code_hash=code_hash, code_expiry=expiration)
    with engine.connect() as conn:
        conn.execute(stmt)

    # TODO send email with link and code
        
    # print code
    print(code)

    return 'ok'

# given email and login code, add session email and session code
@account.post('/account/login/code')
def login_code():

    # get email and code from form
    email = request.json["email"]
    code = request.json["code"]

    # connect to db and get matching codes that expire after utc now
    engine = sqlalchemy.create_engine(current_app.config["DATABASE_URI"])
    stmt = select([Codes.code_hash, Codes.code_expiry]).join(User, User.id == Codes.user_ID).where(User.email == email)
    with engine.connect() as conn:
        result = conn.execute(stmt)
        matched_codes = [x for x in result if sha256_crypt.verify(code, x[0])]
        valid_codes = [x for x in matched_codes if x[1] > datetime.utcnow()]

    # if no valid code exists, return bad creds
    if not len(valid_codes):
        return 'Expired', 401
    
    # otherwise, set session creds and return ok
    session["email"] = email
    session["code"] = code

    return 'ok'

# given session code and new password, update password
@account.post('/password/reset')
def password_reset():

    # get new password from request
    new_password = request.json["new_password"]

    # confirm session code is still active
    engine = sqlalchemy.create_engine(current_app.config["DATABASE_URI"])
    stmt = select([Codes.code_hash, Codes.code_expiry]).join(User, User.id == Codes.user_ID).where(and_(Codes.code_expiry > datetime.utcnow(), User.email == session["email"]))
    with engine.connect() as conn:
        result = conn.execute(stmt)
        matched_codes = [x for x in result if sha256_crypt.verify(session["code"], x[0])]

    # if no valid code exists, return bad creds
    if not len(matched_codes):
        return 'Expired', 401
    
    # otherwise, update password
    stmt = (insert(User).values(password_hash=sha256_crypt.encrypt(new_password)).where(User.email == session["email"]))
    with engine.connect() as conn:
        conn.execute(stmt)

    # and expire the current code so it cannot be used again
    stmt = (insert(Codes).values(code_expiry=datetime.utcnow()).where(Codes.code_hash == matched_codes[0][0]))
    with engine.connect() as conn:
        conn.execute(stmt)

    return 'ok'

# given session email and valid old password and new password, update password
@account.post('/password/update')
def password_update():

    # if session email is not set, return 401
    if not len(session.get("email","")):
        return "unauthorized", 401

    # get passwords from request
    old_password = request.json["old_password"]
    new_password = request.json["new_password"]

    # check old password is valid
    engine = sqlalchemy.create_engine(current_app.config["DATABASE_URI"])
    stmt = select(User.password_hash).where(User.email == session["email"])
    with engine.connect() as conn:
        result = conn.execute(stmt)[0]
        is_valid = sha256_crypt.verify(old_password, result[0])

    # if invalid old password, return unauthorized
    if not is_valid:
        return 'Unauthorized', 401
    
    # otherwise, update password
    stmt = insert(User.password_hash).values(sha256_crypt.encrypt(new_password)).where(User.email == session["email"])
    with engine.connect() as conn:
        conn.execute(stmt)

    return 'ok'

# delete account and ALL DATA
@account.post('/account/delete')
def delete_account():

    return 'Not Implemented', 501

# create account
@account.post('/account/create')
def create_account():

    # get creds
    email = request.json["email"]
    password = request.json["password"]
    if "name" in request.json:
        name = request.json["name"]
    else:
        name = ""

    # create database engine
    engine = sqlalchemy.create_engine(current_app.config["DATABASE_URI"])

    # Database connection session
    Session = sqlalchemy.orm.sessionmaker()
    Session.configure(bind=engine)
    Session = Session()

    # check that email does not exist in db
    user_exists = Session.query(User.email).where(User.email == email).first() is not None

    if user_exists:
        return 'Conflict', 409
    
    # hash password
    password_hash = sha256_crypt.encrypt(password)

    # Make User object
    user = User(
        email=email, 
        password_hash=password_hash,
        name=name)
    
    # insert into db
    Session.add(user)
    Session.commit()

    # get user id
    stmt = select(User.id).where(User.email == email)
    with engine.connect() as conn:
        row = conn.execute(stmt).first()

    # get user id from row
    user_id = row[0]

    # set code expiry
    code_expiry = datetime.utcnow() + timedelta(minutes=15)

    # make code a hash of the hashed password
    code = sha256_crypt.encrypt(password_hash)

    # make a code object
    user_code = Codes(
        user_ID=user_id,
        code_hash=sha256_crypt.encrypt(code),
        code_expiry=code_expiry
    )

    # add to db
    Session.add(user_code)
    Session.commit()

    # TODO send an email

    # print code to console
    print(code)

    return 'ok'

# deactivate account
@account.post('/account/deactivate')
def deactivate_account():

    # get username from form
    email = request.json["email"]

    # get email from session
    session_email = session["email"]

    # if not matching - someone's trying to deactivate an email they don't have
    # access to
    if email != session_email:
        return 'Unauthorized', 401

    # setup db session
    engine = sqlalchemy.create_engine(current_app.config["DATABASE_URI"])
    Session = sqlalchemy.orm.sessionmaker()
    Session.configure(bind=engine)
    Session = Session()

    # check user exists
    user_exists = Session.query(User.email).where(User.email == email).first() is not None

    # if user doesn't exist, return 404
    if not user_exists:
        return 'Not Found', 404

    # set disabled to True
    stmt = update(User).where(User.email == session_email).values(disabled=True)
    with engine.connect() as conn:
        conn.execute(stmt)
        
    # return success
    return 'ok'

# activate account
@account.post('/account/activate')
def activate_account():

    # get username from form
    email = request.json["email"]
    code = request.json["code"]

    # setup db session
    engine = sqlalchemy.create_engine(current_app.config["DATABASE_URI"])
    Session = sqlalchemy.orm.sessionmaker()
    Session.configure(bind=engine)
    Session = Session()

    # check user exists
    user_exists = Session.query(User.email).where(User.email == email).first() is not None

    # if user doesn't exist, return 404
    if not user_exists:
        return 'Not Found', 404
    
    # get unexpired codes matching user email
    stmt = select(Codes.code_hash).join(User, User.id == Codes.user_ID).where(and_(User.email == email, Codes.code_expiry > datetime.utcnow()))
    with engine.connect() as conn:
        res = conn.execute(stmt)
        matched_codes = [x for x in res if sha256_crypt.verify(code, x[0])]

    if not len(matched_codes):
        return "Expired", 410

    # set disabled to True
    stmt = update(User).where(and_(User.email == email)).values(disabled=False)
    with engine.connect() as conn:
        conn.execute(stmt)
        
    # return success
    return 'ok'
