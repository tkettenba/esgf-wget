import os
import sys
import pytest
import tempfile
import json
import shutil

this_dir = os.path.abspath(os.path.dirname(__file__))
modules_dir = os.path.join(this_dir, '..', 'lib')
sys.path.append(modules_dir)

from Const import SUCCESS, FAILURE
from search_utils import search_data_files
from download_utils import get_wget_bash, run_wget_bash, check_wget_response
from common_utils import read_in_data

#
# obs4MIPs is not listed in the allowed_projects of the deployment
#
@pytest.mark.parametrize("download_test", ["obs4MIPs_1_dataset_id_1_nc"])

def test_download_not_allowed(data, download_test):

    test_dict = read_in_data(download_test)
    temp_dir = tempfile.mkdtemp()
    #
    # index_node is for searching
    #
    data_files = search_data_files(test_dict, temp_dir)

    # wget_node = "https://nimbus15.llnl.gov:8443"
    wget_node = os.environ["WGET_API_HOST_URL"]
    assert wget_node

    expected_response = "This query cannot be completed since the project, obs4MIPs, is not allowed to be accessed by this site."
    ret = get_wget_bash(wget_node, test_dict, temp_dir)
    assert ret == SUCCESS
    
    ret = check_wget_response(temp_dir, expected_response)
    assert ret == SUCCESS
    
    shutil.rmtree(temp_dir)  
    assert ret == SUCCESS

# from the root of the repo
# export WGET_API_HOST_URL=https://nimbus15.llnl.gov:8443
# pytest --capture=tee-sys --data `pwd`/tests/test_data/test_download.json tests/tests/test_download_not_allowed.py



