# Conda env
conda init
conda create -n venv python=3.8
source ~/miniconda3/etc/profile.d/conda.sh
conda activate venv
python --version

# Install gaustudio and libraries
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
cd ~/mesh_generation/submodules/gaustudio
pip install -r requirements.txt
cd submodules/gaustudio-diff-gaussian-rasterization
python setup.py install
cd ../../
python setup.py develop

# Install Gaussian Splatting libraries
cd ~/mesh_generation/submodules/gaussian-splatting/submodules/diff-gaussian-rasterization/
pip install -e .
cd ~/mesh_generation/submodules/gaussian-splatting/submodules/simple-knn/
pip install -e .

# Install remaining libraries
pip install opencv-python
pip install rembg
pip install python-dotenv
pip install "fastapi[all]"