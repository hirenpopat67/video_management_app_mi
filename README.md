# Video Management MI

## Description

- A Dockerized Python FastAPI video management app with the [PostgreSQL](https://www.postgresql.org/),  and [Redis](https://redis.io/), enabled.

- The Admin user can upload the videos(Video upload and converting to .mp4 process will be asynchronous), Search the video by its name or size, and Add a video to the blocklist.

We have configured the Python FastAPI app with the connection of [PostgreSQL](https://www.postgresql.org/). In this app, we are using [Redis](https://redis.io/) service for caching mechanism.

## Initial requirements

- [Docker](https://docs.docker.com/engine/install/) And [Docker-Compose](https://docs.docker.com/compose/install/)

## Starting the setup

### Step 1
- Open your terminal and Clone the repository, type: `git clone` HTTPS OR SSH URL
### Step 2
- Navigate to your app directory, Create a `.env` file inside your app directory and **Copy the below lines and Add the following environment variables to the `.env` file:**

#App Config

SQLALCHEMY_DATABASE_URL=

APP_ENV=development

#development [Development]

#testing [Testing]

ADMIN_USERNAME=

ADMIN_PASSWORD=

REDIS_URL=redis://redis:6379/0

#PostgreSQL Config

POSTGRES_DB=

POSTGRES_USER=

POSTGRES_PASSWORD=

#PGAdmin Creds

PGADMIN_EMAIL=

PGADMIN_PASSWORD=

### Step 3
- Fill the .env file variables and start the setup, type: `docker compose up --build`

## Access Application

- As described in the `docker-compose.yml` file, Python FastAPI app HTTP server is reachable via port 8000 and redis service is running on 6379 port, On the Docker host [Try](http://localhost:8000/).

## Note

- Without the .env file the setup won't be run and make sure to add environment variables with values in the .env file