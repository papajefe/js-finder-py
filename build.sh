#!bin/bash

# remove build directory if it exists
rm -r build

# install build requirements
pip install -r requirements.txt

# build modules
cd ./js_finder/
poetry run poetry build --format=wheel
cd ..

# download modules
mkdir dist
wget https://github.com/Lincoln-LM/numba_pokemon_prngs/releases/download/latest/numba_pokemon_prngs-0.1.0-py3-none-any.whl -O ./dist/numba_pokemon_prngs-0.1.0-py3-none-any.whl

# copy to build folder
mkdir build
mkdir ./build/wheels
cp -r ./css/ ./build/css/
cp -r ./pages/ ./build/pages/
cp ./index.html ./build/
cp ./dist/numba_pokemon_prngs-0.1.0-py3-none-any.whl ./build/wheels/
cp ./js_finder/dist/js_finder-0.1.0-py3-none-any.whl ./build/wheels/