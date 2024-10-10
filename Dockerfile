FROM python:3.12.4

WORKDIR /fastapi_video_mi_app

# Copy the requirements file first and install dependencies
COPY requirements.txt .

# Command to install depedencies
RUN pip install -r requirements.txt --no-cache-dir

# copy project to working dir
COPY . /fastapi_video_mi_app