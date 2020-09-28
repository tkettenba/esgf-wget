
import os
import sys
import pytest
import tempfile

this_dir = os.path.abspath(os.path.dirname(__file__))
modules_dir = os.path.join(this_dir, '..', 'lib')
sys.path.append(modules_dir)

from Const import SUCCESS, FAILURE
from search_utils import search_data_files
from download_utils import download_data_files

DOWNLOAD = True
NO_DOWNLOAD = False

test_data = [
    ("esgf-node.llnl.gov", "esgf-node.llnl.gov/solr", "aims3.llnl.gov", "CMIP6.C4MIP.E3SM-Project.E3SM-1-1.hist-bgc.r1i1p1f1.fx.areacella.gr.v20191212", DOWNLOAD),
    ("esgf-node.llnl.gov", "esgf-node.llnl.gov/solr", "aims3.llnl.gov", "CMIP6.CMIP.E3SM-Project.E3SM-1-1.piControl.r1i1p1f1.Amon.clivi.gr.v20191029", NO_DOWNLOAD)
]

@pytest.mark.parametrize("index_node,shards,data_node,dataset_id,do_download", test_data)
def test_download_specify_one_dataset_id(index_node, shards, data_node, dataset_id, do_download):
    # sys.stdout.write("...test_download_specify_one_dataset_id...\n")
    # index_node = "esgf-node.llnl.gov"
    # data_node = "aims3.llnl.gov"
    # dataset_id = "CMIP6.CMIP.E3SM-Project.E3SM-1-1.piControl.r1i1p1f1.Amon.clivi.gr.v20191029"
    temp_dir = tempfile.mkdtemp()
    #
    # index_node is for searching
    #
    data_files = search_data_files(index_node, data_node, dataset_id, temp_dir)
    for f in data_files:
        print("data file: {f}".format(f=f))

    wget_node = "esgf-dev2.llnl.gov"
    ret = download_data_files(shards, wget_node, data_node, dataset_id, data_files, temp_dir, data_files, do_download=do_download)
    # ret = download_data_files(shards, wget_node, data_node, dataset_id, data_files, temp_dir, data_files)

    assert ret == SUCCESS
