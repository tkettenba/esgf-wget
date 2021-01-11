# esgf-wget test suite
Test suite are written using pytest

# Set up for running test suite

```
# Download a miniconda installer and install miniconda. Example below is for MacOS

curl https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86.sh -o Miniconda3-latest-MacOSX-x86.sh
bash ./Miniconda3-latest-MacOSX-x86.sh  -b -p miniconda3
source miniconda3/etc/profile.d/conda.sh
conda activate base

# create a conda environment and install the necessary packages for running the test suite.
conda update -n base -c defaults conda -y
conda create -n test_esgf_wget -c conda-forge pytest wget curl

# Following steps assume wget api service is already running with "CMIP5" and "CMIP6" 
# in the list of allowed_projects, but not "obs4MIPs".
#
# set the needed environment variable for running the test suite.

# For example: export WGET_API_HOST_URL=https://mywgetapiserver.llnl.gov:8080
export WGET_API_HOST_URL=<wget_api_server_url>

# clone the esgf-wget repo
git clone -b <branch> https://github.com/esgf/esgf-wget.git
cd esgf-wget
pytest --capture=tee-sys --data `pwd`/tests/test_data/test_download.json tests/tests/test_download_not_allowed.py
pytest --capture=tee-sys --data `pwd`/tests/test_data/test_download.json tests/tests/test_download.py





