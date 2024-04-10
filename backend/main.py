from datetime import timedelta
from typing import Annotated
from fastapi import Depends, FastAPI, Response, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from schemas import ChangePassword, Khachkar, UserRegister, KhachkarMeshFiles
from authentication import authenticate_user, create_access_token, get_password_hash, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, get_user_by_name, unauthorized_exception, verify_password
from utils import save_image, save_video, save_mesh, create_khachkar, edit_khachkar, read_image, read_video, img_validation, video_validation, mesh_files_validation, preprocess_video
from database import get_db, Base, engine
from mesh_handling import get_mesh_from_video, call_method
import models
import uvicorn

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/post_khachkar/{with_mesh}/")
async def post_khachkar(with_mesh: int, background_tasks: BackgroundTasks, token: Annotated[str, Depends(oauth2_scheme)], khachkar: Khachkar = Depends(Khachkar), db: Session = Depends(get_db)):
    if not token:
        return unauthorized_exception("Invalid token")
    user = get_user_by_name(jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub"), db)
    if user is None:
        return {"status": "error", "msg": "problem with user authentication"}
    img_file_extension = img_validation(khachkar.image)
    if img_file_extension is None:
        return {"status": "error", "msg": "invalid image"}
    image = khachkar.image
    khachkar.image = img_file_extension
    if with_mesh:
        # TODO manage mesh file(s)
        created_khachkar = create_khachkar(db=db, khachkar=khachkar, user_id=user.id)
        save_image(image, created_khachkar.id, img_file_extension)
        background_tasks.add_task(save_mesh, video, created_khachkar, db)
    else:
        vid_file_extension = video_validation(khachkar.video)
        if vid_file_extension is None:
            return {"status": "error", "msg": "invalid video"}
        video = khachkar.video
        khachkar.video = vid_file_extension
        created_khachkar = create_khachkar(db=db, khachkar=khachkar, user_id=user.id)
        save_image(image, created_khachkar.id, img_file_extension)
        save_video(video, created_khachkar.id, vid_file_extension)
        background_tasks.add_task(preprocess_video, created_khachkar.id, vid_file_extension, db, n_frames=300)
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

@app.get("/get_khachkars/mesh/")
async def get_my_khachkars(db: Session = Depends(get_db)):
    # TODO: Filter khachkars by the ones that have mesh data
    khachkars = db.query(models.Khachkar).all()
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
    edit_khachkar(db, db_khachkar, khachkar, img_file_extension, vid_file_extension)
    save_image(khachkar.image, khachkar_id, img_file_extension)
    # TODO: Save mesh file(s)
    save_video(khachkar.video, khachkar_id, vid_file_extension)
    return {"status": "success"}

@app.get("/get_image/{khachkar_id}")
async def get_image(khachkar_id: int, db: Session = Depends(get_db)):
    khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == khachkar_id).first()
    img = read_image(khachkar_id, khachkar.image)
    return Response(content=img, media_type=f"image/{khachkar.image}")

@app.get("/get_video/{khachkar_id}")
async def get_video(khachkar_id: int, db: Session = Depends(get_db)):
    khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == khachkar_id).first()
    video = read_video(khachkar_id, khachkar.video)
    return Response(content=video, media_type=f"video/{khachkar.video}")

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
        "email": user.email,
        "is_admin": user.is_admin,
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
    new_user = models.User(username=user.username, email=user.email, hashed_password=get_password_hash(user.password), is_admin=False)
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

@app.get("/compile_asset_bundles/")
async def compile_asset_bundles(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    print("Compiling asset bundles...")
    if not token:
        return unauthorized_exception("Invalid token")
    user = get_user_by_name(jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub"), db)
    if user is None or not user.is_admin:
        return {"status": "error", "msg": "You are not authorized to perform this action"}
    call_method("CallableMethods.GenerateAsset", "PLACEHOLDER")
    return {"status": "success"}

@app.get("/mesh_khachkar/{khachkar_id}/")
async def mesh_khachkar(token: Annotated[str, Depends(oauth2_scheme)], khachkar_id: int, db: Session = Depends(get_db)):
    print(f"Meshing khachkar {khachkar_id}")
    if not token:
        return unauthorized_exception("Invalid token")
    user = get_user_by_name(jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]).get("sub"), db)
    if user is None:
        return {"status": "error", "msg": "problem with user authentication"}
    khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == khachkar_id).first()
    if khachkar is None:
        return {"status": "error", "msg": "khachkar does not exist"}
    if khachkar.owner_id != user.id and not user.is_admin:
        return {"status": "error", "msg": "you are not the owner of this khachkar"}
    response = get_mesh_from_video(khachkar, db)
    return response

@app.post("/mesh_khachkar/{khachkar_id}/")
async def post_khachkar_mesh(khachkar_id: int, mesh_files: KhachkarMeshFiles = Depends(KhachkarMeshFiles), db: Session = Depends(get_db)):
    db_khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == khachkar_id).first()
    if db_khachkar is None:
        return {"status": "error", "msg": "khachkar does not exist"}
    if db_khachkar.state != models.KhachkarState.creating_mesh:
        return {"status": "error", "msg": "khachkar is not in the meshing process"}
    if not mesh_files.obj or not mesh_files.mtl or not mesh_files.images or len(mesh_files.images) == 0:
        return {"status": "error", "msg": "missing mesh files"}
    if not mesh_files_validation(mesh_files):
        return {"status": "error", "msg": "invalid mesh files"}
    save_mesh(mesh_files, db_khachkar, db)
    return {"status": "success"}

@app.get("/creating_mesh_error/{khachkar_id}/")
def creating_mesh_error(khachkar_id: int, db: Session = Depends(get_db)):
    db_khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == khachkar_id).first()
    if db_khachkar is None:
        return {"status": "error", "msg": "khachkar does not exist"}
    if db_khachkar.state != models.KhachkarState.creating_mesh:
        return {"status": "error", "msg": "khachkar is not in the meshing process"}
    db_khachkar.state = models.KhachkarState.not_meshed
    db.commit()
    return {"status": "success"}
    

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, root_path='/crowdsourcing_backend')