from fastapi import APIRouter, Response, Body, Depends, UploadFile, File, HTTPException, Header, Form
from typing import Annotated
from PYTHON.api.verifier import SessionData, backend, cookie, verifier
from PYTHON.api.config import settings
from uuid import uuid4
from datetime import datetime, timedelta

import os

import sqlalchemy
from sqlalchemy import update, select, insert, and_, create_engine
from sqlalchemy.orm import Session

from PYTHON.api.models import User, Project, Media

media = APIRouter()

# create project (given user id (session) and project name)
@media.post('/project/create', dependencies=[Depends(cookie)])
def create_project(project_name: str = Body(embed=True), session_data: SessionData = Depends(verifier)):

    # connect to db
    engine = create_engine(settings.DATABASE_URI)

    # get user id from session email
    stmt = select(User.id).where(User.email == session_data.email)
    with engine.connect() as conn:
        user_id = conn.execute(stmt).first()[0]

    # make a new project object w/ project name and user_id
    project = Project(name=project_name, user_id=user_id, status='Waiting for Upload', last_modified=datetime.utcnow())
    with Session(engine) as session:
        session.add(project)
        session.commit()

        return project.id

# get project info (given project id)
@media.post('/project/read', dependencies=[Depends(cookie)])
def get_project(response: Response, project_id: str = Body(embed=True), session_data: SessionData = Depends(verifier)):

    engine = create_engine(settings.DATABASE_URI)

    stmt = select(User.id).join(Project).where(and_(Project.id == project_id, User.email == session_data.email))
    with engine.connect() as conn:
        res = conn.execute(stmt).first()

    if res is None:
        response.status_code = 404
        return

    stmt = select(Project.id, Project.name, Project.trashed, Project.last_modified).where(Project.id == project_id)
    with engine.connect() as conn:
        project_db = conn.execute(stmt).first()

    project = project_db._asdict()

    project["media"] = []

    stmt = select(Media.name, Media.id, Media.type, Media.file_type).where(Media.project_id == project_id)
    with engine.connect() as conn:
        media_dbs = conn.execute(stmt)

    project["media"] = []

    for media_db in media_dbs:

        project["media"].append(media_db._asdict())

    return project

# update project name
@media.post('/project/{project_id}/edit', dependencies=[Depends(cookie)])
def update_project(project_id: str, response: Response, project_name: str = Body(embed=True), session_data: SessionData = Depends(verifier)):

    # connect to db
    engine = create_engine(settings.DATABASE_URI)

    # get user id from session email
    stmt = select(User.id).join(Project).where(and_(Project.id == project_id, User.email == session_data.email))
    with engine.connect() as conn:
        user_id = conn.execute(stmt).first()[0]

    if user_id is None:
        response.status_code = 404
        return "Not Found"

    # make a new project object w/ project name and user_id
    with Session(engine) as session:
        project = session.get(Project, project_id)
        project.name = project_name
        project.last_modified = datetime.utcnow()
        session.commit()

        return project.id

# delete project (given project id)
@media.post('/project/{project_id}/delete', dependencies=[Depends(cookie)])
def delete_project(project_id: str, response: Response, session_data: SessionData = Depends(verifier)):

    # connect to db
    engine = create_engine(settings.DATABASE_URI)

    # get user id from session email
    stmt = select(User.id).join(Project).where(and_(Project.id == project_id, User.email == session_data.email))
    with engine.connect() as conn:
        user_id = conn.execute(stmt).first()[0]

    if user_id is None:
        response.status_code = 404
        return "Not Found"

    # make a new project object w/ project name and user_id
    with Session(engine) as session:
        project = session.get(Project, project_id)
        session.delete(project)
        session.commit()

        return "ok"

