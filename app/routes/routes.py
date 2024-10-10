from fastapi import APIRouter,Depends,HTTPException,UploadFile,BackgroundTasks,Request,status
from fastapi.responses import JSONResponse
from app.configurations.config import settings
from app.configurations.database import SessionLocal
from sqlalchemy.orm import Session
import moviepy.editor as moviepy
import os
import uuid
import shutil
from app.configurations.config import basic_auth_required
from app.models.models import Video
import aiofiles
import redis

router = APIRouter()

redis_client = redis.StrictRedis.from_url(settings.REDIS_URL, decode_responses=True)

# Upload directory
UPLOAD_DIR = "uploads"
CONVERTED_DIR = "converted_videos"
# Create upload dir if not exists
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CONVERTED_DIR, exist_ok=True)

# Dependency that provides a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/")
async def index():
    return {"message": "Hello World"}


def convert_to_mp4(video_path: str, output_path: str):
    """Function to convert video to .mp4 using moviepy."""
    try:
        # Load the video file
        clip = moviepy.VideoFileClip(video_path)
        # Write the video to .mp4 format
        clip.write_videofile(output_path, codec="libx264")
        clip.close()

        # Optionally delete the original file to save space
        if os.path.exists(video_path):
            os.remove(video_path)

    except Exception as e:
        print(f"Video conversion failed: {e}")
        raise HTTPException(status_code=500, detail="Video conversion failed")
    

# Background task for video upload and conversion
async def handle_video_upload(file: UploadFile, background_tasks: BackgroundTasks,video_id : int):

    """Save a video file asynchronously and pass to convert_mp4 function to convert video into .mp4"""

    file_location = os.path.join(UPLOAD_DIR, file.filename)

    # Save uploaded video file asynchronously
    async with aiofiles.open(file_location, 'wb') as out_file:
        content = await file.read()  # Read file
        await out_file.write(content)  # Write file

    # Output file path for the converted video
    output_file = os.path.join(CONVERTED_DIR, f"{os.path.splitext(file.filename)[0]}.mp4")

    # Add video conversion to background tasks
    background_tasks.add_task(convert_to_mp4, file_location, output_file)

    return {"message": f"Video '{file.filename}' uploaded successfully with {video_id} ID. Conversion in progress."}

@router.post("/upload-videos")
async def upload_video(file: UploadFile, background_tasks: BackgroundTasks,request: Request,db: Session = Depends(get_db),authenticated: bool = Depends(basic_auth_required)):
    """
    API endpoint to upload a video and convert it to .mp4 in the background.
    """
    # Ensure the uploaded file is a video
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a video.")

    if not file.filename.lower().endswith(('mp4', 'avi', 'mov', 'mkv', 'flv')):
            raise HTTPException(status_code=400, detail="Invalid video format. Only mp4, avi, mov, mkv, and flv allowed.")
    
    check_video_exist = db.query(Video).filter(Video.file_name==file.filename,Video.file_size==file.size).first()

    if check_video_exist:
        return {"message": f"Video '{file.filename}' already exist. Please upload another one..."}

    add_video = Video(file_name=file.filename, file_size=file.size)
    db.add(add_video)
    db.commit()
    response = await handle_video_upload(file, background_tasks,add_video.id)
    return JSONResponse(content=response)


@router.get("/search-videos")
def search_videos(video_id: int = None, name: str = None, size: int = None, db: Session = Depends(get_db),authenticated: bool = Depends(basic_auth_required)):

    """Search the videos by name and file size (Byte). If any of the parameter is not provided all files will be returned"""

    query = db.query(Video)

    if video_id is not None:
        query = query.filter(Video.id == video_id)
    if name is not None:
        query = query.filter(Video.file_name.ilike(f"%{name}%"))  # Case-insensitive search
    if size is not None:
        query = query.filter(Video.file_size == size)

    results = query.all()
    return results

@router.post("/block-video/")
def block_video(video_id: int, db: Session = Depends(get_db),authenticated: bool = Depends(basic_auth_required)):

    """Add the video to Blocklist by its ID (Adding to redis server)"""

    video = db.query(Video).filter(Video.id == video_id).first()
    if video is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

    # Block the video by adding its ID to Redis
    redis_client.sadd("blocked_videos", video_id)
    return {"message": f"Video {video_id} has been blocked."}

@router.get("/download-video/{video_id}")
async def download_video(video_id: int, db: Session = Depends(get_db),authenticated: bool = Depends(basic_auth_required)):
    # Check if the video is in the block list in Redis
    if redis_client.sismember("blocked_videos", video_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This video is blocked and cannot be downloaded.")

    video = db.query(Video).filter(Video.id == video_id).first()
    if video is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

    file_path = os.path.join(CONVERTED_DIR, video.file_name)
    return {"message": f"Video download functionality will come soon...."}