#!/bin/bash

# run this script with source ./install.sh so that the environment can be propagated to the parent shell

# change directory to root of repo regardless of where file has been executed from
# https://stackoverflow.com/questions/3349105/how-can-i-set-the-current-working-directory-to-the-directory-of-the-script-in-ba
cd "$(dirname "${BASH_SOURCE[0]}")"
cd ../../../

# initialize the base environment from https://github.com/nianticlabs/ace/blob/main/environment.yml
source ~/anaconda3/etc/profile.d/conda.sh
conda create --name anchor python --no-default-packages
conda env update -f anchor/third_party/ace/environment.yml --name anchor --prune
conda activate anchor

# install ace subdependency
pip install -e anchor/third_party/ace/dsacstar
# create debug videos of training process in ace
sudo apt install ffmpeg -y

# install pyav video library https://pyav.org/docs/stable/
conda install av -c conda-forge

# install fastapi
conda install -c conda-forge fastapi[all]

# download our deps
pip install firebase-admin==6.1.0
pip install opencv-python~=4.7
