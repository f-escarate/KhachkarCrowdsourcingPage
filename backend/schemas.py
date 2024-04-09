from fastapi import Form, UploadFile
from pydantic import BaseModel
from typing import Optional

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
    latLong: Optional[str] = None
    scenario: Optional[str] = None
    setting: Optional[str] = None
    landscape: Optional[str] = None
    accessibility: Optional[str] = None
    masters_name: Optional[str] = None
    category: Optional[str] = None
    production_period: Optional[str] = None
    motive: Optional[str] = None
    condition_of_preservation: Optional[str] = None
    inscription: Optional[str] = None
    important_features: Optional[str] = None
    backside: Optional[str] = None
    history_ownership: Optional[str] = None
    commemorative_activities: Optional[str] = None
    references: Optional[str] = None
    image: Optional[UploadFile] = None
    video: UploadFile
