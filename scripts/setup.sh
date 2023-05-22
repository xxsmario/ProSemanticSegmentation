
#!/bin/bash

echo "Setup OS packages"

sudo add-apt-repository ppa:ubuntugis/ppa
sudo apt-get -y update
sudo apt install -y git wget python3 python3-dev python3-gdal gdal-bin libgdal-dev
sudo apt upgrade -y git wget python3 python3-dev python3-gdal gdal-bin libgdal-dev

echo "Setup Python dependencies packages"

sudo pip3 install numpy
sudo pip3 install tensorflow-gpu==1.7.0 
sudo pip3 install scikit-image
sudo pip3 install scikit-learn 
sudo pip3 install matplotlib 
sudo pip3 install seaborn
sudo pip3 install psutil

echo "Installation Done"