import os, json, requests, trimesh, shutil
import numpy as np
from utils import update_khachkar_status
from models import Khachkar
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()
UNITY_PATH = os.getenv("UNITY_PATH")
LOGFILE_PATH = os.getenv("LOGFILE_PATH")
PROJECT_PATH = os.getenv("PROJECT_PATH")
UNITY_USER = os.getenv("UNITY_USER")
UNITY_PASSWORD = os.getenv("UNITY_PASSWORD")
MESH_TO_VIDEO_ENDPOINT = os.getenv("MESH_TO_VIDEO_ENDPOINT")
MESHES_PATH = os.getenv("MESHES_PATH")
IMAGES_PATH = os.getenv("IMAGES_PATH")
METADATA_PATH = os.getenv("METADATA_PATH")

def get_mesh_from_video(khachkar: Khachkar, db: Session):
    try:
        index = khachkar.id
        video_path = open(f"data/videos/{index}.mp4", "rb")
        response = requests.post(f"{MESH_TO_VIDEO_ENDPOINT}{index}/", files={"video": video_path})
        
        if response.status_code == 200:
            res = response.json()
            update_khachkar_status(db, khachkar, "creating_mesh")
            return res
        return {"status": "error", "msg": "Gaussian Splatting's server error"}
    except requests.exceptions.ConnectionError as e:
        return {"status": "error", "msg": "Error connecting to Gaussian Splatting server"}

def generate_text_asset(khachkar: Khachkar, db: Session):
    data = khachkar.as_dict()
    # Get the mesh transformations
    #mesh_transformations = db.query(MeshTransformations).filter(MeshTransformations.khachkar_id == khachkar.id).first()
    #data["assetProps"] = mesh_transformations.as_dict()
    json_data = json.dumps(data)
    path = os.path.join(METADATA_PATH, f"Stone{khachkar.id}.json")
    # Save the json file
    with open(path, "w") as file:
        file.write(json_data)

def call_method(method, args):
    virtual_display_command =  'xvfb-run --auto-servernum --server-args="-screen 0 640x480x24:32"'
    command = '{0} -quit -batchmode -username "{1}" -password "{2}" -logFile {3} -projectPath {4} -executeMethod {5} {6}'
    command = command.format(UNITY_PATH, UNITY_USER, UNITY_PASSWORD, LOGFILE_PATH, PROJECT_PATH, method, args)
    return_code = os.system(f'{virtual_display_command} {command}')
    if return_code != 0:
        return {"status": "error", "msg": "Error in Unity method call"}
    return {"status": "success"}

def transform_mesh(id:int, position: list, rotation: list):
    try:
        # Move old mesh to a backup folder
        source_dir = f"{MESHES_PATH}/{id}"
        file_names = os.listdir(source_dir)
        backup_dir = f"{MESHES_PATH}/{id}/backup"
        os.makedirs(backup_dir, exist_ok=True)

        for file_name in file_names:
            shutil.move(os.path.join(source_dir, file_name), backup_dir)
        # Load the mesh
        mesh = trimesh.load_mesh(f"{backup_dir}/{id}.obj")
        # Rotate the mesh
        rot_x_mat = trimesh.transformations.rotation_matrix(np.radians(rotation[0]), [1, 0, 0])
        rot_y_mat = trimesh.transformations.rotation_matrix(np.radians(rotation[1]), [0, 1, 0])
        rot_z_mat = trimesh.transformations.rotation_matrix(np.radians(rotation[2]), [0, 0, 1])
        mesh.apply_transform(trimesh.transformations.concatenate_matrices(rot_x_mat, rot_y_mat, rot_z_mat))
        # Translate the mesh
        mesh.apply_translation(np.array(position))
        # Save the transformed mesh
        mesh.export(f"{source_dir}/{id}.obj")
        # Remove the backup folder
        shutil.rmtree(backup_dir)
    except Exception as e:
        # Move the old mesh back
        print(e)
        for file_name in file_names:
            shutil.move(os.path.join(backup_dir, file_name), source_dir)
        return {"status": "error", "msg": str(e)}
    return {"status": "success"}

def scale_mesh(id: int, height: float):
    UNITY_SCALE_RATIO = 2.99 # The ratio of the height of the mesh in Unity to the real height
    try:
        # Move old mesh to a backup folder
        source_dir = f"{MESHES_PATH}/{id}"
        file_names = os.listdir(source_dir)
        backup_dir = f"{MESHES_PATH}/{id}/backup"
        os.makedirs(backup_dir, exist_ok=True)

        for file_name in file_names:
            shutil.move(os.path.join(source_dir, file_name), backup_dir)
        # Load the mesh
        mesh = trimesh.load(f"{backup_dir}/{id}.obj", force="mesh")
        
        # Scale the mesh based on the height
        objective_height = height * UNITY_SCALE_RATIO
        scale = objective_height / mesh.bounding_box_oriented.primitive.extents[1]
        mesh.apply_scale(scale)

        # Save the scaled mesh
        mesh.export(f"{source_dir}/{id}.obj")
        # Remove the backup folder
        shutil.rmtree(backup_dir)
    except Exception as e:
        # Move the old mesh back
        print(e)
        for file_name in file_names:
            shutil.move(os.path.join(backup_dir, file_name), source_dir)
        return {"status": "error", "msg": str(e)}
    return {"status": "success"}

def crop_mesh(id: int, bounding_box: list):
    try:
        # Move old mesh to a backup folder
        source_dir = f"{MESHES_PATH}/{id}"
        file_names = os.listdir(source_dir)
        backup_dir = f"{MESHES_PATH}/{id}/backup"
        os.makedirs(backup_dir, exist_ok=True)

        for file_name in file_names:
            shutil.move(os.path.join(source_dir, file_name), backup_dir)
        # Load the mesh
        mesh = trimesh.load(f"{backup_dir}/{id}.obj", force="mesh")

        box = trimesh.primitives.Box(np.array(bounding_box))
        box.apply_translation(np.array([0, bounding_box[1]/2, 0]))
        mesh = mesh.slice_plane(box.facets_origin, -box.facets_normal)
        # Save the cropped mesh
        mesh.export(f"{source_dir}/{id}.obj")
        # Remove the backup folder
        shutil.rmtree(backup_dir)
    except Exception as e:
        # Move the old mesh back
        print(e)
        for file_name in file_names:
            shutil.move(os.path.join(backup_dir, file_name), source_dir)
        return {"status": "error", "msg": str(e)}
    return {"status": "success"}

if __name__ == "__main__":
    call_method("CallableMethods.GenerateAsset")