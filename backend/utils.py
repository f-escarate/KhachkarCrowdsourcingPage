import glob, os, shutil
from datetime import datetime
from requests import Session
from schemas import Khachkar
import models

IMG_PATH = "./data/images"
VID_PATH = "./data/videos"
FRAMES_PATH = "./data/temp_frames"

def file_validation(file, extensions) -> str | None:
    """
        Returns the file extension, (if the file is valid).
    """
    parts = file.filename.split('.')
    extension =  parts[-1].lower()
    if extension in extensions:
        return extension
    return None

def img_validation(img) -> str | None:
    """
        Returns the image extension, (if the image is valid).
    """
    return file_validation(img, ['jpeg', 'jpg', 'bmp', 'png', 'webp'])

def video_validation(video) -> str | None:
    """
        Returns the video extension, (if the video is valid).
    """
    return file_validation(video, ['mp4', 'mov', 'avi', 'mkv', 'wmv'])

def save_file(file, path, id, extension):
    """
        Saves the file in its path.
    """
    # Remove the old image (if it exist)
    for file in glob.glob(str(id) + '.*'):
        os.remove(file)
    # Saves the image
    with open(f"{path}/{id}.{extension}", "wb+") as file_object:
        file_object.write(file.file.read())

def save_image(img, id, extension):
    """
        Saves the image in the photo's path.
    """
    save_file(img, IMG_PATH, id, extension)

def save_video(video, index, extension):
    """
        Saves the video in the video's path.
    """
    save_file(video, VID_PATH, f"{index}_temp", extension)

def save_mesh(mesh, khachkar: models.Khachkar, db: Session):
    # TODO: Save the mesh
    update_khachkar_status(db, khachkar, "meshed")

def read_file(id, path, extension):
    """
        Reads the file of the given id and path.
    """
    with open(f"{path}/{id}.{extension}", "rb") as file_object:
        return file_object.read()

def read_image(id, extension):
    """
        Reads the image of the given id.
    """
    return read_file(id, IMG_PATH, extension)

def read_video(id, extension):
    """
        Reads the video of the given id.
    """
    return read_file(id, VID_PATH, extension)

def preprocess_video(index, extension: str, db: Session, n_frames: int = 300):
    """
        Preprocesses the video in order to remove audio and keep 300 frames only.
        It uses ffmpeg
    """
    khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == index).first()
    update_khachkar_status(db, khachkar, "processing_video")
    id = f"{index}_temp"
    # Get video duration
    dur = os.system('ffprobe -i {VID_PATH}/{id}.{extension} -show_entries format=duration -v quiet -of csv="p=0"')
    fps = n_frames // dur + 1
    os.mkdir(f"{FRAMES_PATH}/{id}") # Create folder for frames
    # Generate images from video
    os.system(f"ffmpeg -i {VID_PATH}/{id}.{extension} -vf fps={fps} {FRAMES_PATH}/{id}/%06d.jpg")
    # Generate video from images
    os.system(f"ffmpeg -r {fps} -i {FRAMES_PATH}/{id}/%06d.jpg {VID_PATH}/{index}.mp4")
    shutil.rmtree(f"{FRAMES_PATH}/{id}")    # Remove the temporary frames
    os.remove(f"{VID_PATH}/{id}.{extension}")   # Remove the temporary video
    update_khachkar_status(db, khachkar, "not_meshed")

def create_khachkar(db: Session, khachkar: Khachkar, user_id: int):
    """
        Creates a Khackkar in the database.
    """
    khachkar_dict = khachkar.dict()
    khachkar_dict['date'] = datetime.now()
    db_khachkar = models.Khachkar(**khachkar_dict, owner_id=user_id)
    db.add(db_khachkar)
    db.commit()
    db.refresh(db_khachkar)
    return db_khachkar

def edit_khachkar(db: Session, db_khachkar: models.Khachkar, khachkar: Khachkar, img_file_extension: str, vid_file_extension: str):
    """
        Edits a Khackkar in the database.
    """
    db_khachkar.date = datetime.now()
    db_khachkar.image = img_file_extension
    db_khachkar.video = vid_file_extension
    db_khachkar.location = khachkar.location
    db_khachkar.latLong = khachkar.latLong
    db_khachkar.scenario = khachkar.scenario
    db_khachkar.setting = khachkar.setting
    db_khachkar.landscape = khachkar.landscape
    db_khachkar.accessibility = khachkar.accessibility
    db_khachkar.masters_name = khachkar.masters_name
    db_khachkar.category = khachkar.category
    db_khachkar.production_period = khachkar.production_period
    db_khachkar.motive = khachkar.motive
    db_khachkar.condition_of_preservation = khachkar.condition_of_preservation
    db_khachkar.inscription = khachkar.inscription
    db_khachkar.important_features = khachkar.important_features
    db_khachkar.backside = khachkar.backside
    db_khachkar.history_ownership = khachkar.history_ownership
    db_khachkar.commemorative_activities = khachkar.commemorative_activities
    db_khachkar.references = khachkar.references
    db.commit()



def update_khachkar_status(db: Session, db_khachkar: models.Khachkar, status: str):
    """
        Updates the status of the Khackkar in the database.
    """
    db_khachkar.state = status
    db.commit()