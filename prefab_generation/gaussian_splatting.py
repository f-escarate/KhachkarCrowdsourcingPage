import os
from utils import remove_background
from dotenv import load_dotenv
load_dotenv()

GAUSSIAN_SPLATTING_PATH = os.environ['GAUSSIAN_SPLATTING_PATH']
GAUSSIANS_PATH = os.environ['GAUSSIANS_PATH']
MESHES_PATH = os.environ['MESHES_PATH']

def remove_backgrounds(colmap_path):
    photos = os.listdir(os.path.join(colmap_path, "input"))
    cleaned_path = os.path.join(colmap_path, "images")
    os.mkdir(cleaned_path)
    for photo in photos:
        remove_background(photo, colmap_path, cleaned_path)

def generate_mesh(index: int, colmap_path: str, remove_backgrounds: bool = True):
    convert_res = os.system(f'python {GAUSSIAN_SPLATTING_PATH}/convert.py -s {colmap_path}')
    if convert_res != 0:
        print("COLMAP Error")
        return 1
    if remove_backgrounds:
        remove_backgrounds(colmap_path)
    train_res = os.system(f'python {GAUSSIAN_SPLATTING_PATH}/train.py -s {colmap_path} --iterations 7000 --model_path {GAUSSIANS_PATH}/{index}')
    if train_res != 0:
        print("Training Gaussians Error")
        return 2
    # Generate the mesh using gaustudio
    gaustudio_res = os.system(f'gs-extract-mesh -m {GAUSSIANS_PATH}/{index} -o {MESHES_PATH}/{index}')
    if gaustudio_res != 0:
        print("Gaustudio Error")
        return 3
    # Bind the texture using mvs-texturing
    mvs_res = os.system(f'cd {MESHES_PATH}/{index} && texrecon ./images ./fused_mesh.ply ./textured_mesh --outlier_removal=gauss_clamping --data_term=area --no_intermediate_results')
    if mvs_res != 0:
        print("MVS Texturing Error")
        return 4
    return 0
