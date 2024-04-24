#!/bin/bash

# COLMAP installation
sudo apt-get -y install git cmake ninja-build build-essential libboost-program-options-dev libboost-filesystem-dev libboost-graph-dev libboost-system-dev libeigen3-dev libflann-dev libfreeimage-dev libmetis-dev libgoogle-glog-dev libgtest-dev libsqlite3-dev libglew-dev qtbase5-dev libqt5opengl5-dev libcgal-dev libceres-dev
cd ~/KhachkarCrowdsourcingPage/mesh_generation/submodules/colmap
mkdir build
cd build
cmake .. -GNinja
ninja
sudo ninja install