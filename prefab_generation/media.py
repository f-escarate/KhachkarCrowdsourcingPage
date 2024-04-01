import os
import cv2
from sys import argv
from gaussian_splatting import gSplatModel

def try_to_create_dir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        print(f"The directory {path} already exists")

def video_to_photos_ffmpeg(input, output_path, qscale=1, qmin=1, fps=2):
    # Creating the output directory
    path = os.path.join(output_path, input.split(".")[0])
    try_to_create_dir(path)
    imgs_path = os.path.join(path, "input")
    try_to_create_dir(imgs_path)
    os.system(f"ffmpeg -i videos\{input} -qscale:v {qscale} -qmin {qmin} -vf fps={fps} {imgs_path}\%04d.jpg")
    return path

def video_to_photos(index: int, n_frames: int, video_path: str, images_path: str) -> None:
    extension = 'mp4' # The extension should be get from the database
    # Open the video
    vidcap = cv2.VideoCapture(f"{video_path}\{index}.{extension}")
    # Get total number of frames
    total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    # Calculate spacing between frames
    frame_spacing = max(total_frames // n_frames, 1)
    
    # Iterate through the video frames
    count = 0
    success = True
    while count < total_frames and success:
        vidcap.set(cv2.CAP_PROP_POS_FRAMES, count) # Set frame position
        success, image = vidcap.read()
        if count % frame_spacing == 0:
            # Save the frame as an image file
            frame_filename = os.path.join(images_path, f"frame_{count:04d}.jpg")
            cv2.imwrite(frame_filename, image)
        
        count += frame_spacing

    vidcap.release()