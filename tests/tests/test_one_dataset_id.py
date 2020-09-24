
import os
import sys
import pytest
import tempfile

this_dir = os.path.abspath(os.path.dirname(__file__))
modules_dir = os.path.join(this_dir, '..', 'lib')
sys.path.append(modules_dir)

from search_utils import search_data_files
from download_utils import download_data_files

test_data = [
    ("esgf-node.llnl.gov", "aims3.llnl.gov", "CMIP6.C4MIP.E3SM-Project.E3SM-1-1.hist-bgc.r1i1p1f1.fx.areacella.gr.v20191212")
# below not working
#    ("esgf-node.llnl.gov", "aims3.llnl.gov", "CMIP6.CMIP.E3SM-Project.E3SM-1-1.piControl.r1i1p1f1.Amon.clivi.gr.v20191029")
#    ("esgf-node.llnl.gov", "aims3.llnl.gov", "CMIP6.ScenarioMIP.CCCma.CanESM5.ssp126.r12i1p2f1.Amon.wap.gn.v20190429")
]

@pytest.mark.parametrize("index_node,data_node,dataset_id", test_data)
def test_download_specify_one_dataset_id(index_node, data_node, dataset_id):
    # sys.stdout.write("...test_download_specify_one_dataset_id...\n")
    # index_node = "esgf-node.llnl.gov"
    # data_node = "aims3.llnl.gov"
    # dataset_id = "CMIP6.CMIP.E3SM-Project.E3SM-1-1.piControl.r1i1p1f1.Amon.clivi.gr.v20191029"
    temp_dir = tempfile.mkdtemp()
    #
    # index_node is the solr node
    #
    data_files = search_data_files(index_node, data_node, dataset_id, temp_dir)

    wget_node = "esgf-dev2.llnl.gov"
    ret = download_data_files(wget_node, data_node, dataset_id, data_files, temp_dir)

#    assert True
    assert False
