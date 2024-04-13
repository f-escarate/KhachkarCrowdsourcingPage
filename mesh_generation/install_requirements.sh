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
LAST_BASH_RC_LINES=$(cat ~/.bashrc | tail -n +$((BASH_RC_LINES+1)))
eval "$LAST_BASH_RC_LINES"

cd ~/prefab_generation/installers
chmod 777 *
./install_colmap.sh
./install_mvs_texturing.sh
./install_conda_env.sh

exit 0