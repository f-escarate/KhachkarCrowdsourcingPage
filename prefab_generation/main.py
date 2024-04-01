from prefab_generation.media import video_to_photos, try_to_create_dir
from prefab_generation.gaussian_splatting import gSplatModel
from unity import call_method
from dotenv import load_dotenv
import os

load_dotenv()
VIDEOS_PATH = os.environ['VIDEOS_PATH']
COLMAPS_PATH = os.environ['COLMAPS_PATH']
GAUSSIANS_PATH = os.environ['GAUSSIANS_PATH']
MESHES_PATH = os.environ['MESHES_PATH']
UNITY_PATH = os.environ['UNITY_PATH']
PROJECT_PATH = os.environ['PROJECT_PATH']

g_splat = gSplatModel(GAUSSIANS_PATH, MESHES_PATH)

def video_to_asset(index, n_frames = 15):
    # Create name and folders
    name = f"{index}_{n_frames}F"
    colmap_path = os.path.join(COLMAPS_PATH, name)
    try_to_create_dir(colmap_path)
    images_path = os.path.join(colmap_path, "input")
    try_to_create_dir(images_path)
    # Get images from video
    video_to_photos(index, n_frames, VIDEOS_PATH, images_path)
    # Generate OBJ using Gaussian Splatting and SuGaR
    run_res = g_splat.run(name, colmap_path, remove_backgrounds=True)
    # Import the mesh to Unity
    #if run_res == 0:
    #    call_method("CallableMethods.ImportMesh", index)
    ## Generate asset
    #if run_res == 0:
    #    call_method("CallableMethods.GenerateAsset", index)
    #return