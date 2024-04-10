#!/bin/bash

BASH_RC_LINES=$(awk 'END { print NR }' ~/.bashrc)

# CUDA installation
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-11-8

echo 'export PATH=/usr/local/cuda-11.8/bin${PATH:+:${PATH}}' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-11.8/lib64\{LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}' >> ~/.bashrc

# Miniconda installation
cd ~
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh

# For OpenCV
sudo apt-get install ffmpeg libsm6 libxext6  -y

# Reload bashrc for the nexts scripts
eval "$(cat ~/.bashrc | tail -n +$((BASH_RC_LINES+1)))"

cd ./installers
bash ./install_colmap.sh
bash ./install_gaustudio.sh
bash ./install_mvs_texturing.sh
bash ./install_gsplatting.sh
bash ./install_libraries.sh

exit 0