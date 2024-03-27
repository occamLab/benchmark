
echo "---------------------NOTICE--------------------------------"
echo "multi_model_test_runner.sh assumes that install.sh has already been run"
echo "---------------------NOTICE--------------------------------"


source ~/anaconda3/etc/profile.d/conda.sh
conda activate anchor

# change directory to root of repo regardless of where file has been executed from
# https://stackoverflow.com/questions/3349105/how-can-i-set-the-current-working-directory-to-the-directory-of-the-script-in-ba
cd "$(dirname "${BASH_SOURCE[0]}")"
cd ../../../

export PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python
python -m anchor.backend.data.multi_model_ace