

from Utils import run_cmd
from Const import SUCCESS, FAILURE

def download_data_files(wget_node, data_node, dataset_id, expected_data_files, temp_dir, do_download=True):
    cmd = "curl --data \"dataset_id={d}|{dn}\" https://{n}/wget -o {dir}/wget.bash".format(d=dataset_id,
                                                                                           dn=data_node,
                                                                                           n=wget_node,
                                                                                           dir=temp_dir)
    ret = run_cmd(cmd)
    if ret != SUCCESS:
        return(ret)

    if do_download:
        ret = run_cmd("bash {d}/wget.bash".format(d=temp_dir), cwd=temp_dir)

    return(ret)