# trash project
@media.post('/project/{project_id}/trash', dependencies=[Depends(cookie)])
def trash_project(project_id: str, response: Response, session_data: SessionData = Depends(verifier)):

    # connect to db
    engine = create_engine(settings.DATABASE_URI)

    # get user id from session email
    stmt = select(User.id).join(Project).where(and_(Project.id == project_id, User.email == session_data.email))
    with engine.connect() as conn:
        user_id = conn.execute(stmt).first()[0]

    if user_id is None:
        response.status_code = 404
        return "Not Found"

    # make a new project object w/ project name and user_id
    with Session(engine) as session:
        project = session.get(Project, project_id)
        project.trashed = True
        session.commit()

        return "ok"

# restore project after being trashed
@media.post('/project/{project_id}/restore', dependencies=[Depends(cookie)])
def trash_project(project_id: str, response: Response, session_data: SessionData = Depends(verifier)):

    # connect to db
    engine = create_engine(settings.DATABASE_URI)

    # get user id from session email
    stmt = select(User.id).join(Project).where(and_(Project.id == project_id, User.email == session_data.email))
    with engine.connect() as conn:
        user_id = conn.execute(stmt).first()[0]

    if user_id is None:
        response.status_code = 404
        return "Not Found"

    # make a new project object w/ project name and user_id
    with Session(engine) as session:
        project = session.get(Project, project_id)
        project.trashed = False
        session.commit()

        return "ok"

# list project objects
@media.get('/project/list', dependencies=[Depends(cookie)])
def list_projects(session_data: SessionData = Depends(verifier)):

    # connect to db
    engine = create_engine(settings.DATABASE_URI)

    # get user id from session email
    stmt = select(Project.id, Project.name, Project.trashed, Project.last_modified).join(User).where(User.email == session_data.email)
    with engine.connect() as conn:
        project_dbs = conn.execute(stmt)

    projects = []

    for project_db in project_dbs:

        project = {
            "name": getattr(project_db, "name"),
            "id": getattr(project_db, "id"),
            "trashed": getattr(project_db, "trashed"),
            "last_modified": getattr(project_db, "last_modified"),
            "media": []
        }

        stmt = select(Media.name, Media.id, Media.type, Media.file_type).where(Media.project_id == getattr(project_db, "id"))
        with engine.connect() as conn:
            media_dbs = conn.execute(stmt)

        for media_db in media_dbs:

            project["media"].append(media_db._asdict())

        projects.append(project)

    return projects

# get name, type, and file type of media
@media.get('/project/{project_id}/media/{media_id}', dependencies=[Depends(cookie)])
def get_media(project_id: str, media_id: str, response: Response, session_data: SessionData = Depends(verifier)):

    engine = create_engine(settings.DATABASE_URI)
    
    stmt = select(Media.name, Media.type, Media.file_type).join(Project, Project.id == Media.project_id).join(User, User.id == Project.user_id).where(and_(Media.id == media_id, Media.project_id == project_id, User.email == session_data.email))
    print(stmt)
    with engine.connect() as conn:
        row = conn.execute(stmt).first()

    if row is None:
        response.status_code = 404
        return "Not Found"

    return row._asdict()

# create media (given project id, media name, media type, and media file)
# TODO how to deal with conflicts? require deleting old or allow overwrite?
# TODO differentiate 404 (not found) and 403 (forbidden)
@media.post('/project/{project_id}', dependencies=[Depends(cookie)])
def create_media(
    response: Response, 
    media_content: Annotated[bytes, File()], 
    project_id: str, 
    media_name: str = Body(), 
    media_type: str  = Body(),
    file_type: str = Body(), 
    session_data: SessionData = Depends(verifier)):

    # make sure session.email can access the project
    engine = create_engine(settings.DATABASE_URI)

    stmt = select(User.id).join(Project, Project.user_id == User.id).where(and_(User.email == session_data.email, Project.id == project_id))
    print(stmt)
    with engine.connect() as conn:
        user_id = conn.execute(stmt).first()

    if user_id is None:
        response.status_code = 404
        return "Not Found"
    
    # make media object
    media = Media(name=media_name, type=media_type, content=media_content, project_id=project_id, file_type=file_type)

    # add media object and update project object
    with Session(engine) as session:
        session.add(media)
        session.commit()
        session.refresh(media)
        media_id = media.id

        return media.id

