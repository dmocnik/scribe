# coding: utf-8
from sqlalchemy import Column, String
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class User(Base):
    __tablename__ = 'Users'
    __table_args__ = {'comment': 'Users table'}

    Users_PK = Column(INTEGER(11), primary_key=True)
    Email = Column(String(100), nullable=False)
    PasswordHash = Column(String(100), nullable=False)


class Employee(Base):
    __tablename__ = 'employee'

    id = Column(INTEGER(11), primary_key=True)
    firstname = Column(String(255))
    lastname = Column(String(255))
