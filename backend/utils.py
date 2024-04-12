import glob, os
from datetime import datetime
from requests import Session
from schemas import Khachkar, KhachkarMeshFiles
import models

IMG_PATH = "./data/images"
VID_PATH = "./data/videos"
FRAMES_PATH = "./data/temp_frames"
MESHES_PATH = "./data/meshes"

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

def mesh_files_validation(mesh_files: KhachkarMeshFiles) -> bool:
    """
        Returns True if the mesh files are valid.
    """
    ret = file_validation(mesh_files.obj, ['obj']) and file_validation(mesh_files.mtl, ['mtl'])
    for img in mesh_files.images:
        ret = ret and img_validation(img)
    return ret

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

def save_mesh(mesh_files: KhachkarMeshFiles, khachkar: models.Khachkar, db: Session):
    path = f"{MESHES_PATH}/{khachkar.id}"
    os.mkdir(path) # Create folder for mesh
    save_file(mesh_files.obj, path, khachkar.id, 'obj')
    save_file(mesh_files.mtl, path, mesh_files.mtl.filename.split(".")[0], 'mtl')
    for img in mesh_files.images:
        name, extension = img.filename.split(".")
        save_file(img, path, name, extension)
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

def preprocess_video(index, extension: str, db: Session, n_frames: int = 300, out_secs: int = 3):
    """
        Preprocesses the video in order to remove audio and keep 'n_frames' frames only.
        It uses ffmpeg
        out_secs: the duration of the output video in seconds
    """
    khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == index).first()
    update_khachkar_status(db, khachkar, "processing_video")
    temp_video = f'{VID_PATH}/{index}_temp.{extension}'
    # get video duration in seconds to get the scale factor
    dur = float(os.popen(f'ffprobe -i {temp_video} -show_entries format=duration -v quiet -of csv="p=0"').read())
    out_secs_factor: float = out_secs / dur
    # Generate smaller video
    fps: int = n_frames // out_secs
    os.system(f'ffmpeg -i {temp_video} -an -hide_banner -loglevel error -vf "setpts={out_secs_factor}*PTS, fps={fps}" -t {out_secs} {VID_PATH}/{index}.mp4')
    os.remove(f"{temp_video}")   # Remove the temporary video
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