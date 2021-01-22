

import json
import re

from Utils import run_cmd
from Const import SUCCESS, FAILURE

def construct_params_for_search(test_dict):
    exclude_list = ["index_node", "dataset_ids", "do_download"]
    params = None
    for key in test_dict:
        if key in exclude_list:
            continue
        elif key == "shards":
            key_value = "{k}={v}".format(k=key, v=test_dict[key][0])
        else:
            key_value = "{k}={v}".format(k=key, v=test_dict[key])
        if params:
            params = params + "&{p}".format(p=key_value)
        else:
            params = key_value

    if "limit" not in test_dict:
        params = params + "&limit=10000"
        
    if "dataset_ids" in test_dict:
        for dataset_id_str in test_dict["dataset_ids"]:
            dataset_id, data_node = dataset_id_str.split("|")
    
            if params:
                params = params + "&dataset_id={id}%7C{data}".format(id=dataset_id,
                                                                     data=data_node)
            else:
                params = "&dataset_id={id}%7C{data}".format(id=dataset_id,
                                                            data=data_node)
    return(params)
            
def get_datafiles_from_search_result(search_output_json_file):
    data_files = []
    with open(search_output_json_file) as f:
        json_data = json.load(f)

        docs = json_data['response']['docs']
        for d in docs:
            match_obj = re.match(r'(\S+)\|(\S+)', d['id'])
            full_nc_filename = match_obj.group(1)
            match_obj = re.match(r'\S+\.(\S+\.nc)$', full_nc_filename)
            nc_filename = match_obj.group(1)
            data_files.append(nc_filename)

    return(data_files)

def search_data_files(test_dict, temp_dir):
#    temp_dir = tempfile.mkdtemp()

    index_node = test_dict["index_node"]
    params = construct_params_for_search(test_dict)

    std_params = "format=application%2fsolr%2bjson&type=File"
    if params:
        url = "https://{index}/esg-search/search?{p}&{p1}".format(index=index_node,
                                                                  p=std_params,
                                                                  p1=params)
    else:
        url = "https://{index}/esg-search/search?{p}".format(index=index_node,
                                                             p=std_params)
    print("url: {u}".format(u=url))
    search_result_json_file = "{dir}/curl.out.json".format(dir=temp_dir)
    cmd = "curl \"{url}\" -o {f}".format(url=url,
                                         f=search_result_json_file)
    ret = run_cmd(cmd)
    if ret != SUCCESS:
        return(ret)

    data_files = get_datafiles_from_search_result(search_result_json_file)
    for d in data_files:
        print("FOUND from search, filename: {d}".format(d=d))
    return(data_files)

def search_data_filesPREV(test_dict, temp_dir):
#    temp_dir = tempfile.mkdtemp()

    data_files = []
    index_node = test_dict["index_node"]
    params = get_params_for_search(test_dict)

    for dataset_id_str in test_dict["dataset_ids"]:

        dataset_id, data_node = dataset_id_str.split("|")
        std_params = "format=application%2fsolr%2bjson&type=File"

        if params:
            url = "https://{index}/esg-search/search?{p}&dataset_id={id}%7C{data}&{p1}".format(index=index_node,
                                                                                               p=std_params,
                                                                                               data=data_node,
                                                                                               id=dataset_id,
                                                                                               p1=params)
        else:
            url = "https://{index}/esg-search/search?{p}&dataset_id={id}%7C{data}".format(index=index_node,
                                                                                          p=std_params,
                                                                                          data=data_node,
                                                                                          id=dataset_id)
        print("url: {u}".format(u=url))
        search_result_json_file = "{dir}/curl.out.json".format(dir=temp_dir)
        cmd = "curl \"{url}\" -o {f}".format(url=url,
                                             f=search_result_json_file)
        ret = run_cmd(cmd)
        if ret != SUCCESS:
            return(ret)

        dataset_datafiles = get_datafiles_from_search_result(search_result_json_file)
        data_files.extend(dataset_datafiles)

    for d in data_files:
        print("FOUND from search, filename: {d}".format(d=d))

    return(data_files)
