from fastapi import APIRouter, Response, Body, Depends, UploadFile, File
from typing import Annotated
from PYTHON.api.verifier import SessionData, backend, cookie, verifier
from PYTHON.api.config import settings
from uuid import uuid4
import base64

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
    project = Project(name=project_name, user_id=user_id)
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
        res = conn.execute(stmt)

    if res is None:
        return 404

    project = {}

    stmt = select(Project.name).where(Project.id == project_id)
    with engine.connect() as conn:
        project["name"] = conn.execute(stmt).first()[0]

    stmt = select(Media.name, Media.id, Media.type).where(Media.project_id == project_id)
    with engine.connect() as conn:
        media_dbs = conn.execute(stmt)

    project["media"] = []

    for media_db in media_dbs:

        project["media"].append(media_db._asdict())

    return project

# update project (can only really update name)
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
        session.commit()

        return project.id

# delete project (given project id)
@media.post('/project/{project_id}/delete', dependencies=[Depends(cookie)])
def update_project(project_id: str, response: Response, session_data: SessionData = Depends(verifier)):

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

# list project objects
@media.get('/project/list', dependencies=[Depends(cookie)])
def list_projects(session_data: SessionData = Depends(verifier)):

    # connect to db
    engine = create_engine(settings.DATABASE_URI)

    # get user id from session email
    stmt = select(Project.id, Project.name).join(User).where(User.email == session_data.email)
    with engine.connect() as conn:
        project_dbs = conn.execute(stmt)

    projects = []

    for project_db in project_dbs:

        project = {
            "name": getattr(project_db, "name"),
            "id": getattr(project_db, "id"),
            "media": []
        }

        stmt = select(Media.name, Media.id, Media.type).where(Media.project_id == getattr(project_db, "id"))
        with engine.connect() as conn:
            media_dbs = conn.execute(stmt)

        for media_db in media_dbs:

            project["media"].append(media_db._asdict())

        projects.append(project)

    return projects




    # get project ids
    stmt = select(Media.id, Media.name, Media.type, Media.project_id).join(Project, Project.id == Media.project_id, isouter=True).where(Project.user_id == user_id)
    with engine.connect() as conn:
        res = conn.execute(stmt)

         # initialize a dictionary to store projects and their media
        projects = {}

        # iterate through the query result
        for db_row in res:
            media_info = {
                "id": db_row.id,
                "name": db_row.name,
                "type": db_row.type
            }

            # if project already exists in the dictionary, append media to it
            if db_row.project_id in projects:
                projects[db_row.project_id]["media"].append(media_info)
            # if project doesn't exist, create a new entry
            else:
                projects[db_row.project_id] = {
                    "project_id": db_row.project_id,
                    "media": [media_info]
                }

        # convert the dictionary to a list of projects
        projects_list = list(projects.values())

    # return the projects objects!
    return projects_list

# get name and type for media_id
@media.get('/project/{project_id}/media/{media_id}', dependencies=[Depends(cookie)])
def get_media(project_id: str, media_id: str, response: Response, session_data: SessionData = Depends(verifier)):

    engine = create_engine(settings.DATABASE_URI)
    
    stmt = select(Media.name, Media.type).join(Project, Project.id == Media.project_id).join(User, User.id == Project.user_id).where(and_(Media.id == media_id, Media.project_id == project_id, User.email == session_data.email))
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
def create_media(response: Response, media_content: Annotated[bytes, File()], project_id: str, media_name: str = Body(embed=True), media_type: str  = Body(embed=True), session_data: SessionData = Depends(verifier)):

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
    media = Media(name=media_name, type=media_type, content=media_content, project_id=project_id)

    # add media object and update project object
    with Session(engine) as session:
        session.add(media)
        session.commit()
        session.refresh(media)
        media_id = media.id

    return media_id

# get video
@media.get('/project/{project_id}/video', dependencies=[Depends(cookie)])
def read_media(project_id: str, response: Response, session_data: SessionData = Depends(verifier)):

    # make sure session.email owns that media
    engine = create_engine(settings.DATABASE_URI)

    stmt = select(Media.content) \
        .join(Project, Project.id == Media.project_id) \
        .join(User, User.id == Project.user_id) \
        .where(and_(
            User.email == session_data.email, 
            Project.id == project_id, 
            Media.type == 'video',)
        )    
    with engine.connect() as conn:
        res = conn.execute(stmt).first()

    if res is None:
        response.status_code = 404
        return "Not Found"
   
    return Response(content=res[0], media_type="video/mp4")
        
# get transcript
@media.get('/project/{project_id}/transcript', dependencies=[Depends(cookie)])
def read_media(project_id: str, response: Response, session_data: SessionData = Depends(verifier)):

    # make sure session.email owns that media
    engine = create_engine(settings.DATABASE_URI)

    stmt = select(Media.content) \
        .join(Project, Project.id == Media.project_id) \
        .join(User, User.id == Project.user_id) \
        .where(and_(
            User.email == session_data.email, 
            Project.id == project_id, 
            Media.type == 'transcript',)
        )    
    with engine.connect() as conn:
        res = conn.execute(stmt).first()

    if res is None:
        response.status_code = 404
        return "Not Found"
   
    return Response(content=res[0], media_type="text/plain")

# get aisummary
@media.get('/project/{project_id}/aisummary', dependencies=[Depends(cookie)])
def read_media(project_id: str, response: Response, session_data: SessionData = Depends(verifier)):

    # make sure session.email owns that media
    engine = create_engine(settings.DATABASE_URI)

    stmt = select(Media.content) \
        .join(Project, Project.id == Media.project_id) \
        .join(User, User.id == Project.user_id) \
        .where(and_(
            User.email == session_data.email, 
            Project.id == project_id, 
            Media.type == 'aisummary',)
        )    
    with engine.connect() as conn:
        res = conn.execute(stmt).first()

    if res is None:
        response.status_code = 404
        return "Not Found"
   
    return Response(content=res[0], media_type="text/plain")

# get ai_audio
@media.get('/project/{project_id}/aiaudio', dependencies=[Depends(cookie)])
def read_media(project_id: str, response: Response, session_data: SessionData = Depends(verifier)):

    # make sure session.email owns that media
    engine = create_engine(settings.DATABASE_URI)

    stmt = select(Media.content) \
        .join(Project, Project.id == Media.project_id) \
        .join(User, User.id == Project.user_id) \
        .where(and_(
            User.email == session_data.email, 
            Project.id == project_id, 
            Media.type == 'aiaudio',)
        )    
    with engine.connect() as conn:
        res = conn.execute(stmt).first()

    if res is None:
        response.status_code = 404
        return "Not Found"
   
    return Response(content=res[0], media_type="audio/mp3")

# get ai_video
@media.get('/project/{project_id}/aivideo', dependencies=[Depends(cookie)])
def read_media(project_id: str, response: Response, session_data: SessionData = Depends(verifier)):

    # make sure session.email owns that media
    engine = create_engine(settings.DATABASE_URI)

    stmt = select(Media.content) \
        .join(Project, Project.id == Media.project_id) \
        .join(User, User.id == Project.user_id) \
        .where(and_(
            User.email == session_data.email, 
            Project.id == project_id, 
            Media.type == 'aivideo',)
        )    
    with engine.connect() as conn:
        res = conn.execute(stmt).first()

    if res is None:
        response.status_code = 404
        return "Not Found"
   
    return Response(content=res[0], media_type="video/mp4")

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
        session.commit()

        return 'ok'