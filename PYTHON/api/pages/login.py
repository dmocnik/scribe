from passlib.hash import sha256_crypt
from PYTHON.api.models import User, Codes
import sqlalchemy
from sqlalchemy import update, select, insert, and_
import random
from datetime import datetime, timedelta

from fastapi import APIRouter, Response, Body, Depends
from PYTHON.api.verifier import SessionData, backend, cookie, verifier
from PYTHON.api.config import settings
from PYTHON.smtp.smtp_module import scribe_smtp
from uuid import UUID, uuid4
import string
from urllib.parse import quote_plus

account = APIRouter()

# login with username and password
@account.post('/login')
# async def login(email: str, password: str, response: Response):
async def login(response: Response, email: str = Body(), password: str = Body()):

    # create database engine
    engine = sqlalchemy.create_engine(settings.DATABASE_URI)

    # make statement and execute
    stmt = select(User.password_hash).where(and_(User.email == email, User.disabled == False))
    with engine.connect() as conn:
        row = conn.execute(stmt).first()

    # if email exists in db and password hash matches, 
    if row is not None and sha256_crypt.verify(password, row[0]):

        # initialize session and return ok
        session = uuid4()
        data = SessionData(email=email)

        await backend.create(session, data)
        cookie.attach_to_response(response, session)

        return 'ok'

    # otherwise return 401 if invalid creds
    else:    
        response.status_code = 401
        return
    
# get email of current session
@account.get('/email', dependencies=[Depends(cookie)])
async def get_email(session_data: SessionData = Depends(verifier)):
    return session_data

# given email address, send reset password link
# adds entry to Codes table and send email
# TODO: check bad email
@account.post('/password/reset/request')
def password_request_reset(response: Response, email: str = Body(embed=True)):
    # connect to db
    engine = sqlalchemy.create_engine(settings.DATABASE_URI)

    # generate random code
    code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(64))
    # hash the code
    code_hash = sha256_crypt.encrypt(code)

    # set expiration to 15 minutes
    expiration = datetime.utcnow() + timedelta(minutes=15)

    # get user id from matching email
    stmt = select(User.id, User.name).where(User.email == email)
    with engine.connect() as conn:
        user_db = conn.execute(stmt).first()

    # add code to db
    stmt = insert(Codes).values(user_ID=user_db[0], code_hash=code_hash, code_expiry=expiration)
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()

    print('added code to db')

    data = {
        "reset_link": settings.FRONTEND_URL + "/reset-password?email=" + quote_plus(email) + "&code=" + code 
    }

    if user_db[1] == "":
        data["name"] = email
    else:
        data["name"] = user_db[1]

    # send email with link and code
    smtp_driver = scribe_smtp(settings.smtp_server, settings.smtp_port, settings.smtp_username, settings.password)
    # success = smtp_driver.send_email(to=email,subject='Password Reset Request', body=f"oi here's your code: {code}")
    success = smtp_driver.send_template(to=email, subject='Password Reset Request', template='password_reset.html', data=data)

    # if email failed, let em know
    if not success:
        response.status_code = 400
        return
    
    # # print code
    # print(code)

    return 'ok'

# given email and login code, add session email and session code
@account.post('/account/login/code')
async def login_code(response: Response, email: str = Body(), code: str = Body()):

    # connect to db and get matching codes that expire after utc now
    engine = sqlalchemy.create_engine(settings.DATABASE_URI)
    stmt = (
        select(Codes.code_hash, Codes.code_expiry)
        .join(User, User.id == Codes.user_ID)
        .where(User.email == email)
    )
    with engine.connect() as conn:
        result = conn.execute(stmt)
        result = [x for x in result] # doesn't iterate properly w/o this :(
        matched_codes = [x for x in result if sha256_crypt.verify(code, x[0])]
        valid_codes = [x for x in matched_codes if x[1] > datetime.utcnow()]

    # if no valid code exists, return bad creds
    if not len(valid_codes):
        response.status_code = 401
        return
    
    # otherwise, set session creds and return ok
    session = uuid4()
    data = SessionData(email=email, code=code)
    await backend.create(session, data)
    cookie.attach_to_response(response, session)

    return 'ok'

# given session code and new password, update password
@account.post('/password/reset', dependencies=[Depends(cookie)])
async def password_reset(response: Response, new_password: str = Body(embed=True), session_data: SessionData = Depends(verifier)):

    # confirm session code is still active
    engine = sqlalchemy.create_engine(settings.DATABASE_URI)
    stmt = select(Codes.code_hash, Codes.code_expiry).join(User, User.id == Codes.user_ID).where(and_(Codes.code_expiry > datetime.utcnow(), User.email == session_data.email))
    with engine.connect() as conn:
        result = conn.execute(stmt)
        result = [x for x in result]
        matched_codes = [x for x in result if sha256_crypt.verify(session_data.code, x[0])]

    # if no valid code exists, return bad creds
    if not len(matched_codes):
        response.status_code = 401
        return
    
    # otherwise, update password
    stmt = (update(User).values(password_hash=sha256_crypt.encrypt(new_password)).where(User.email == session_data.email))
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()

    # and expire the current code so it cannot be used again
    stmt = (update(Codes).values(code_expiry=datetime.utcnow()).where(Codes.code_hash == matched_codes[0][0]))
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()

    return 'ok'

