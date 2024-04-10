import os
from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from media import video_to_images, try_to_create_dir
from gaussian_splatting import generate_mesh
from dotenv import load_dotenv
load_dotenv()

VIDEOS_PATH = os.environ['VIDEOS_PATH']
COLMAPS_PATH = os.environ['COLMAPS_PATH']

app = FastAPI()

@app.post("/get_mesh_from_video/{index}/")
async def get_mesh_from_video(index: int, background_tasks: BackgroundTasks, video: UploadFile = File(...)):
    # Create name
    extension = 'mp4'
    print(f"Saving video {index}.{extension}")
    video_path = os.path.join(VIDEOS_PATH, f"{index}.{extension}")
    with open(video_path, "wb") as f:
        f.write(video.file.read())
    print("Creating directories...")
    colmap_path = os.path.join(COLMAPS_PATH, str(index))
    try_to_create_dir(colmap_path)
    images_path = os.path.join(colmap_path, "input")
    try_to_create_dir(images_path)

    try:
        print("Extracting images from video...")
        video_to_images(video_path, images_path)
    except Exception as e:
        return {"status": "error", "message": f"Error extracting images from video: {e}"}
    # Generate OBJ using Gaussian Splatting and Gaustudio
    background_tasks.add_task(generate_mesh, index, colmap_path)
    return {"status": "success", "message": "Mesh generation started in background"}