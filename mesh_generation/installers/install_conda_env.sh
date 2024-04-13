# Conda env
conda init
conda create -n venv python=3.8
source ~/miniconda3/etc/profile.d/conda.sh
conda activate venv
python --version

# clone repositories
cd ~
git clone https://github.com/GAP-LAB-CUHK-SZ/gaustudio.git
git clone https://github.com/graphdeco-inria/gaussian-splatting --recursive

# Install gaustudio and libraries
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
cd ~/gaustudio
pip install -r requirements.txt
cd submodules/gaustudio-diff-gaussian-rasterization
python setup.py install
cd ../../
python setup.py develop

# Install Gaussian Splatting libraries
cd ~/gaussian-splatting/submodules/diff-gaussian-rasterization/
pip install -e .
cd ~/gaussian-splatting/submodules/simple-knn/
pip install -e .

# Install remaining libraries
pip install opencv-python
pip install rembg
pip install python-dotenv
pip install "fastapi[all]"