# get video mp4
@media.get('/project/{project_id}/video/mp4', dependencies=[Depends(cookie)])
def read_video_mp4(project_id: str, response: Response, session_data: SessionData = Depends(verifier)):

    # make sure session.email owns that media
    engine = create_engine(settings.DATABASE_URI)

    stmt = select(Media.content) \
        .join(Project, Project.id == Media.project_id) \
        .join(User, User.id == Project.user_id) \
        .where(and_(
            User.email == session_data.email, 
            Project.id == project_id, 
            Media.type == 'video',
            Media.file_type == 'mp4')
        )    
    with engine.connect() as conn:
        res = conn.execute(stmt).first()

    if res is None:
        response.status_code = 404
        return "Not Found"
   
    return Response(content=res[0], media_type="video/mp4")

# get video mov
@media.get('/project/{project_id}/video/mov', dependencies=[Depends(cookie)])
def read_media_wav(project_id: str, response: Response, session_data: SessionData = Depends(verifier)):

    # make sure session.email owns that media
    engine = create_engine(settings.DATABASE_URI)

    stmt = select(Media.content) \
        .join(Project, Project.id == Media.project_id) \
        .join(User, User.id == Project.user_id) \
        .where(and_(
            User.email == session_data.email, 
            Project.id == project_id, 
            Media.type == 'video',
            Media.file_type == 'mov')
        )    
    with engine.connect() as conn:
        res = conn.execute(stmt).first()

    if res is None:
        response.status_code = 404
        return "Not Found"
   
    return Response(content=res[0], media_type="video/mov")
        
# get transcript txt
@media.get('/project/{project_id}/transcript/txt', dependencies=[Depends(cookie)])
def read_media_txt(project_id: str, response: Response, session_data: SessionData = Depends(verifier)):

    # make sure session.email owns that media
    engine = create_engine(settings.DATABASE_URI)

    stmt = select(Media.content) \
        .join(Project, Project.id == Media.project_id) \
        .join(User, User.id == Project.user_id) \
        .where(and_(
            User.email == session_data.email, 
            Project.id == project_id, 
            Media.type == 'transcript',
            Media.file_type == 'txt',)
        )    
    with engine.connect() as conn:
        res = conn.execute(stmt).first()

    if res is None:
        response.status_code = 404
        return "Not Found"
   
    return Response(content=res[0], media_type="text/plain")

# get aisummary txt
@media.get('/project/{project_id}/aisummary/txt', dependencies=[Depends(cookie)])
def read_media(project_id: str, response: Response, session_data: SessionData = Depends(verifier)):

    # make sure session.email owns that media
    engine = create_engine(settings.DATABASE_URI)

    stmt = select(Media.content) \
        .join(Project, Project.id == Media.project_id) \
        .join(User, User.id == Project.user_id) \
        .where(and_(
            User.email == session_data.email, 
            Project.id == project_id, 
            Media.type == 'aisummary',
            Media.file_type == 'txt')
        )    
    with engine.connect() as conn:
        res = conn.execute(stmt).first()

    if res is None:
        response.status_code = 404
        return "Not Found"
   
    return Response(content=res[0], media_type="text/plain")

# get aisummary md
@media.get('/project/{project_id}/aisummary/md', dependencies=[Depends(cookie)])
def read_media(project_id: str, response: Response, session_data: SessionData = Depends(verifier)):

    # make sure session.email owns that media
    engine = create_engine(settings.DATABASE_URI)

    stmt = select(Media.content) \
        .join(Project, Project.id == Media.project_id) \
        .join(User, User.id == Project.user_id) \
        .where(and_(
            User.email == session_data.email, 
            Project.id == project_id, 
            Media.type == 'aisummary',
            Media.file_type == 'md')
        )    
    with engine.connect() as conn:
        res = conn.execute(stmt).first()

    if res is None:
        response.status_code = 404
        return "Not Found"
   
    return Response(content=res[0], media_type="text/markdown")

