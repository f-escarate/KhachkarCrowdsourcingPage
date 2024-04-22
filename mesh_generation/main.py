import os
from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from media import video_to_images, try_to_create_dir
from utils import handle_error_in_mesh_creation
from gaussian_splatting import generate_mesh
from dotenv import load_dotenv
load_dotenv()

VIDEOS_PATH = os.environ['VIDEOS_PATH']
COLMAPS_PATH = os.environ['COLMAPS_PATH']

app = FastAPI()

queue = []
meshing = False

@app.post("/get_mesh_from_video/{index}/")
async def get_mesh_from_video(index: int, background_tasks: BackgroundTasks, video: UploadFile = File(...)):
    # Create name
    extension = 'mp4'
    print(f"Saving video {index}.{extension}")
    video_path = os.path.join(VIDEOS_PATH, f"{index}.{extension}")
    with open(video_path, "wb") as f:
        f.write(video.file.read())
    background_tasks.add_task(video_to_mesh, index, video_path)
    return {"status": "success", "message": "Queued for mesh generation"}

def video_to_mesh(index: int, video_path: str):
    global meshing
    try:
        print("Creating directories...")
        colmap_path = os.path.join(COLMAPS_PATH, str(index))
        try_to_create_dir(colmap_path)
        images_path = os.path.join(colmap_path, "input")
        try_to_create_dir(images_path)
        print("Extracting images from video...")
        video_to_images(video_path, images_path)
    except Exception as e:
        print(f"Error extracting images from video: {e}")
        handle_error_in_mesh_creation(index)
        return
    if meshing:
        queue.append((index, colmap_path))
        return
    # Generate OBJ using Gaussian Splatting and Gaustudio
    meshing = True
    generate_mesh(index, colmap_path)
    while len(queue) > 0:
        next_index, next_colmap_path = queue.pop(0)
        generate_mesh(next_index, next_colmap_path)
    meshing = False

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)