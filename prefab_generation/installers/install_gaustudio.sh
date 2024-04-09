# Conda env
conda create -n venv python=3.8
conda activate venv
# Install gaustudio and libraries
cd ~
git clone https://github.com/GAP-LAB-CUHK-SZ/gaustudio.git
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
cd gaustudio
pip install -r requirements.txt
cd submodules/gaustudio-diff-gaussian-rasterization
python setup.py install
cd ../../
python setup.py develop