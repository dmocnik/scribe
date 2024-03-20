from typing import List

from sqlalchemy import Column, DateTime, Enum, ForeignKeyConstraint, Index, String, text
from sqlalchemy.dialects.mysql import INTEGER, LONGBLOB, TINYINT
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship
from sqlalchemy.orm.base import Mapped

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = mapped_column(INTEGER(11), primary_key=True)
    email = mapped_column(String(64), nullable=False)
    password_hash = mapped_column(String(256), nullable=False)
    disabled = mapped_column(TINYINT(1), nullable=False, server_default=text('1'))
    name = mapped_column(String(30))

    codes: Mapped[List['Codes']] = relationship('Codes', uselist=True, back_populates='user')
    project: Mapped[List['Project']] = relationship('Project', uselist=True, back_populates='user')


class Codes(Base):
    __tablename__ = 'codes'
    __table_args__ = (
        ForeignKeyConstraint(['user_ID'], ['user.id'], name='codes_ibfk_1'),
        Index('user_ID', 'user_ID')
    )

    id = mapped_column(INTEGER(11), primary_key=True)
    user_ID = mapped_column(INTEGER(11), nullable=False)
    code_hash = mapped_column(String(256), nullable=False)
    code_expiry = mapped_column(DateTime, nullable=False)

    user: Mapped['User'] = relationship('User', back_populates='codes')


class Project(Base):
    __tablename__ = 'project'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['user.id'], name='project_user_FK'),
        Index('project_user_FK', 'user_id')
    )

    id = mapped_column(INTEGER(11), primary_key=True)
    name = mapped_column(String(64), nullable=False)
    user_id = mapped_column(INTEGER(11), nullable=False)

    user: Mapped['User'] = relationship('User', back_populates='project')
    media: Mapped[List['Media']] = relationship('Media', uselist=True, back_populates='project')


class Media(Base):
    __tablename__ = 'media'
    __table_args__ = (
        ForeignKeyConstraint(['project_id'], ['project.id'], name='media_project_FK'),
        Index('media_project_FK', 'project_id')
    )

    id = mapped_column(INTEGER(11), primary_key=True)
    name = mapped_column(String(64), nullable=False)
    type = mapped_column(Enum('video', 'transcript', 'aivideo', 'aiaudio', 'aisummary'), nullable=False)
    content = mapped_column(LONGBLOB, nullable=False)
    project_id = mapped_column(INTEGER(11), nullable=False)

    project: Mapped['Project'] = relationship('Project', back_populates='media')
