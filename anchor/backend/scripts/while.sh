#!/bin/bash

echo "---------------------NOTICE--------------------------------"
echo "while.sh assumes that install.sh has already been run"
echo "---------------------NOTICE--------------------------------"

source ~/anaconda3/etc/profile.d/conda.sh
conda activate anchor

# change directory to root of repo regardless of where file has been executed from
# https://stackoverflow.com/questions/3349105/how-can-i-set-the-current-working-directory-to-the-directory-of-the-script-in-ba
cd "$(dirname "${BASH_SOURCE[0]}")"
cd ../../../

export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

# runs continuously, checking for new uploads to iosLoggerDemo/tarQueue/
# trains if new tar file is found, deletes the tar file and uploads the model to iosLoggerDemo/trainedModels/
while true
do
    # disable output buffering so that all logs are in the correct order
    export PYTHONUNBUFFERED=1 
    # retains logs to console and pushes them to the log_uploader as well
    python -m anchor.backend.data.ace
    # |& tee /dev/tty |& python -m "anchor.backend.data.log_uploader"
    # sleep 30
    break
done
