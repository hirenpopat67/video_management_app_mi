from sqlalchemy import  Column, Integer,Text,DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# class Users(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True)
#     first_name = Column(Text)
#     last_name = Column(Text)
#     user_name = Column(Text)
#     is_admin =Column(Boolean,default=False)
#     password = Column(Text)

class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True)
    file_name = Column(Text)
    file_size = Column(Integer)
    uploaded_at = Column(DateTime,default=datetime.now())
    