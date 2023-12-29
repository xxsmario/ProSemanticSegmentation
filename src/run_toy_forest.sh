#!/bin/bash

echo "00) ------------------ Downloading and extracting forest_toy.zip ------------------"
rm -R forest_toy forest_toy.zip
wget https://storage.googleapis.com/nextgenmap-dataset/dl-semantic-segmentation/forest_toy.zip
unzip forest_toy.zip

echo "01) ------------------ Running standardize_imgs.py ------------------"
./standardize_imgs.py -n 0 -b 1 2 3 4 -i forest_toy/raw_data/mosaic_201709.tif forest_toy/raw_data/mosaic_201801.tif -o forest_toy/stand_data

echo "02) ------------------ Running stack_imgs.py ------------------"
./stack_imgs.py -i forest_toy/stand_data/mosaic_201709_stand.tif -r forest_toy/raw_da