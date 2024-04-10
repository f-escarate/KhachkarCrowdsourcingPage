#!/bin/bash

sudo apt install libpng-dev libjpeg-dev libtiff-dev libtbb-dev
cd ~
git clone https://github.com/nmoehrle/mvs-texturing.git
cd mvs-texturing
mkdir build && cd build && cmake ..
make -j
echo 'export PATH="/home/user/mvs-texturing/build/apps/texrecon:$PATH"' >> ~/.bashrc