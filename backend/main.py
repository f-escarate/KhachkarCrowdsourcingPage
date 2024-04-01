from datetime import timedelta
from typing import Annotated
from fastapi import Depends, FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from schemas import ChangePassword, Khachkar, UserRegister
from authentication import authenticate_user, create_access_token, get_password_hash, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, get_user_by_name, unauthorized_exception, verify_password
from utils import save_image, save_video, create_khachkar, read_image, img_validation, video_validation
from database import get_db, Base, engine
import models

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:8000",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/post_khachkar/")
async def post_khachkar(token: Annotated[str, Depends(oauth2_scheme)], khachkar: Khachkar = Depends(Khachkar), db: Session = Depends(get_db)):
    if not token:
        return unauthorized_exception("Invalid token")
    user = get_user_by_name(jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub"), db)
    if user is None:
        return {"status": "error", "msg": "problem with user authentication"}
    img_file_extension = img_validation(khachkar.image)
    if img_file_extension is None:
        return {"status": "error", "msg": "invalid image"}
    vid_file_extension = video_validation(khachkar.video)
    if vid_file_extension is None:
        return {"status": "error", "msg": "invalid video"}
        
    image = khachkar.image
    video = khachkar.video
    khachkar.image = img_file_extension
    khachkar.video = vid_file_extension
    created_khachkar = create_khachkar(db=db, khachkar=khachkar, user_id=user.id)
    save_image(image, created_khachkar.id, img_file_extension)
    save_video(video, created_khachkar.id, vid_file_extension)
    return {"status": "success"}

@app.get("/get_khachkars/")
async def get_khachkars(db: Session = Depends(get_db)):
    khachkars = db.query(models.Khachkar).all()
    return khachkars

@app.get("/get_khachkars/own/")
async def get_my_khachkars(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    if not token:
        return unauthorized_exception("Invalid token")
    user = get_user_by_name(jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub"), db)
    if user is None:
        return {"status": "error", "msg": "problem with user authentication"}
    khachkars = db.query(models.Khachkar).filter(models.Khachkar.owner_id == user.id).all()
    return khachkars

@app.get("/get_khachkar/{khachkar_id}/")
async def get_khachkar(khachkar_id: int, db: Session = Depends(get_db)):
    khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == khachkar_id).first()
    return khachkar

@app.patch("/update_khachkar/{khachkar_id}/")
async def update_khachkar(token: Annotated[str, Depends(oauth2_scheme)], khachkar_id: int, khachkar: Khachkar = Depends(Khachkar), db: Session = Depends(get_db)):
    if not token:
        return unauthorized_exception("Invalid token")
    user = get_user_by_name(jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub"), db)
    if user is None:
        return {"status": "error", "msg": "problem with user authentication"}
    db_khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == khachkar_id).first()
    if db_khachkar is None:
        return {"status": "error", "msg": "khachkar does not exist"}
    if db_khachkar.owner_id != user.id:
        return {"status": "error", "msg": "you are not the owner of this khachkar"}
    img_file_extension = img_validation(khachkar.image)
    if img_file_extension is None:
        return {"status": "error", "msg": "invalid image"}
    vid_file_extension = video_validation(khachkar.video)
    if vid_file_extension is None:
        return {"status": "error", "msg": "invalid video"}
    db_khachkar.date = khachkar.date
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
    save_image(khachkar.image, khachkar_id, img_file_extension)
    save_video(khachkar.video, khachkar_id, vid_file_extension)
    return {"status": "success"}

@app.get("/get_image/{khachkar_id}")
async def get_image(khachkar_id: int, db: Session = Depends(get_db)):
    khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == khachkar_id).first()
    img = read_image(khachkar_id, khachkar.image)
    return Response(content=img, media_type=f"image/{khachkar.image}")

@app.get("/me/")
async def get_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    credentials_exception = unauthorized_exception("Could not validate credentials")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_name(username, db)
    if user is None:
        raise credentials_exception
    return {
        "status": "success",
        "username": user.username,
        "email": user.email
    }

@app.post("/register/")
async def register(user: UserRegister = Depends(UserRegister), db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user is not None:
        return {"status": "error", "msg": "username already exists"}
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user is not None:
        return {"status": "error", "msg": "an account with this email already exists"}
    if user.password != user.password2:
        return {"status": "error", "msg": "passwords do not match"}
    new_user = models.User(username=user.username, email=user.email, hashed_password=get_password_hash(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status": "success"}

@app.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise unauthorized_exception("Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {
        "status": "success",
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.patch("/change_password/")
async def change_password(token: Annotated[str, Depends(oauth2_scheme)], change: ChangePassword = Depends(ChangePassword), db: Session = Depends(get_db)):
    if not token:
        return unauthorized_exception("Invalid token")
    user = get_user_by_name(jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub"), db)
    if user is None:
        return {"status": "error", "msg": "Problem with user authentication"}
    if not verify_password(change.old_pass, user.hashed_password):
        return {"status": "error", "msg": "Incorrect old password"}
    user.hashed_password = get_password_hash(change.new_pass)
    db.commit()
    return {"status": "success"}

app.mount("/", StaticFiles(directory="static",html = True), name="static")