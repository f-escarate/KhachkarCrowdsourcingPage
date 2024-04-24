#!/bin/bash

sudo apt install libpng-dev libjpeg-dev libtiff-dev libtbb-dev
cd ~/KhachkarCrowdsourcingPage/mesh_generation/submodules/mvs-texturing
mkdir build && cd build && cmake ..
make -j
echo 'export PATH="~/KhachkarCrowdsourcingPage/mesh_generation/submodules/mvs-texturing/build/apps/texrecon:$PATH"' >> ~/.bashrc