# get aisummary pdf
@media.get('/project/{project_id}/aisummary/pdf', dependencies=[Depends(cookie)])
def read_media(project_id: str, response: Response, session_data: SessionData = Depends(verifier)):

    # make sure session.email owns that media
    engine = create_engine(settings.DATABASE_URI)

    stmt = select(Media.content) \
        .join(Project, Project.id == Media.project_id) \
        .join(User, User.id == Project.user_id) \
        .where(and_(
            User.email == session_data.email, 
            Project.id == project_id, 
            Media.type == 'aisummary',
            Media.file_type == 'pdf')
        )    
    with engine.connect() as conn:
        res = conn.execute(stmt).first()

    if res is None:
        response.status_code = 404
        return "Not Found"
   
    return Response(content=res[0], media_type="application/pdf")

# get ai_audio mp3
@media.get('/project/{project_id}/aiaudio/mp3', dependencies=[Depends(cookie)])
def read_media(project_id: str, response: Response, session_data: SessionData = Depends(verifier)):

    # make sure session.email owns that media
    engine = create_engine(settings.DATABASE_URI)

    stmt = select(Media.content) \
        .join(Project, Project.id == Media.project_id) \
        .join(User, User.id == Project.user_id) \
        .where(and_(
            User.email == session_data.email, 
            Project.id == project_id, 
            Media.type == 'aiaudio',
            Media.file_type == 'mp3')
        )    
    with engine.connect() as conn:
        res = conn.execute(stmt).first()

    if res is None:
        response.status_code = 404
        return "Not Found"
   
    return Response(content=res[0], media_type="audio/mp3")

# get ai_audio wav
@media.get('/project/{project_id}/aiaudio/wav', dependencies=[Depends(cookie)])
def read_media(project_id: str, response: Response, session_data: SessionData = Depends(verifier)):

    # make sure session.email owns that media
    engine = create_engine(settings.DATABASE_URI)

    stmt = select(Media.content) \
        .join(Project, Project.id == Media.project_id) \
        .join(User, User.id == Project.user_id) \
        .where(and_(
            User.email == session_data.email, 
            Project.id == project_id, 
            Media.type == 'aiaudio',
            Media.file_type == 'wav')
        )    
    with engine.connect() as conn:
        res = conn.execute(stmt).first()

    if res is None:
        response.status_code = 404
        return "Not Found"
   
    return Response(content=res[0], media_type="audio/wav")

# get ai_video mp4
@media.get('/project/{project_id}/aivideo/mp4', dependencies=[Depends(cookie)])
def read_media(project_id: str, response: Response, session_data: SessionData = Depends(verifier)):

    # make sure session.email owns that media
    engine = create_engine(settings.DATABASE_URI)

    stmt = select(Media.content) \
        .join(Project, Project.id == Media.project_id) \
        .join(User, User.id == Project.user_id) \
        .where(and_(
            User.email == session_data.email, 
            Project.id == project_id, 
            Media.type == 'aivideo',
            Media.file_type == 'mp4')
        )    
    with engine.connect() as conn:
        res = conn.execute(stmt).first()

    if res is None:
        response.status_code = 404
        return "Not Found"
   
    return Response(content=res[0], media_type="video/mp4")

# get ai_video mov
@media.get('/project/{project_id}/aivideo/mov', dependencies=[Depends(cookie)])
def read_media(project_id: str, response: Response, session_data: SessionData = Depends(verifier)):

    # make sure session.email owns that media
    engine = create_engine(settings.DATABASE_URI)

    stmt = select(Media.content) \
        .join(Project, Project.id == Media.project_id) \
        .join(User, User.id == Project.user_id) \
        .where(and_(
            User.email == session_data.email, 
            Project.id == project_id, 
            Media.type == 'aivideo',
            Media.file_type == 'mov')
        )    
    with engine.connect() as conn:
        res = conn.execute(stmt).first()

    if res is None:
        response.status_code = 404
        return "Not Found"
   
    return Response(content=res[0], media_type="video/mov")

