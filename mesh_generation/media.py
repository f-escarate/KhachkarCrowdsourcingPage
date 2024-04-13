import os
import cv2
from sys import argv

def try_to_create_dir(path):
    try:
        os.mkdir(path)
    except FileExistsError:
        print(f"The directory {path} already exists")

def video_to_images(video_path: str, images_path: str) -> None:
    # Open the video
    vidcap = cv2.VideoCapture(video_path)
    # Get total number of frames
    total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Iterate through the video frames
    count = 0
    success = True
    while count < total_frames and success:
        vidcap.set(cv2.CAP_PROP_POS_FRAMES, count) # Set frame position
        success, image = vidcap.read()
        # Save the frame as an image file
        frame_filename = os.path.join(images_path, f"frame_{count:04d}.jpg")
        cv2.imwrite(frame_filename, image)
        count += 1

    vidcap.release()