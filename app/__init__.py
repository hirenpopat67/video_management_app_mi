from fastapi import FastAPI
from app.routes.routes import router
from app.configurations.database import create_tables


def create_app():

    app = FastAPI()

    create_tables()

    # Register your routes with the app
    app.include_router(router)

    return app