#!/bin/bash

echo "00) ------------------ Downloading and extracting forest_toy.zip ------------------"
rm -R forest_toy forest_toy.zip
wget https://storage.googleapis.com/nextgenmap-dataset/dl-semantic-segmentation/forest_toy.zip
unzip forest_toy.zip

echo "01) ------------------ Running standardize_imgs.py ------------------"
./st