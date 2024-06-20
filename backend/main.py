from datetime import timedelta
from typing import Annotated, List
from fastapi import Depends, FastAPI, Response, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session

from schemas import ChangePassword, Khachkar, UserRegister, KhachkarMeshFiles, KhachkarMeshTransformations
from authentication import authenticate_user, create_access_token, get_password_hash, get_name_by_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_user_by_name, unauthorized_exception, verify_password
from utils import save_image, save_video, save_mesh, create_khachkar, edit_khachkar, read_image, read_video, read_file, img_validation, update_khachkars_in_unity, video_validation, mesh_files_validation, preprocess_video, MESHES_PATH, queue_khahckar_for_meshing
from database import get_db, Base, engine, SessionLocal
from mesh_handling import get_mesh_from_video, call_method, transform_mesh, crop_mesh, generate_text_asset
from valdi import ValdiTask
from contextlib import asynccontextmanager
import models, os, asyncio

Base.metadata.create_all(bind=engine)

# Runs the ValdiTask in the background to check the status of the Gaussian Splatting server and start it when is needed
valdi_task = ValdiTask()
@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(valdi_task.try_to_call_gsplatting_server(SessionLocal()))
    yield

app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)
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
    user = get_user_by_name(get_name_by_token(token), db)
    if user is None:
        return {"status": "error", "msg": "problem with user authentication"}
    img_file_extension = img_validation(khachkar.image)
    if img_file_extension is None:
        return {"status": "error", "msg": "invalid image"}
    image = khachkar.image
    khachkar.image = img_file_extension
    if with_mesh:
        if len(khachkar.mesh_files) <= 3:
            return {"status": "error", "msg": "not enough mesh files"}
        khachkar_mesh_files = KhachkarMeshFiles(obj = khachkar.mesh_files.pop(0), mtl = khachkar.mesh_files.pop(0), images = khachkar.mesh_files)
        if not mesh_files_validation(khachkar_mesh_files):
            return {"status": "error", "msg": "invalid mesh files"}
        khachkar.video = 'mp4'
        created_khachkar = create_khachkar(db=db, khachkar=khachkar, user_id=user.id)
        save_image(image, created_khachkar.id, img_file_extension)
        save_mesh(khachkar_mesh_files, created_khachkar, db)
    else:
        vid_file_extension = video_validation(khachkar.video)
        if vid_file_extension is None:
            return {"status": "error", "msg": "invalid video"}
        video = khachkar.video
        khachkar.video = vid_file_extension
        created_khachkar = create_khachkar(db=db, khachkar=khachkar, user_id=user.id)
        if image.size > 0:
            save_image(image, created_khachkar.id, img_file_extension)
        save_video(video, created_khachkar.id, vid_file_extension)
        background_tasks.add_task(preprocess_video, created_khachkar.id, vid_file_extension, db, n_frames=100, get_thumbnail=image.size == 0)
    return {"status": "success"}

@app.get("/get_khachkars/")
async def get_khachkars(db: Session = Depends(get_db)):
    khachkars = db.query(models.Khachkar).all()
    return khachkars

@app.get("/get_khachkars/own/")
async def get_my_khachkars(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    if not token:
        return unauthorized_exception("Invalid token")
    user = get_user_by_name(get_name_by_token(token), db)
    if user is None:
        return {"status": "error", "msg": "problem with user authentication"}
    khachkars = db.query(models.Khachkar).filter(models.Khachkar.owner_id == user.id).all()
    return khachkars

@app.get("/get_khachkars/ready/")
async def get_ready_khachkars(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    khachkars = db.query(models.Khachkar).filter(models.Khachkar.state == models.KhachkarState.ready).all()
    return khachkars

@app.get("/get_khachkar/{khachkar_id}/")
async def get_khachkar(khachkar_id: int, db: Session = Depends(get_db)):
    khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == khachkar_id).first()
    return khachkar

@app.get("/get_khachkar/with_enums/{khachkar_id}/")
async def get_khachkar(khachkar_id: int, db: Session = Depends(get_db)):
    khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == khachkar_id).first()
    khachkar.accessibility = list(models.AccessibilityLevel).index(khachkar.accessibility)
    khachkar.condition_of_preservation = list(models.ConditionOfPreservation).index(khachkar.condition_of_preservation)
    khachkar.landscape = list(models.Landscape).index(khachkar.landscape)
    khachkar.location = list(models.Location).index(khachkar.location)
    return khachkar

