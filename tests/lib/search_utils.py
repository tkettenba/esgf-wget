

import json
import re

from Utils import run_cmd
from Const import SUCCESS, FAILURE


def search_data_files(index_node, data_node, dataset_id, temp_dir):
#    temp_dir = tempfile.mkdtemp()
    
    url = "https://{index}/search_files/{id}%7C{data}/{index}/".format(index=index_node,
                                                                       data=data_node,
                                                                       id=dataset_id)
    print("url: {u}".format(u=url))
    cmd = "curl {url} -o {dir}/curl.out.json".format(url=url,
                                                     dir=temp_dir)
    ret = run_cmd(cmd)
    if ret != SUCCESS:
        return(ret)

    data_files = []

    with open("{dir}/curl.out.json".format(dir=temp_dir)) as f:
        json_data = json.load(f)

        docs = json_data['response']['docs']
        for d in docs:
            match_obj = re.match("(\S+)\|(\S+)", d['id'])
            data_files.append(match_obj.group(1))

    for d in data_files:
        print("filename: {d}".format(d=d))

    return(data_files)
