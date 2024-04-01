import datetime
from fastapi import Form, UploadFile
from pydantic import BaseModel


def form_body(cls):
    cls.__signature__ = cls.__signature__.replace(
        parameters=[
            arg.replace(default=Form(...))
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
    location: str
    latLong: str
    scenario: str
    setting: str
    landscape: str
    accessibility: str
    masters_name: str
    category: str
    production_period: str
    motive: str
    condition_of_preservation: str
    inscription: str
    important_features: str
    backside: str
    history_ownership: str
    commemorative_activities: str
    references: str
    date: datetime.date
    image: UploadFile
    video: UploadFile