# update media (given media id, field to update, and new content)
# TODO decide on workflow

# delete media (given media id)
@media.post("/project/{project_id}/media/{media_id}/delete", dependencies=[Depends(cookie)])
def delete_media(response: Response, project_id: str, media_id: str, session_data: SessionData = Depends(verifier)):

    engine = create_engine(settings.DATABASE_URI)

    stmt = select(User.id).join(Project, Project.user_id == User.id).join(Media, Media.project_id == Project.id).where(and_(User.email == session_data.email, Project.id == project_id, Media.id == media_id))
    with engine.connect() as conn:
        res = conn.execute(stmt)

    if res is None:
        response.status_code = 404
        return "Not Found"

    with Session(engine) as session:

        media = session.get(Media, media_id)
        session.delete(media)

        project = session.get(Project, project_id)
        project.last_modified = datetime.utcnow()

        session.commit()

        return 'ok'

@media.post('/project/{project_id}/internal')
def create_media_internal(response: Response, media_content: Annotated[bytes, File()], project_id: str, media_name: str = Body(), media_type: str  = Body(), host_key: str = Form(...)):
    if host_key != os.getenv("HOST_KEY"):
        response.status_code = 403
        return "Invalid host key"

    # make sure session.email can access the project
    engine = create_engine(settings.DATABASE_URI)
    
    # make media object
    media = Media(name=media_name, type=media_type, content=media_content, project_id=project_id)

    # add media object and update project object
    with Session(engine) as session:
        session.add(media)
        session.commit()

    return media.id

# get video, but for internal use requiring no auth besides host key
@media.post('/project/{project_id}/video/internal')
def read_media_internal(project_id: str, response: Response, host_key: str = Form(...)):
    if host_key != os.getenv("HOST_KEY"):
        response.status_code = 403
        return "Invalid host key"
    
    # make sure session.email owns that media
    engine = create_engine(settings.DATABASE_URI)

    stmt = select(Media.content) \
        .join(Project, Project.id == Media.project_id) \
        .where(and_(
            Project.id == project_id, 
            Media.type == 'video',)
        )    
    with engine.connect() as conn:
        res = conn.execute(stmt).first()

    if res is None:
        response.status_code = 404
        return "Not Found"

    return Response(content=res[0], media_type="video/mp4")

# get transcript, but for internal use requiring no auth besides host key
@media.post('/project/{project_id}/transcript/internal')
def read_media_internal(project_id: str, response: Response, host_key: str = Form(...)):
    if host_key != os.getenv("HOST_KEY"):
        response.status_code = 403
        return "Invalid host key"

    # make sure session.email owns that media
    engine = create_engine(settings.DATABASE_URI)

    stmt = select(Media.content) \
        .join(Project, Project.id == Media.project_id) \
        .where(and_(
            Project.id == project_id, 
            Media.type == 'transcript',)
        )    
    with engine.connect() as conn:
        res = conn.execute(stmt).first()

    if res is None:
        response.status_code = 404
        return "Not Found"

    return Response(content=res[0], media_type="text/plain")

# get aisummary, but for internal use requiring no auth besides host key
@media.post('/project/{project_id}/aisummary/internal')
def read_media_internal(project_id: str, response: Response, host_key: str = Form(...)):
    if host_key != os.getenv("HOST_KEY"):
        response.status_code = 403
        return "Invalid host key"
        
    # make sure session.email owns that media
    engine = create_engine(settings.DATABASE_URI)
    
    stmt = select(Media.content) \
        .join(Project, Project.id == Media.project_id) \
        .where(and_(
            Project.id == project_id, 
            Media.type == 'aisummary',)
        )    
    with engine.connect() as conn:
        res = conn.execute(stmt).first()
    
    if res is None:
        response.status_code = 404
        return "Not Found"
    
    return Response(content=res[0], media_type="text/plain")

