# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, String, text
from sqlalchemy.dialects.mysql import INTEGER, LONGBLOB, TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Media(Base):
    __tablename__ = 'media'

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(64), nullable=False)
    type = Column(String(20), nullable=False)
    content = Column(LONGBLOB, nullable=False)


class User(Base):
    __tablename__ = 'user'

    id = Column(INTEGER(11), primary_key=True)
    email = Column(String(64), nullable=False)
    password_hash = Column(String(256), nullable=False)
    name = Column(String(30))
    disabled = Column(TINYINT(1), nullable=False, server_default=text("1"))


class Codes(Base):
    __tablename__ = 'codes'

    id = Column(INTEGER(11), primary_key=True)
    user_ID = Column(ForeignKey('user.id'), nullable=False, index=True)
    code_hash = Column(String(256), nullable=False)
    code_expiry = Column(DateTime, nullable=False)

    user = relationship('User')


class Project(Base):
    __tablename__ = 'project'

    id = Column(INTEGER(11), primary_key=True)
    name = Column(String(64), nullable=False)
    video_id = Column(ForeignKey('user.id'), index=True)
    transcript_id = Column(ForeignKey('user.id'), index=True)
    aitranscript_id = Column(ForeignKey('user.id'), index=True)
    aisummary_id = Column(ForeignKey('user.id'), index=True)
    aiaudio_id = Column(ForeignKey('user.id'), index=True)
    aivideo_id = Column(ForeignKey('media.id'), index=True)

    aiaudio = relationship('User', primaryjoin='Project.aiaudio_id == User.id')
    aisummary = relationship('User', primaryjoin='Project.aisummary_id == User.id')
    aitranscript = relationship('User', primaryjoin='Project.aitranscript_id == User.id')
    aivideo = relationship('Media')
    transcript = relationship('User', primaryjoin='Project.transcript_id == User.id')
    video = relationship('User', primaryjoin='Project.video_id == User.id')
