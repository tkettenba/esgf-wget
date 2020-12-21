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
from download_utils import get_wget_bash, run_wget_bash
from common_utils import read_in_data

@pytest.mark.parametrize("download_offset_limit_test",
                         ["1_dataset_id_multiple_ncs_offset_1"])

        
def test_download_offset_limit(data, download_offset_limit_test):

    test_dict  = read_in_data(download_offset_limit_test)
    temp_dir = tempfile.mkdtemp()
    #
    # index_node is for searching
    #
    data_files = search_data_files(test_dict, temp_dir)
    for f in data_files:
        print("data file: {f}".format(f=f))

    wget_node = os.environ["WGET_API_HOST_URL"]
    assert wget_node
    
    ret = get_wget_bash(wget_node, test_dict, temp_dir)
    assert ret == SUCCESS

    offset = test_dict["offset"]
    limit = test_dict["limit"]
    ret = run_wget_bash(data_files[offset:(limit + offset if limit is not None else None)],
                        temp_dir, do_download=test_dict["do_download"])

    ret = run_wget_bash(data_files,
                        temp_dir, do_download=test_dict["do_download"])    

    #shutil.rmtree(temp_dir)
    
    assert ret == SUCCESS

# from the root of the repo                                                                                                                                                    
# export WGET_API_HOST_URL=https://nimbus15.llnl.gov:8443                                                                                                                      
# pytest --capture=tee-sys --data `pwd`/tests/test_data/test_offset_limit.json tests/tests/test_download_offset_limit.py
