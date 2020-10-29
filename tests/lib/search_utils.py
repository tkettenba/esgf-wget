

import json
import re

from Utils import run_cmd
from Const import SUCCESS, FAILURE


def search_data_files(index_node, dataset_ids, temp_dir):
#    temp_dir = tempfile.mkdtemp()

    data_files = []
    for dataset_id_str in dataset_ids:

        dataset_id, data_node = dataset_id_str.split("|")
        param = "format=application%2fsolr%2bjson&type=File"
        url = "https://{index}/esg-search/search?{p}&dataset_id={id}%7C{data}".format(index=index_node,
                                                                                      p=param,
                                                                                      data=data_node,
                                                                                      id=dataset_id)
        

#        url = "https://{index}/search_files/{id}%7C{data}/{index}/".format(index=index_node,
#                                                                           data=data_node,
#                                                                           id=dataset_id)

        print("url: {u}".format(u=url))
        cmd = "curl \"{url}\" -o {dir}/curl.out.json".format(url=url,
                                                         dir=temp_dir)
        ret = run_cmd(cmd)
        if ret != SUCCESS:
            return(ret)

        with open("{dir}/curl.out.json".format(dir=temp_dir)) as f:
            json_data = json.load(f)

            docs = json_data['response']['docs']
            for d in docs:
                match_obj = re.match(r'(\S+)\|(\S+)', d['id'])
                full_nc_filename = match_obj.group(1)
                match_obj = re.match(r'\S+\.(\S+\.nc)$', full_nc_filename)
                nc_filename = match_obj.group(1)
                data_files.append(nc_filename)

    # for d in data_files:
    #     print("filename: {d}".format(d=d))

    return(data_files)

