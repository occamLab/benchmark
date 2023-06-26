#!/bin/bash

# run this script with source ./install.sh so that the environment can be propagated to the parent shell


# initialize the base environment from https://github.com/nianticlabs/ace/blob/main/environment.yml
source ~/anaconda3/etc/profile.d/conda.sh
conda create --name anchor python --no-default-packages
conda env update -f ../third_party/ace/environment.yml --name anchor --prune
conda activate anchor

# install ace subdependency
pip install -e ../third_party/ace/dsacstar

# download hloc deps
pip install -e ../third_party/Hierarchical-Localization

# download our deps
pip install firebase-admin==6.1.0
pip install opencv-python~=4.7
