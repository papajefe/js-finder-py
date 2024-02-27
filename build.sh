#!bin/bash

# remove build/dist directory if they exist
rm -r build
rm -r dist

# install build requirements
pip install -r requirements.txt

python build.py

# build modules
cd ./js_finder/
poetry run poetry build --format=wheel
cd ..

# download modules
mkdir dist
wget https://github.com/Lincoln-LM/numba_pokemon_prngs/releases/download/latest/numba_pokemon_prngs-0.1.0-py3-none-any.whl -O ./dist/numba_pokemon_prngs-0.1.0-py3-none-any.whl
wget https://github.com/Lincoln-LM/wgpu-gen4ids/releases/download/latest/wgpu-gen4ids.zip
unzip wgpu-gen4ids.zip -d ./dist/
rm wgpu-gen4ids.zip

# copy to build folder
mkdir build
mkdir ./build/wheels
cp -r ./css/ ./build/css/
cp -r ./pages/ ./build/pages/
cp ./index.html ./build/
cp ./dist/numba_pokemon_prngs-0.1.0-py3-none-any.whl ./build/wheels/
cp ./js_finder/dist/js_finder-0.1.0-py3-none-any.whl ./build/wheels/
mv ./dist/package/ ./build/pages/wgpu_gen4ids/
rm ./build/pages/wgpu_gen4ids/.gitignore