import os, json, requests, trimesh, shutil
import numpy as np
from utils import save_file, update_khachkar_status
from models import Khachkar, MeshTransformations
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
    mesh_transformations = db.query(MeshTransformations).filter(MeshTransformations.khachkar_id == khachkar.id).first()
    data["assetProps"] = mesh_transformations.as_dict()
    json_data = json.dumps(data)
    save_file(json_data, f"{PROJECT_PATH}/Assets/StonesMetadata", khachkar.id, "json")

def call_method(method, args):
    command = '{0} -quit -batchmode -username "{1}" -password "{2}" -logFile {3} -projectPath {4} -executeMethod {5} {6}'
    command = command.format(UNITY_PATH, UNITY_USER, UNITY_PASSWORD, LOGFILE_PATH, PROJECT_PATH, method, args)
    return_code = os.system(command)
    if return_code != 0:
        return {"status": "error", "msg": "Error in Unity method call"}
    return {"status": "success"}

def transform_mesh(id:int, position: list, rotation: list, scale: float):
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

        # Translate the mesh
        translation = np.array(position) - mesh.centroid
        mesh.apply_translation(translation)

        # Scale the mesh
        mesh.apply_scale(scale)

        # Rotate the mesh
        rotation_matrix = trimesh.transformations.rotation_matrix(np.radians(rotation[0]), [1, 0, 0], mesh.centroid)
        mesh.apply_transform(rotation_matrix)
        rotation_matrix = trimesh.transformations.rotation_matrix(np.radians(rotation[1]), [0, 1, 0], mesh.centroid)
        mesh.apply_transform(rotation_matrix)
        rotation_matrix = trimesh.transformations.rotation_matrix(np.radians(rotation[2]), [0, 0, 1], mesh.centroid)
        mesh.apply_transform(rotation_matrix)

        # Save the rotated mesh
        mesh.export(f"{source_dir}/{id}.obj")
        # Remove the backup folder
        shutil.rmtree(backup_dir)
    except Exception as e:
        # Move the old mesh back
        for file_name in file_names:
            shutil.move(os.path.join(backup_dir, file_name), source_dir)
        return {"status": "error", "msg": str(e)}
    return {"status": "success"}

if __name__ == "__main__":
    call_method("CallableMethods.GenerateAsset")