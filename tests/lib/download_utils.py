import os
import re
import functools

from Utils import run_cmd, run_cmd_capture_output
from Const import SUCCESS, FAILURE


def get_nc_filename(full_filename):
    # print("xxx full_filename: {f}".format(f=full_filename))
    just_filename = None
    #match_obj = re.match("(\S+).(\S+).nc", full_filename)
    match_obj = re.match(r'(\S+).(\S+).nc', full_filename)
    if match_obj:
        just_filename = match_obj.group(1)
        # print("XXX just_filename: {f}".format(f=just_filename))
    return(just_filename)

def compare_to_expected(expected_datafiles, downloaded_files):

    print("INFO...number of expected datafiles: {n}".format(n=len(expected_datafiles)))
    print("INFO...number of download files: {n}".format(n=len(downloaded_files)))

    if functools.reduce(lambda x, y : x and y, map(lambda p, q: p == q, expected_datafiles, downloaded_files), True): 
        print ("PASS...Downloaded or would have downloaded file(s) match expected file(s)")
        ret = SUCCESS
    else:
        print ("FAIL...Downloaded or would have downloaded file(s) did not match expected file(s)")
        ret = FAILURE
    return (ret)

def get_wget_bash_PREV(shards, wget_node, dataset_ids, temp_dir, limit=None):

    print("xxx...get_wget_bash()...xxx")
    # url = "https://{n}/wget".format(n=wget_node)
    url = "{n}/wget".format(n=wget_node)

    params = ""
    for id in dataset_ids:
        dataset_param = "dataset_id={d}".format(d=id)
        params = params + " --data \"{ds_param}\"".format(ds_param=dataset_param)

    if shards:
        shards_str = ",".join(shards)
        shards_param = " --data \"shards={s}\"".format(s=shards_str)
        params = params + shards_param

    if limit:
        limit_param = " --data \"limit={l}\"".format(l=limit)
        params = params + limit_param

    # print("xxx params: ", params)
    cmd = "curl {url} {params} -o {dir}/wget.bash".format(params=params,
                                                          url=url,
                                                          dir=temp_dir)
    
    ret = run_cmd(cmd)
    return ret


def construct_wget_params(test_dict):
    exclude_list = ["index_node", "do_download"]
    params = ""
    for key in test_dict:
        if key in exclude_list:
            continue
        elif key == "shards":
            shards_str = test_dict["shards"][0]
            shards_param = " --data \"shards={s}\"".format(s=shards_str)
            params = params + shards_param
        elif key == "dataset_ids":
            for id in test_dict["dataset_ids"]:
                dataset_param = "dataset_id={d}".format(d=id)
                params = params + " --data \"{ds_param}\"".format(ds_param=dataset_param)            
        else:
            params = params + " --data \"{k}={v}\"".format(k=key,
                                                           v=test_dict[key])
    return(params)
        
# def get_wget_bash(shards, wget_node, dataset_ids, temp_dir, limit=None):
def get_wget_bash(wget_node, test_dict, temp_dir):

    print("xxx...get_wget_bash()...xxx")
    # url = "https://{n}/wget".format(n=wget_node)
    url = "{n}/wget".format(n=wget_node)

    params = construct_wget_params(test_dict)

    # print("xxx params: ", params)
    cmd = "curl {url} {params} -o {dir}/wget.bash".format(params=params,
                                                          url=url,
                                                          dir=temp_dir)
    
    ret = run_cmd(cmd)
    return ret

def run_wget_bash(expected_datafiles, temp_dir, do_download):

    print("xxx...download_data_files...xxx")
    print("...expected_data_files:")
    for f in expected_datafiles:
        print("...f: {f}".format(f=f))

    if do_download:
        ret = run_cmd("bash {d}/wget.bash".format(d=temp_dir), cwd=temp_dir)
        if ret != SUCCESS:
            return(ret)

        for f in expected_datafiles:
            should_expect_f = "{d}/{f}".format(d=temp_dir, f=f)
            nc_filename = get_nc_filename(should_expect_f)
            if os.path.exists(should_expect_f):
                print("FOUND Downloaded file: {f}".format(f=f))
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

def check_wget_response(temp_dir, expected_response):

    print("xxx...check_wget_response...xxx")
    with open("{d}/wget.bash".format(d=temp_dir)) as f:
        lines = f.readlines()
        if expected_response in lines[0]:
            print("FOUND the expected response: {r}".format(r=expected_response))
            ret = SUCCESS
        else:
            print("Did not find the expected response: {r}".format(r=expected_response))
            ret = FAILURE
    return(ret)