@app.get("/get_options_list/")
async def get_options_list(token: Annotated[str, Depends(oauth2_scheme)]):
    if not token:
        return {"status": "error", "msg": "You are not authorized to perform this action (login first)"}
    return {
        "status": "success",
        "msg": {
            "location": [[location.value, location.name] for location in models.Location],
            "landscape": [[landscape.value, landscape.name] for landscape in models.Landscape],
            "accessibility": [[accessibility.value, accessibility.name] for accessibility in models.AccessibilityLevel],
            "condition_of_preservation": [[condition.value, condition.name] for condition in models.ConditionOfPreservation]
        }
    }

@app.patch("/update_khachkar/{khachkar_id}/{with_mesh}/")
async def update_khachkar(token: Annotated[str, Depends(oauth2_scheme)], khachkar_id: int, with_mesh: int, background_tasks: BackgroundTasks, khachkar: Khachkar = Depends(Khachkar), db: Session = Depends(get_db)):
    if not token:
        return unauthorized_exception("Invalid token")
    user = get_user_by_name(get_name_by_token(token), db)
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
    image = khachkar.image
    
    if with_mesh:
        if len(khachkar.mesh_files) <= 3:
            return {"status": "error", "msg": "not enough mesh files"}
        khachkar_mesh_files = KhachkarMeshFiles(obj = khachkar.mesh_files.pop(0), mtl = khachkar.mesh_files.pop(0), images = khachkar.mesh_files)
        if not mesh_files_validation(khachkar_mesh_files):
            return {"status": "error", "msg": "invalid mesh files"}
        edit_khachkar(db, db_khachkar, khachkar, img_file_extension, 'mp4')
        save_image(image, db_khachkar.id, img_file_extension)
        save_mesh(khachkar_mesh_files, db_khachkar, db)
    else:
        vid_file_extension = video_validation(khachkar.video)
        if vid_file_extension is None:
            return {"status": "error", "msg": "invalid video"}
        video = khachkar.video
        khachkar.video = vid_file_extension
        edit_khachkar(db, db_khachkar, khachkar, img_file_extension, vid_file_extension)
        if image.size > 0:
            save_image(image, db_khachkar.id, img_file_extension)
        save_video(video, db_khachkar.id, vid_file_extension)
        background_tasks.add_task(preprocess_video, db_khachkar.id, vid_file_extension, db, n_frames=100, get_thumbnail=image.size == 0)
    return {"status": "success"}

@app.get("/get_image/{khachkar_id}")
async def get_image(khachkar_id: int, db: Session = Depends(get_db)):
    khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == khachkar_id).first()
    img = read_image(khachkar_id, khachkar.image)
    return Response(content=img, media_type=f"image/{khachkar.image}")

@app.get("/get_video/{khachkar_id}")
async def get_video(khachkar_id: int):
    video = read_video(khachkar_id, "mp4")
    return Response(content=video, media_type=f"video/mp4")

@app.get("/me/")
async def get_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    user = get_user_by_name(get_name_by_token(token), db)
    if user is None:
        raise unauthorized_exception("Could not validate credentials")
    return {
        "status": "success",
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
    }

