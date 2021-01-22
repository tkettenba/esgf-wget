import os
import json

def read_in_data(test_case):

    with open(os.environ["WGET_API_TEST_DATA"]) as f:
        test_data_dict = json.load(f)
        test_case_dict = test_data_dict[test_case]
        return(test_case_dict)
    return(None)

#        return(test_case_dict["index_node"],
#               test_case_dict["shards"],
#               test_case_dict["dataset_ids"],
#               test_case_dict["do_download"])
    return(None)
