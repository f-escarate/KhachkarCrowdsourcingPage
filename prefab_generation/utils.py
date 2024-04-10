import os, requests
from rembg import remove
from dotenv import load_dotenv
load_dotenv()

HANDLE_ERROR_ENDPOINT = os.environ['HANDLE_ERROR_ENDPOINT']

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
