#!/bin/bash
source ~/.profile

source ~/miniconda3/etc/profile.d/conda.sh
conda activate venv
cd ~/KhachkarCrowdsourcingPage/mesh_generation/
nohup python3 "main.py" > "log" 2>&1 &
echo $! > "save_pid.txt"