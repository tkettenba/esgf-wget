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

@pytest.mark.parametrize("download_test", ["1_dataset_id_1_nc",
                                           "1_dataset_id_multiple_ncs",
                                           "2_dataset_id_multiple_nc",
                                           "cmip5_1_dataset_id_multiple_ncs",
                                           "cmip5_1_dataset_id_multiple_ncs_multiple_shards",
                                           "cmip6_params1",
                                           "1_dataset_id_multiple_ncs_offset_0"])
                                           "1_dataset_id_multiple_ncs_offset_1"])

#@pytest.mark.parametrize("download_test", ["cmip6_params1"])

def test_download(data, download_test):
    '''
    parameters:
       data - data file (json format) - tests/test_data/test_download.json
       download_test - list of test cases to run

    test steps:
       + calls search_data_files() which accesses the search API with the
         specified parameters, and get the list of data files returned.
       + calls get_wget_bash() which accesses the wget API specifying 
         same parameters and get the wget bash script.
       + calls run_wget_bash() which checks if the data files specified in 
         the wget bash script matches the data files returned with the
         search API.
    '''

    test_dict = read_in_data(download_test)
    temp_dir = tempfile.mkdtemp()
    #
    # index_node is for searching
    #
    data_files = search_data_files(test_dict, temp_dir)

    #
    # wget_node = "https://nimbus15.llnl.gov:8443"
    wget_node = os.environ["WGET_API_HOST_URL"]
    assert wget_node
    
    ret = get_wget_bash(wget_node, test_dict, temp_dir)
    assert ret == SUCCESS

    ret = run_wget_bash(data_files, temp_dir, do_download=test_dict["do_download"])

    shutil.rmtree(temp_dir)
    
    assert ret == SUCCESS

#
# Before running the test suite, deploy wgetApi. 
# Below is an example of wgetApi settings.
#
#    settings:
#      debug: False
#      allowedHosts: "*"
#      esgfSolrUrl: https://esgf-node.llnl.gov/solr
#      esgfSolrShardsXml: /esg/esgf_wget/esgf_solr_shards.xml
#      wgetScriptFileDefaultLimit: 10000
#      wgetScriptFileMaxLimit: 50000
#      dataUploadMaxNumberFields: 10240
#      wgetMaxDirLength: 50
#      # Allowed projects for wget api
#      allowed_projects:
#        - '"CMIP6"'
#        - '"CMIP5"'
#        - '"CMIP3"'
#        - '"input4MIPs"'
#        - '"CREATE-IP"'
#        - '"E3SM"'
#      shards:
#        - localhost:8983/solr
#        - localhost:8985/solr
#        - localhost:8987/solr
#        - localhost:8988/solr
#        - localhost:8990/solr
#        - localhost:8993/solr
#        - localhost:8994/solr
#        - localhost:8995/solr
#        - localhost:8996/solr
#        - localhost:8997/solr
   
#
# from the root of the repo
# export WGET_API_HOST_URL=https://nimbus15.llnl.gov:8443
# pytest --capture=tee-sys --data `pwd`/tests/test_data/test_download.json tests/tests/test_download.py
#


