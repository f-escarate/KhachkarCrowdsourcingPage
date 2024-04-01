import glob, os

from requests import Session
from schemas import Khachkar
import models

IMG_PATH = "./data/images"

def img_validation(img) -> str | None:
    """
        Returns the image extension, (if the image is valid).
    """
    parts = img.filename.split('.')
    extension =  parts[-1].lower()
    if extension in ['jpeg', 'jpg', 'bmp', 'png', 'webp']:
        return extension
    return None

def save_image(img, id, extension):
    """
        Saves the image in the photo's path.
    """
    # Remove the old image (if it exist)
    for file in glob.glob(str(id) + '.*'):
        os.remove(file)
    # Saves the image
    with open(f"{IMG_PATH}/{id}.{extension}", "wb+") as file_object:
        file_object.write(img.file.read())

def read_image(id, extension):
    """
        Reads the image of the given id.
    """
    with open(f"{IMG_PATH}/{id}.{extension}", "rb") as file_object:
        return file_object.read()

def create_khachkar(db: Session, khachkar: Khachkar, user_id: int):
    """
        Creates a Khackkar in the database.
    """
    db_khachkar = models.Khachkar(**khachkar.dict(), owner_id=user_id)
    db.add(db_khachkar)
    db.commit()
    db.refresh(db_khachkar)
    return db_khachkar
    