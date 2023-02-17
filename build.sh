#!bin/bash

# remove build directory if it exists
rm -r build

# install build requirements
pip install -r requirements.txt

# Build seed_to_time
cd ./seed_to_time/
poetry run poetry build --format=wheel
cd ..

# Copy to build folder
mkdir build
cp ./index.html ./build/
cp ./numba_pokemon_prngs-0.1.0-py3-none-any.whl ./build/
cp ./seed_to_time/dist/seed_to_time-0.1.0-py3-none-any.whl ./build