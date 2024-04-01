git clone https://github.com/Anttwo/SuGaR.git --recursive

cd SuGaR

conda env create -f environment.yml
conda activate sugar

cd gaussian_splatting/submodules/diff-gaussian-rasterization/
pip install -e .
cd ../simple-knn/
pip install -e .
cd ../../../