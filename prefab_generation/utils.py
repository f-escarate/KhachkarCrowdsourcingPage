import os, requests
from rembg import remove
from dotenv import load_dotenv
load_dotenv()

MESHES_PATH = os.environ['MESHES_PATH']
HANDLE_ERROR_ENDPOINT = os.environ['HANDLE_ERROR_ENDPOINT']
HANDLE_SUCCESS_ENDPOINT = os.environ['HANDLE_SUCCESS_ENDPOINT']

def remove_background(photo, in_path, out_path):
    photo_path = os.path.join(in_path, photo)
    output_path = os.path.join(out_path, photo)
    
    with open(photo_path, 'rb') as i:
        with open(output_path, 'wb') as o:
            input = i.read()
            output = remove(input)
            o.write(output)

def handle_error_in_mesh_creation(index: int):
    print(f"Handling error in mesh creation for Khachkar #{index}")
    response = requests.get(f"{HANDLE_ERROR_ENDPOINT}{index}/")
    if response.status_code != 200:
        print(f"Error handling error in mesh creation for index {index}")
    # TODO: Remove the files and folders created for this index

def handle_successful_mesh_creation(index: int):
    files_in_dir = os.listdir(f"{MESHES_PATH}/{index}")
    textures = filter(lambda img: img.endswith(('.png')), files_in_dir)
    files = {
        'obj': open(f"{MESHES_PATH}/{index}/textured_mesh.obj", 'rb'),
        'mtl': open(f"{MESHES_PATH}/{index}/textured_mesh.mtl", 'rb'),
        'images': [
            open(f"{MESHES_PATH}/{index}/{img}", 'rb') for img in textures
        ]
    }
    response = requests.post(f"{HANDLE_SUCCESS_ENDPOINT}{index}/", files=files)
    if response.status_code != 200:
        print(f"Error handling successful mesh creation for index {index}")
    # TODO: Remove the files and folders created for this index
