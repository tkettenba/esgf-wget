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

test_data = []
with open("/Users/muryanto1/work/wget_api/tests/test_data/test_offset_limit.json") as f:
    test_data_dict = json.load(f)
    for test_descr in test_data_dict:
        a_test_dict = test_data_dict[test_descr]
        test_tuple = tuple(a_test_dict[k] for k in ["index_node", "shards", "dataset_ids", "do_download", "offset", "limit"])
        test_data.append(test_tuple)

print("test_data: {td}".format(td=test_data))
        
@pytest.mark.parametrize("index_node,shards,dataset_ids,do_download,offset,limit", test_data)
def test_download_offset_limit(index_node, shards, dataset_ids, do_download, offset, limit):

    temp_dir = tempfile.mkdtemp()
    #
    # index_node is for searching
    #
    data_files = search_data_files(index_node, dataset_ids, temp_dir)
    for f in data_files:
        print("data file: {f}".format(f=f))

    wget_node = "esgf-dev2.llnl.gov"
    ret = get_wget_bash(shards, wget_node, dataset_ids, temp_dir, limit)
    assert ret == SUCCESS

    ret = run_wget_bash(data_files[offset:(limit + offset if limit is not None else None)],
                        temp_dir, do_download=do_download)

    shutil.rmtree(temp_dir)
    
    assert ret == SUCCESS



