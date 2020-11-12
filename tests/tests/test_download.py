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

def read_in_data(test_case):

    with open(os.environ["WGET_API_TEST_DATA"]) as f:
        test_data_dict = json.load(f)
        test_case_dict = test_data_dict[test_case]
        return(test_case_dict["index_node"],
               test_case_dict["shards"],
               test_case_dict["dataset_ids"],
               test_case_dict["do_download"])
    return(None)

@pytest.mark.parametrize("download_test", ["1_dataset_id_1_nc",
                                           "1_dataset_id_multiple_ncs",
                                           "2_dataset_id_multiple_nc"])

def test_download(data, download_test):

    index_node, shards, dataset_ids, do_download = read_in_data(download_test)
    temp_dir = tempfile.mkdtemp()
    #
    # index_node is for searching
    #
    data_files = search_data_files(index_node, dataset_ids, temp_dir)

    # REVISIT
    # wget_node = "http://esgf-dev2.llnl.gov"
    # wget_node = "https://nimbus15.llnl.gov:8443"
    wget_node = os.environ["WGET_API_HOST_URL"]
    assert wget_node
    
    ret = get_wget_bash(shards, wget_node, dataset_ids, temp_dir)
    assert ret == SUCCESS

    ret = run_wget_bash(data_files, temp_dir, do_download=do_download)

    shutil.rmtree(temp_dir)
    
    assert ret == SUCCESS

# from the root of the repo
# export WGET_API_HOST_URL=https://nimbus15.llnl.gov:8443
# pytest --capture=tee-sys --data `pwd`/tests/test_data/test_data.json tests/tests/test_download.py