@app.get("/get_user_id/")
async def get_user_id(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
    user = get_user_by_name(get_name_by_token(token), db)
    if user is None:
        raise unauthorized_exception("Could not validate credentials")
    return {
        "status": "success",
        "user_id": user.id
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
    user = get_user_by_name(get_name_by_token(token), db)
    if user is None:
        return {"status": "error", "msg": "Problem with user authentication"}
    if not verify_password(change.old_pass, user.hashed_password):
        return {"status": "error", "msg": "Incorrect old password"}
    user.hashed_password = get_password_hash(change.new_pass)
    db.commit()
    return {"status": "success"}

@app.post("/compile_asset_bundles/")
async def compile_asset_bundles(token: Annotated[str, Depends(oauth2_scheme)], khachkar_ids: List[int], db: Session = Depends(get_db)):
    print("Compiling asset bundles...")
    if not token:
        return unauthorized_exception("Invalid token")
    user = get_user_by_name(get_name_by_token(token), db)
    if user is None or not user.is_admin:
        return {"status": "error", "msg": "You are not authorized to perform this action"}
    for id in khachkar_ids:
        khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == id).first()
        generate_text_asset(khachkar, db)
    args = " ".join([str(id) for id in khachkar_ids])
    args = f"{len(khachkar_ids)} {args}"
    response = call_method("CallableMethods.generateAssetBundles", args)
    update_khachkars_in_unity(db, khachkar_ids)
    return response

@app.get("/get_khachkars_in_unity/")
async def get_khachkars_in_unity(db: Session = Depends(get_db)):
    khachkars = [x.khachkar_id for x in db.query(models.KhachkarInUnity).all()]
    return {"status": "success", "khachkars": khachkars}

@app.get("/mesh_khachkar/{khachkar_id}/")
async def mesh_khachkar(token: Annotated[str, Depends(oauth2_scheme)], khachkar_id: int, db: Session = Depends(get_db)):
    print(f"Meshing khachkar {khachkar_id}")
    if not token:
        return unauthorized_exception("Invalid token")
    user = get_user_by_name(get_name_by_token(token), db)
    if user is None:
        return {"status": "error", "msg": "problem with user authentication"}
    khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == khachkar_id).first()
    if khachkar is None:
        return {"status": "error", "msg": "khachkar does not exist"}
    if khachkar.owner_id != user.id and not user.is_admin:
        return {"status": "error", "msg": "you are not the owner of this khachkar"}
    
    # Check if the Valdi server is running
    token = valdi_task.get_access_token()
    if token is None:
        return {"status": "error", "msg": "Gaussian Splatting server connection error 1"}
    vm_status = valdi_task.get_is_vm_status_data(token)
    if vm_status is None:
        return {"status": "error", "msg": "Gaussian Splatting server server connection error 2"}
    if vm_status["status"] != "running":
        queue_khahckar_for_meshing(khachkar_id, db)
        print("Gaussian Splatting server is not running, but the khachkar will be meshed when it starts")
        return {"status": "success"}
    response = get_mesh_from_video(khachkar, db)
    return response

@app.post("/mesh_khachkar/{khachkar_id}/")
async def post_khachkar_mesh(khachkar_id: int, mesh_files: List[UploadFile] = File(...), db: Session = Depends(get_db)):
    db_khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == khachkar_id).first()
    if db_khachkar is None:
        return {"status": "error", "msg": "khachkar does not exist"}
    if db_khachkar.state != models.KhachkarState.creating_mesh:
        return {"status": "error", "msg": "khachkar is not in the meshing process"}
    if len(mesh_files) <= 3:
        return {"status": "error", "msg": "not enough mesh files"}
    khachkar_mesh_files = KhachkarMeshFiles(obj = mesh_files.pop(0), mtl = mesh_files.pop(0), images = mesh_files)
    if not mesh_files_validation(khachkar_mesh_files):
        return {"status": "error", "msg": "invalid mesh files"}
    save_mesh(khachkar_mesh_files, db_khachkar, db)
    transform_mesh(khachkar_id, [0, 0, 0], [180, 0, 0], 3)
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

@app.get("/get_mtl/{id}/")
def get_mtl(id: int, db: Session = Depends(get_db)):
    khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == id).first()
    if khachkar is None:
        return {"status": "error", "msg": "khachkar does not exist"}
    # Search for the mtl file
    file_names = os.listdir(f"{MESHES_PATH}/{id}")
    for file_name in file_names:
        if file_name.endswith(".mtl"):
            splitted_name = file_name.split(".")
            name, extension = "".join(splitted_name[:-1]), splitted_name[-1]
            mtl = read_file(name, f"{MESHES_PATH}/{id}", extension)
            return Response(content=mtl)
    return {"status": "error", "msg": "mtl file not found"}

