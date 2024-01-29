import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base 

Base = declarative_base()

class Employee(Base):
    __tablename__ = 'employee'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    firstname = sqlalchemy.Column(sqlalchemy.String(length=255))
    lastname = sqlalchemy.Column(sqlalchemy.String(length=255))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}