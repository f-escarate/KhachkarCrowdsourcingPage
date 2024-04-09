# Conda env
conda activate venv
# Clone Gaussian Splatting and install requirements
cd ~
git clone https://github.com/graphdeco-inria/gaussian-splatting.git
cd gaussian-splatting
conda env update --file environment.yml --prune