@app.get("/get_mtl/{id}/{img}")
def get_mtl(id: int, img: str, db: Session = Depends(get_db)):
    khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == id).first()
    if khachkar is None:
        return {"status": "error", "msg": "khachkar does not exist"}
    splitted_name = img.split(".")
    name, extension = "".join(splitted_name[:-1]), splitted_name[-1]
    image = read_file(name, f"{MESHES_PATH}/{id}", extension)
    return Response(content=image)
    

@app.get("/get_obj/{id}")
def get_obj(id: int, db: Session = Depends(get_db)):
    khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == id).first()
    if khachkar is None:
        return {"status": "error", "msg": "khachkar does not exist"}
    obj = read_file(id, f"{MESHES_PATH}/{id}", "obj")
    return Response(content=obj)

@app.post("/set_mesh_transformations/{khachkar_id}/")
def set_mesh_transformations(token: Annotated[str, Depends(oauth2_scheme)], khachkar_id: int, transformations: KhachkarMeshTransformations, db: Session = Depends(get_db)):
    if not token:
        return unauthorized_exception("Invalid token")
    user = get_user_by_name(get_name_by_token(token), db)
    if user is None:
        return {"status": "error", "msg": "problem with user authentication"}
    db_khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == khachkar_id).first()
    if db_khachkar is None:
        return {"status": "error", "msg": "khachkar does not exist"}
    if db_khachkar.state != models.KhachkarState.meshed:
        return {"status": "error", "msg": "khachkar is not meshed"}
    print("Setting mesh transformations...")
    return transform_mesh(khachkar_id, transformations.pos, transformations.rot, transformations.scale)

@app.post("/crop_mesh/{khachkar_id}/")
def post_mesh_bounding_box(token: Annotated[str, Depends(oauth2_scheme)], khachkar_id: int, bounding_box: List[float], db: Session = Depends(get_db)):
    if not token:
        return unauthorized_exception("Invalid token")
    user = get_user_by_name(get_name_by_token(token), db)
    if user is None:
        return {"status": "error", "msg": "problem with user authentication"}
    db_khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == khachkar_id).first()
    if db_khachkar is None:
        return {"status": "error", "msg": "khachkar does not exist"}
    if db_khachkar.state != models.KhachkarState.meshed:
        return {"status": "error", "msg": "khachkar is not meshed"}
    print("Setting mesh bounding box...")
    return crop_mesh(khachkar_id, bounding_box)

@app.get("/set_ready/{khachkar_id}/")
def set_ready(token: Annotated[str, Depends(oauth2_scheme)], khachkar_id: int, db: Session = Depends(get_db)):
    if not token:
        return unauthorized_exception("Invalid token")
    user = get_user_by_name(get_name_by_token(token), db)
    if user is None:
        return {"status": "error", "msg": "problem with user authentication"}
    db_khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == khachkar_id).first()
    if db_khachkar is None:
        return {"status": "error", "msg": "khachkar does not exist"}
    print("Setting khachkar ready...")
    db_khachkar.state = models.KhachkarState.ready
    db.commit()
    return {"status": "success"}

@app.get("/set_unready/{khachkar_id}/")
def set_unready(token: Annotated[str, Depends(oauth2_scheme)], khachkar_id: int, db: Session = Depends(get_db)):
    if not token:
        return unauthorized_exception("Invalid token")
    user = get_user_by_name(get_name_by_token(token), db)
    if user is None:
        return {"status": "error", "msg": "problem with user authentication"}
    db_khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == khachkar_id).first()
    if db_khachkar is None:
        return {"status": "error", "msg": "khachkar does not exist"}
    print("Setting khachkar unready...")
    db_khachkar.state = models.KhachkarState.meshed
    db.commit()
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, root_path='/crowdsourcing_backend')