import os
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.
from fastapi import HTTPException,status,Depends
from functools import wraps
from fastapi.security import HTTPBasic, HTTPBasicCredentials

class Config:
    # SQLALCHEMY Configurations
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Redis Configurations
    REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")


class Development(Config):

    # SQLALCHEMY URL Configurations
    SQLALCHEMY_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL','postgresql://postgres:root@postgres:5432/fastapi_video_mi_db')

class Production(Config):
    pass

class Testing(Config):
    # SQLALCHEMY URL Configurations
    SQLALCHEMY_DATABASE_URL = os.getenv('sqlite:///video_mi_test_db')

def get_settings():
    env = os.getenv("APP_ENV", "development").lower()
    
    if env == "production":
        return Production()
    elif env == "testing":
        return Testing()
    else:  # defaults to development
        return Development()

settings = get_settings()


security = HTTPBasic()


def basic_auth_required(credentials: HTTPBasicCredentials = Depends(security)):

    # Get username and password from environment variables
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    
    if not ADMIN_USERNAME or not ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Please set ADMIN_USERNAME & ADMIN_PASSWORD in your .env file and restart the app.",
        )

    if credentials.username == ADMIN_USERNAME and credentials.password == ADMIN_PASSWORD:
        return True
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="You are not a Admin User!",
        headers={"WWW-Authenticate": "Basic"},
    )