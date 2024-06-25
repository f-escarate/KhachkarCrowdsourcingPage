from typing import List
from fastapi import Depends, FastAPI, Response, BackgroundTasks, File, UploadFile, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException

from sqlalchemy.orm import Session

from schemas import ChangePassword, Khachkar, EditKhachkar, UserLogin, UserRegister, KhachkarMeshFiles, KhachkarMeshTransformations, Settings
from authentication import authenticate_user, get_password_hash, get_user_by_email, unauthorized_exception, verify_password
from utils import save_image, save_video, save_mesh, create_khachkar, edit_khachkar, read_image, read_video, read_file, img_validation, update_khachkar_status, update_khachkars_in_unity, video_validation, mesh_files_validation, preprocess_video, MESHES_PATH
from database import get_db, Base, engine, SessionLocal
from mesh_handling import get_mesh_from_video, call_method, scale_mesh, transform_mesh, crop_mesh, generate_text_asset
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

@AuthJWT.load_config
def get_config():
    return Settings()

@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "status": "error",
            "msg": "You are not authorized to perform this action (login first)",
            "details": exc.message
        }
    )

@app.post("/post_khachkar/{with_mesh}/")
async def post_khachkar(with_mesh: int, background_tasks: BackgroundTasks, Authorize: AuthJWT = Depends(), khachkar: Khachkar = Depends(Khachkar), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    email = Authorize.get_jwt_subject()
    user = get_user_by_email(email, db)
    if user is None:
        return {"status": "error", "msg": "problem with user authentication"}
    img_file_extension = img_validation(khachkar.image)
    if img_file_extension is None:
        return {"status": "error", "msg": "invalid image"}
    image = khachkar.image
    khachkar.image = img_file_extension
    if with_mesh:
        if len(khachkar.mesh_files) == 0:
            return {"status": "error", "msg": "not enough mesh files"}
        khachkar_mesh_files = KhachkarMeshFiles(obj = khachkar.mesh_files.pop(0), mtl = khachkar.mesh_files.pop(0), images = khachkar.mesh_files)
        if not mesh_files_validation(khachkar_mesh_files):
            return {"status": "error", "msg": "invalid mesh files"}
        khachkar.video = None
        created_khachkar = create_khachkar(db=db, khachkar=khachkar, user_id=user.id)
        if image.size > 0:
            save_image(image, created_khachkar.id, img_file_extension)
        save_mesh(khachkar_mesh_files, created_khachkar, db)
        scale_mesh(created_khachkar.id, created_khachkar.height)
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
async def get_my_khachkars(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    email = Authorize.get_jwt_subject()
    user = get_user_by_email(email, db)
    if user is None:
        return {"status": "error", "msg": "problem with user authentication"}
    khachkars = db.query(models.Khachkar).filter(models.Khachkar.owner_id == user.id).all()
    return khachkars

@app.get("/get_khachkars/ready/")
async def get_ready_khachkars(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    email = Authorize.get_jwt_subject()
    get_user_by_email(email, db)
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
async def get_options_list(Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return {
        "status": "success",
        "msg": {
            "location": [[location.value, location.name] for location in models.Location],
            "landscape": [[landscape.value, landscape.name] for landscape in models.Landscape],
            "accessibility": [[accessibility.value, accessibility.name] for accessibility in models.AccessibilityLevel],
            "condition_of_preservation": [[condition.value, condition.name] for condition in models.ConditionOfPreservation]
        }
    }

@app.get("/get_filters_options/")
async def get_filters_options():
    return {
        "status": "success",
        "msg": {
            "location": [location.value for location in models.Location],
            "state": [[state.value, state.get_label()] for state in models.KhachkarState]
        }
    }

@app.patch("/update_khachkar/{khachkar_id}/")
async def update_khachkar(khachkar_id: int, Authorize: AuthJWT = Depends(), khachkar: EditKhachkar = Depends(EditKhachkar), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    email = Authorize.get_jwt_subject()
    user = get_user_by_email(email, db)
    if user is None:
        return {"status": "error", "msg": "problem with user authentication"}
    db_khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == khachkar_id).first()
    if db_khachkar is None:
        return {"status": "error", "msg": "khachkar does not exist"}
    img_file_extension = img_validation(khachkar.image)
    if img_file_extension is None:
        return {"status": "error", "msg": "invalid image"}
    image = khachkar.image
    
    edit_khachkar(db, db_khachkar, khachkar, img_file_extension)
    if image.size > 0:
        save_image(image, db_khachkar.id, img_file_extension)
    return {"status": "success"}

@app.get("/get_image/{khachkar_id}")
async def get_image(khachkar_id: int, db: Session = Depends(get_db)):
    khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == khachkar_id).first()
    try:
        img = read_image(khachkar_id, khachkar.image)
        return Response(content=img, media_type=f"image/{khachkar.image}")
    except FileNotFoundError:
        return Response(content=None, status_code=404)

@app.get("/get_video/{khachkar_id}")
async def get_video(khachkar_id: int):
    video = read_video(khachkar_id, "mp4")
    return Response(content=video, media_type=f"video/mp4")

@app.get("/me/")
async def get_user(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    email = Authorize.get_jwt_subject()
    user = get_user_by_email(email, db)
    if user is None:
        raise unauthorized_exception("Could not validate credentials")
    return {
        "status": "success",
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin,
    }

@app.get("/get_user_id/")
async def get_user_id(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    email = Authorize.get_jwt_subject()
    user = get_user_by_email(email, db)
    if user is None:
        raise unauthorized_exception("Could not validate credentials")
    return {
        "status": "success",
        "user_id": user.id
    }

@app.post("/register/")
async def register(user: UserRegister = Depends(UserRegister), db: Session = Depends(get_db)):
    db_user = get_user_by_email(user.email, db)
    if db_user is not None:
        return {"status": "error", "msg": "an account with this email already exists"}
    if user.password != user.password2:
        return {"status": "error", "msg": "passwords do not match"}
    new_user = models.User(username=user.username, email=user.email, hashed_password=get_password_hash(user.password), is_admin=False)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"status": "success"}

@app.post("/login")
async def login_for_access_token(user: UserLogin = Depends(UserLogin), Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(user.email, user.password, db)
    if not user:
        raise unauthorized_exception("Incorrect username or password")
    access_token = Authorize.create_access_token(subject=user.email)
    refresh_token = Authorize.create_refresh_token(subject=user.email)
    return {
        "status": "success",
        "access_token": access_token,
        "refresh_token": refresh_token
    }

@app.post('/refresh/')
def refresh(Authorize: AuthJWT = Depends()):
    """
    The jwt_refresh_token_required() function insures a valid refresh
    token is present in the request before running any code below that function.
    we can use the get_jwt_subject() function to get the subject of the refresh
    token, and use the create_access_token() function again to make a new access token
    """
    Authorize.jwt_refresh_token_required()

    current_user = Authorize.get_jwt_subject()
    new_access_token = Authorize.create_access_token(subject=current_user)
    return {"status": "success", "access_token": new_access_token}

@app.patch("/change_password/")
async def change_password(Authorize: AuthJWT = Depends(), change: ChangePassword = Depends(ChangePassword), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    email = Authorize.get_jwt_subject()
    user = get_user_by_email(email, db)
    if user is None:
        return {"status": "error", "msg": "Problem with user authentication"}
    if not verify_password(change.old_pass, user.hashed_password):
        return {"status": "error", "msg": "Incorrect old password"}
    user.hashed_password = get_password_hash(change.new_pass)
    db.commit()
    return {"status": "success"}

@app.post("/compile_asset_bundles/")
async def compile_asset_bundles(khachkar_ids: List[int], Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    email = Authorize.get_jwt_subject()
    user = get_user_by_email(email, db)
    if user is None or not user.is_admin:
        return {"status": "error", "msg": "You are not authorized to perform this action"}
    print("Compiling asset bundles...")
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
async def mesh_khachkar(khachkar_id: int, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    print(f"Meshing khachkar {khachkar_id}")
    email = Authorize.get_jwt_subject()
    user = get_user_by_email(email, db)
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
    if vm_status["status"] == "running" and valdi_task.no_khachkars_meshing(db) and valdi_task.no_khachkars_queued(db):
        return get_mesh_from_video(khachkar, db)

    update_khachkar_status(db, khachkar, "queued_for_meshing")
    print("Gaussian Splatting server is not running, or is busy")
    return {"status": "success"}
        

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
    print("saved")
    print("transforming")
    transform_res = transform_mesh(khachkar_id, [0, 0, 0], [180, 0, 0])
    if transform_res["status"] == "error":
        return transform_res
    print("transformed")
    # Now scale the mesh based on the height of the khachkar
    height = db_khachkar.height
    return scale_mesh(khachkar_id, height)

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
def set_mesh_transformations(khachkar_id: int, transformations: KhachkarMeshTransformations, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    email = Authorize.get_jwt_subject()
    user = get_user_by_email(email, db)
    if user is None:
        return {"status": "error", "msg": "problem with user authentication"}
    db_khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == khachkar_id).first()
    if db_khachkar is None:
        return {"status": "error", "msg": "khachkar does not exist"}
    if db_khachkar.state != models.KhachkarState.meshed:
        return {"status": "error", "msg": "khachkar is not meshed"}
    print("Setting mesh transformations...")
    transform_res = transform_mesh(khachkar_id, transformations.pos, transformations.rot)
    if transform_res["status"] == "error":
        return transform_res
    # Update the khachkar's scale based on its height
    height = db.query(models.Khachkar).filter(models.Khachkar.id == khachkar_id).first().height
    return scale_mesh(khachkar_id, height)

@app.post("/crop_mesh/{khachkar_id}/")
def post_mesh_bounding_box(khachkar_id: int, bounding_box: List[float], Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    email = Authorize.get_jwt_subject()
    user = get_user_by_email(email, db)
    if user is None:
        return {"status": "error", "msg": "problem with user authentication"}
    db_khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == khachkar_id).first()
    if db_khachkar is None:
        return {"status": "error", "msg": "khachkar does not exist"}
    if db_khachkar.state != models.KhachkarState.meshed:
        return {"status": "error", "msg": "khachkar is not meshed"}
    print("Setting mesh bounding box...")
    crop_res = crop_mesh(khachkar_id, bounding_box)
    if crop_res["status"] == "error":
        return crop_res
    # Update the khachkar's scale based on its height
    height = db.query(models.Khachkar).filter(models.Khachkar.id == khachkar_id).first().height
    return scale_mesh(khachkar_id, height)

@app.get("/set_ready/{khachkar_id}/")
def set_ready(khachkar_id: int, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    email = Authorize.get_jwt_subject()
    user = get_user_by_email(email, db)
    if user is None:
        return {"status": "error", "msg": "problem with user authentication"}
    db_khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == khachkar_id).first()
    if db_khachkar is None:
        return {"status": "error", "msg": "khachkar does not exist"}
    # Check if has an image
    try:
        read_image(khachkar_id, db_khachkar.image)
    except FileNotFoundError:
        return {"status": "error", "msg": "khachkar does not have an image"}
    print("Setting khachkar ready...")
    db_khachkar.state = models.KhachkarState.ready
    db.commit()
    return {"status": "success"}

@app.get("/set_unready/{khachkar_id}/")
def set_unready(khachkar_id: int, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    email = Authorize.get_jwt_subject()
    user = get_user_by_email(email, db)
    if user is None:
        return {"status": "error", "msg": "problem with user authentication"}
    db_khachkar = db.query(models.Khachkar).filter(models.Khachkar.id == khachkar_id).first()
    if db_khachkar is None:
        return {"status": "error", "msg": "khachkar does not exist"}
    print("Setting khachkar unready...")
    db_khachkar.state = models.KhachkarState.meshed
    db.commit()
    return {"status": "success"}

@app.get("/get_server_status/")
def get_server_status(Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    Authorize.jwt_required()
    email = Authorize.get_jwt_subject()
    user = get_user_by_email(email, db)
    if user is None:
        return {"status": "error", "msg": "problem with user authentication"}
    if not user.is_admin:
        return {"status": "error", "msg": "you are not authorized to perform this action"}
    
    token = valdi_task.get_access_token()
    if token is None:
        return {"status": "valdi_error", "msg": "Valdi bad authentication error"}
    vm_status = valdi_task.get_is_vm_status_data(token)
    if vm_status is None:
        return {"status": "valdi_error", "msg": "Valdi server error"}

    response_obj = {
        "server_status": vm_status["status"],
        "last_restarted": vm_status["last_restarted_time"],
        "last_stopped": vm_status["last_stopped_time"],
        "gpu": vm_status["pretty_gpu_name"],
    }
    return {"status": "success", "msg": response_obj}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, root_path='/crowdsourcing_backend')