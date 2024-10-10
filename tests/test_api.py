from app.models.models import Video
import pytest
from app.routes.routes import get_db
from app.configurations.config import settings
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from runserver import app
from base64 import b64encode
import io

engine = create_engine(settings.SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    """Create a new database session for each test."""
    # Override the session to use the testing session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def client(db):
    # Dependency override to use the testing database
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as client:
        yield client

@pytest.fixture
def auth_header():
    username = "hiren"  # Replace with your test username
    password = "1234"  # Replace with your test password
    credentials = f"{username}:{password}"
    b64_credentials = b64encode(credentials.encode()).decode("utf-8")
    return {"Authorization": f"Basic {b64_credentials}"}

def test_upload_video(client, db,auth_header):

    # Create a dummy video file-like object in memory
    video_content = io.BytesIO(b"dummy video content")
    video_content.name = "test_video.mp4"
    video_file = open("test_video.mp4", "rb")  # Add a valid video file path for testing
    response = client.post("/upload-videos", files={"file": video_file})
    assert response.status_code == 200
    assert "message" in response.json()

    # Test invalid file type
    response_invalid = client.post("/upload-videos", files={"file": ("test.txt", b"content")})
    assert response_invalid.status_code == 400

    video_file.close()


def test_search_videos(client, db,auth_header):
    # Add a test video to the database for searching
    new_video = Video(file_name="sample_video.mp4", file_size=123456)
    db.add(new_video)
    db.commit()
    
    response = client.get("/search-videos", params={"name": "sample"})
    assert response.status_code == 200
    assert len(response.json()) > 0  # Check if any video is returned

    # Test search by non-existent video_id
    response_no_video = client.get("/search-videos", params={"video_id": 999})
    assert response_no_video.status_code == 200
    assert len(response_no_video.json()) == 0  # No videos should be found


def test_block_video(client, db,auth_header):
    new_video = Video(file_name="test_video.mp4", file_size=123456)
    db.add(new_video)
    db.commit()

    # Block the video
    response = client.post(f"/block-video/?video_id={new_video.id}")
    assert response.status_code == 200
    assert "Video" in response.json()["message"]

    # Test blocking a non-existent video
    response_no_video = client.post(f"/block-video/?video_id={999}")
    assert response_no_video.status_code == 404


def test_download_video(client, db,auth_header):
    new_video = Video(file_name="test_video.mp4", file_size=123456)
    db.add(new_video)
    db.commit()

    # Attempt to download a non-blocked video
    response = client.get(f"/download-video/{new_video.id}")
    assert response.status_code == 200
    assert "message" in response.json()

    # Block the video and try to download again
    client.post("/block-video/", json={"video_id": new_video.id})
    response_blocked = client.get(f"/download-video/{new_video.id}")
    assert response_blocked.status_code == 403
    assert "This video is blocked" in response_blocked.json()["detail"]