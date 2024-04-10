import os
from utils import remove_background, handle_error_in_mesh_creation
from dotenv import load_dotenv
load_dotenv()

GAUSSIAN_SPLATTING_PATH = os.environ['GAUSSIAN_SPLATTING_PATH']
GAUSSIANS_PATH = os.environ['GAUSSIANS_PATH']
MESHES_PATH = os.environ['MESHES_PATH']

def remove_images_backgrounds(index, colmap_path):
    try:
        photos = os.listdir(os.path.join(colmap_path, "input"))
        cleaned_path = os.path.join(colmap_path, "images")
        os.mkdir(cleaned_path)
        for photo in photos:
            remove_background(photo, colmap_path, cleaned_path)
    except Exception as e:
        print(f"Error removing background: {e}")
        handle_error_in_mesh_creation(index)

def generate_mesh(index: int, colmap_path: str, remove_backgrounds: bool = True):
    convert_res = os.system(f'python {GAUSSIAN_SPLATTING_PATH}/convert.py -s {colmap_path}')
    if convert_res != 0:
        print("COLMAP Error")
        handle_error_in_mesh_creation(index)
        return
    if remove_backgrounds:
        remove_images_backgrounds(index, colmap_path)
    train_res = os.system(f'python {GAUSSIAN_SPLATTING_PATH}/train.py -s {colmap_path} --iterations 7000 --model_path {GAUSSIANS_PATH}/{index}')
    if train_res != 0:
        print("Training Gaussians Error")
        handle_error_in_mesh_creation(index)
        return
    # Generate the mesh using gaustudio
    gaustudio_res = os.system(f'gs-extract-mesh -m {GAUSSIANS_PATH}/{index} -o {MESHES_PATH}/{index}')
    if gaustudio_res != 0:
        print("Gaustudio Error")
        handle_error_in_mesh_creation(index)
        return
    # Bind the texture using mvs-texturing
    mvs_res = os.system(f'cd {MESHES_PATH}/{index} && texrecon ./images ./fused_mesh.ply ./textured_mesh --outlier_removal=gauss_clamping --data_term=area --no_intermediate_results')
    if mvs_res != 0:
        print("MVS Texturing Error")
        handle_error_in_mesh_creation(index)
        return
    return 0
