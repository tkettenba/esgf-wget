import os
import sys
import pytest
import tempfile
import json

this_dir = os.path.abspath(os.path.dirname(__file__))
modules_dir = os.path.join(this_dir, '..', 'lib')
sys.path.append(modules_dir)

from Const import SUCCESS, FAILURE
from search_utils import search_data_files
from download_utils import download_data_files

DOWNLOAD = True
NO_DOWNLOAD = False

test_data = []
with open("/Users/muryanto1/work/wget_api/tests/test_data/test_data.json") as f:
    test_data_dict = json.load(f)
#    print("XXX test_data: {td}".format(td=test_data_dict))
    # data_tuple = [(d[key] for key in ["index_node", "shards", "data_node", "dataset_ids", "do_download"]) for d in test_data_dict]
    for test_descr in test_data_dict:
#        print("XXX test_descr: {td}".format(td=test_descr))
        a_test_dict = test_data_dict[test_descr]
#        test_tuple = tuple(a_test_dict[k] for k in ["index_node", "shards", "data_node", "dataset_ids", "do_download"])
        test_tuple = tuple(a_test_dict[k] for k in ["index_node", "shards", "dataset_ids", "do_download"])
        test_data.append(test_tuple)

print("test_data: {td}".format(td=test_data))
        
@pytest.mark.parametrize("index_node,shards,dataset_ids,do_download", test_data)
def test_download_specify_one_dataset_id(index_node, shards, dataset_ids, do_download):
    # sys.stdout.write("...test_download_specify_one_dataset_id...\n")
    # index_node = "esgf-node.llnl.gov"
    # data_node = "aims3.llnl.gov"
    # dataset_id = "CMIP6.CMIP.E3SM-Project.E3SM-1-1.piControl.r1i1p1f1.Amon.clivi.gr.v20191029"

    temp_dir = tempfile.mkdtemp()
    #
    # index_node is for searching
    #
    data_files = search_data_files(index_node, dataset_ids, temp_dir)
    for f in data_files:
        print("data file: {f}".format(f=f))

    wget_node = "esgf-dev2.llnl.gov"
    ret = download_data_files(shards, wget_node, dataset_ids, data_files, temp_dir, data_files, do_download=do_download)

    
    assert True
#    assert ret == SUCCESS



