import os
import re
import functools

from Utils import run_cmd, run_cmd_capture_output
from Const import SUCCESS, FAILURE


def get_nc_filename(full_filename):
    print("xxx full_filename: {f}".format(f=full_filename))
    just_filename = None
    #match_obj = re.match("(\S+).(\S+).nc", full_filename)
    match_obj = re.match(r'(\S+).(\S+).nc', full_filename)
    if match_obj:
        just_filename = match_obj.group(1)
        print("XXX just_filename: {f}".format(f=just_filename))
    return(just_filename)

def compare_to_expected(expected_datafiles, downloaded_files):

    if functools.reduce(lambda x, y : x and y, map(lambda p, q: p == q, expected_datafiles, downloaded_files), True): 
        print ("PASS...Downloaded or would have downloaded file(s) match expected file(s)")
        ret = SUCCESS
    else:
        print ("FAIL...Downloaded or would have downloaded file(s) did not match expected file(s)")
        ret = FAILURE
    return (ret)

def download_data_files(shards, wget_node, data_node, dataset_id, expected_data_files, temp_dir, expected_datafiles, do_download=True):

    url = "https://{n}/wget".format(n=wget_node)

    dataset_param = "dataset_id={d}|{dn}".format(d=dataset_id,
                                                 dn=data_node)
    params = "--data \"{ds_param}\"".format(ds_param=dataset_param)

    if shards:
        shards_param = " --data \"shards={s}\"".format(s=shards)
        params = params + shards_param 


    cmd = "curl {params} {url} -o {dir}/wget.bash".format(params=params,
                                                          url=url,
                                                          dir=temp_dir)

    

#    cmd = "curl --data \"dataset_id={d}|{dn}\" https://{n}/wget -o {dir}/wget.bash".format(d=dataset_id,
#                                                                                           dn=data_node,
#                                                                                           n=wget_node,
#                                                                                           dir=temp_dir)


    ret = run_cmd(cmd)
    if ret != SUCCESS:
        return(ret)

    if do_download:
        ret = run_cmd("bash {d}/wget.bash".format(d=temp_dir), cwd=temp_dir)
        if ret != SUCCESS:
            return(ret)

        for f in expected_datafiles:
            should_expect_f = "{d}/{f}".format(d=temp_dir, f=f)
            nc_filename = get_nc_filename(should_expect_f)
            if os.path.exists(should_expect_f):
                print("FOUND {f}".format(f=f))
                ret = SUCCESS
            else:
                print("FAIL...did not find {f}".format(f=f))
                ret = FAILURE
                break
    else:
        print("Not downloading the file")
        would_have_downloaded_files = []
        ret, cmd_output = run_cmd_capture_output("bash {d}/wget.bash -n".format(d=temp_dir), cwd=temp_dir)
        if ret != SUCCESS:
            return(ret)
        for l in cmd_output:
            match_obj = re.match(r'(\S+)\s+...Downloading', l)
            if match_obj:
                filename = match_obj.group(1)
                print("WOULD HAVE DOWNLOADED {f}".format(f=filename))
                would_have_downloaded_files.append(filename)
            ret = compare_to_expected(expected_datafiles, would_have_downloaded_files)

    return(ret)