# given session email and valid old password and new password, update password
@account.post('/password/update', dependencies=[Depends(cookie)])
def password_update(response: Response, old_password: str = Body(), new_password: str = Body(), session_data: SessionData = Depends(verifier)):

    # check old password is valid
    engine = sqlalchemy.create_engine(settings.DATABASE_URI)
    stmt = select(User.password_hash).where(User.email == session_data.email)
    with engine.connect() as conn:
        result = conn.execute(stmt)
        result = [x for x in result]
        print(result)
        is_valid = sha256_crypt.verify(old_password, result[0][0])

    # if invalid old password, return unauthorized
    if not is_valid:
        response.status_code = 401
        return
    
    # otherwise, update password
    stmt = update(User).values(password_hash=sha256_crypt.encrypt(new_password)).where(User.email == session_data.email)
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()

    return 'ok'

# delete account and ALL DATA
@account.post('/account/delete', dependencies=[Depends(cookie)])
def delete_account(response: Response, password: str = Body()):

    # check password

    # delete everything from 

    response.status_code = 501
    return

# create account
# TODO discuss cleaning email, bad users may try some wild injections
@account.post('/account/create')
async def create_account(response: Response, email: str = Body(), password: str = Body(), name: str = Body()):

    # create database engine
    engine = sqlalchemy.create_engine(settings.DATABASE_URI)

    # Database connection session
    Session = sqlalchemy.orm.sessionmaker()
    Session.configure(bind=engine)
    Session = Session()

    # check that email does not exist in db
    user_exists = Session.query(User.email).where(User.email == email).first() is not None

    if user_exists:
        response.status_code = 409
        return
    
    # hash password
    password_hash = sha256_crypt.encrypt(password)

    # Make User object
    user = User(
        email=email, 
        password_hash=password_hash,
        name=name, 
        disabled=True)
    
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
    code = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(64))

    # make a code object
    user_code = Codes(
        user_ID=user_id,
        code_hash=sha256_crypt.encrypt(code),
        code_expiry=code_expiry
    )

    # add code to db
    Session.add(user_code)
    Session.commit()

    # populate email
    data = {}
    if name == "":
        data["name"] = email
    else:
        data["name"] = name

    data["verification_link"] = settings.FRONTEND_URL + "/verify-account?email=" + quote_plus(email) + "&code=" + code

    # send an email
    smtp_driver = scribe_smtp(settings.smtp_server, settings.smtp_port, settings.smtp_username, settings.password)
    # success = smtp_driver.send_email(to=email,subject='Email Confirmation Code', body=f"oi here's your code: {code}")
    success = smtp_driver.send_template(to=email, subject='Welcome to Scribe! Please Confirm Your Email', template='verify_account.html', data=data)

    # if email failed, return failure
    if not success:
        response.status_code = 400
        return 

    # print code to console
    # print(code)

    return 'ok'

# deactivate account
@account.post('/account/deactivate', dependencies=[Depends(cookie)])
def deactivate_account(response: Response, email: str = Body(), session_data: SessionData = Depends(verifier)):

    # if not matching - someone's trying to deactivate an email they don't have access to
    if email != session_data.email:
        response.status_code = 401
        return

    # setup db session
    engine = sqlalchemy.create_engine(settings.DATABASE_URI)
    Session = sqlalchemy.orm.sessionmaker()
    Session.configure(bind=engine)
    Session = Session()

    # set disabled to True
    stmt = update(User).where(User.email == session_data.email).values(disabled=True)
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()
        
    # return success
    return 'ok'

# given email and code, activate account
@account.post('/account/activate')
def activate_account(response: Response, email: str = Body(), code: str = Body()):

    # setup db session
    engine = sqlalchemy.create_engine(settings.DATABASE_URI)
    Session = sqlalchemy.orm.sessionmaker()
    Session.configure(bind=engine)
    Session = Session()

    # get unexpired codes matching user email
    stmt = select(Codes.code_hash).join(User, User.id == Codes.user_ID).where(and_(User.email == email, Codes.code_expiry > datetime.utcnow()))
    with engine.connect() as conn:
        result = conn.execute(stmt)
        result = [x for x in result]
        matched_codes = [x for x in result if sha256_crypt.verify(code, x[0])]

    if not len(matched_codes):
        response.status_code = 401
        return

    # set disabled to True
    stmt = update(User).where(and_(User.email == email)).values(disabled=False)
    with engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()
        
    # return success
    return 'ok'

