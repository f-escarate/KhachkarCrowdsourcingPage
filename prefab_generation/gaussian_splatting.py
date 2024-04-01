import os
from utils import remove_background

class gSplatModel():
    def __init__(self, gaussians_path, meshes_path):
        self.gaussians_path = gaussians_path
        self.meshes_path = meshes_path
    
    def remove_backgrounds(self, colmap_path):
        photos = os.listdir(os.path.join(colmap_path, "input"))
        cleaned_path = os.path.join(colmap_path, "images")
        os.mkdir(cleaned_path)
        for photo in photos:
            remove_background(photo, colmap_path, cleaned_path)

    def run(self, name, colmap_path, remove_backgrounds = False):
        convert_res = os.system(f'python ./gaussian-splatting/convert.py -s {colmap_path}')
        if convert_res != 0:
            print("Error al usar COLMAP")
            return 1
        if remove_backgrounds:
            self.remove_backgrounds(colmap_path)
        train_res = os.system(f'python ./gaussian-splatting/train.py -s {colmap_path} --iterations 7000 --model_path {self.gaussians_path}/{name}')
        if train_res != 0:
            print("Error al entrenar")
            return 2
        # Transform the gaussian splatting to mesh using sugar
        self.gen_obj(name)
        return 0
    
    def gen_obj(self, index, frames = 15):
        colmap_path = f"./output/{index}_15F"
        gaussion_splatting_path = f"./output/{index}_15F"
        os.system(f'python ./gaussian-splatting/gen_obj.py -s ./output/{name} -o ./output/{name}.obj')