# get ai_audio, but for internal use requiring no auth besides host key
@media.post('/project/{project_id}/aiaudio/internal')
def read_media_internal(project_id: str, response: Response, host_key: str = Form(...)):
    if host_key != os.getenv("HOST_KEY"):
        response.status_code = 403
        return "Invalid host key"
        
    # make sure session.email owns that media
    engine = create_engine(settings.DATABASE_URI)
    stmt = select(Media.content) \
        .join(Project, Project.id == Media.project_id) \
        .where(and_(
            Project.id == project_id, 
            Media.type == 'aiaudio',)
        )    
    with engine.connect() as conn:
        res = conn.execute(stmt).first()

    if res is None:
        response.status_code = 404
        return "Not Found"

    return Response(content=res[0], media_type="audio/mp3")

# post ai_video, but for internal use requiring no auth besides host key
@media.post('/project/{project_id}/aivideo/internal')
def read_media_internal(project_id: str, response: Response, host_key: str = Form(...)):

    if host_key != os.getenv("HOST_KEY"):
        response.status_code = 403
        return "Invalid host key"

    # make sure session.email owns that media
    engine = create_engine(settings.DATABASE_URI)

    stmt = select(Media.content) \
        .join(Project, Project.id == Media.project_id) \
        .where(and_(
            Project.id == project_id, 
            Media.type == 'aivideo',)
        )    
    with engine.connect() as conn:
        res = conn.execute(stmt).first()

    if res is None:
        response.status_code = 404
        return "Not Found"

    return Response(content=res[0], media_type="video/mp4")

# get aiaudio_clips, but for internal use requiring no auth besides host key
# this is a json file
@media.post('/project/{project_id}/aiaudio_clips/internal')
def read_media_internal(project_id: str, response: Response, host_key: str = Form(...)):
    if host_key != os.getenv("HOST_KEY"):
        response.status_code = 403
        return "Invalid host key"

    # make sure session.email owns that media
    engine = create_engine(settings.DATABASE_URI)

    stmt = select(Media.content) \
        .join(Project, Project.id == Media.project_id) \
        .where(and_(
            Project.id == project_id, 
            Media.type == 'aiaudio_clips',)
        )    
    with engine.connect() as conn:
        res = conn.execute(stmt).first()

    if res is None:
        response.status_code = 404
        return "Not Found"

    return Response(content=res[0], media_type="application/json")

# delete media (given media id), but for internal use requiring no auth besides host key
@media.post("/project/{project_id}/media/{media_id}/delete/internal")
def delete_media_internal(response: Response, project_id: str, media_id: str, host_key: str = Form(...)):

    if host_key != os.getenv("HOST_KEY"):
        raise HTTPException(status_code=403, detail="Invalid host key.")

    engine = create_engine(settings.DATABASE_URI)

    with Session(engine) as session:

        media = session.get(Media, media_id)
        session.delete(media)

        project = session.get(Project, project_id)
        project.last_modified = datetime.utcnow()

        session.commit()

        return 'ok'
    
# Healthcheck to verify if the hostkey is correct
@media.post('/healthcheck/internal')
def healthcheck_internal(host_key: str = Form(...)):  # Get the host key from the form body
    if host_key != os.getenv("HOST_KEY"):
        raise HTTPException(status_code=403, detail="Invalid host key, you provided: " + host_key)
    return 'ok'

# Regular healthcheck
@media.get('/healthcheck')
def healthcheck():
    return 'ok'

@media.post('/project/{project_id}/status/internal')
def update_project_status(project_id: str, response: Response, status_name: str = Form(...), host_key: str = Form(...)):
    if host_key != os.getenv("HOST_KEY"):
        raise HTTPException(status_code=403, detail="Invalid host key.")

    # connect to db
    engine = create_engine(settings.DATABASE_URI)

    # enum('Ready','Waiting for Upload','Processing')

    # make a new project object w/ status name and user_id
    with Session(engine) as session:
        project = session.get(Project, project_id)
        project.status = status_name
        project.last_modified = datetime.utcnow()
        session.commit()

        return project.id