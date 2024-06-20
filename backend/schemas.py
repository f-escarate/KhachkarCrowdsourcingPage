from fastapi import Form, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List

def form_body(cls):
    cls.__signature__ = cls.__signature__.replace(
        parameters=[
            arg.replace(default=Form(...) if arg.default is arg.empty else Form(arg.default))
            for arg in cls.__signature__.parameters.values()
        ]
    )
    return cls

# ================ Users schemas ================ #
@form_body
class UserRegister(BaseModel):
    username: str
    email: str
    password: str
    password2: str

class Token(BaseModel):
    access_token: str
    token_type: str
    
@form_body
class ChangePassword(BaseModel):
    old_pass: str
    new_pass: str


# ================ Khachkar schemas ================ #
    
@form_body
class Khachkar(BaseModel):
    location: Optional[str] = 'Unknown location'
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    height: Optional[float] = None
    landscape: Optional[str] = None
    accessibility: Optional[str] = None
    production_period: Optional[str] = None
    condition_of_preservation: Optional[str] = None
    inscription: Optional[str] = None
    important_features: Optional[str] = None
    references: Optional[str] = None
    image: Optional[UploadFile] = None
    video: Optional[UploadFile] = None
    mesh_files: List[UploadFile] = File(...)


class KhachkarMeshFiles(BaseModel):
    obj: UploadFile
    mtl: UploadFile
    images: List[UploadFile]

class KhachkarMeshTransformations(BaseModel):
    pos: List[float]
    rot: List[float]
    scale: float