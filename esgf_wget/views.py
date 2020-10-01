
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import xml.etree.ElementTree as ET
import urllib.request
import urllib.parse
import datetime
import json
import os

from .query_utils import split_value, \
                         KEYWORDS, \
                         CORE_QUERY_FIELDS
from .local_settings import ESGF_SOLR_SHARDS_XML, \
                            ESGF_SOLR_URL, \
                            WGET_SCRIPT_FILE_DEFAULT_LIMIT, \
                            WGET_SCRIPT_FILE_MAX_LIMIT

def get_solr_shards_from_xml():
    shard_list = []
    if os.path.isfile(ESGF_SOLR_SHARDS_XML):
        tree = ET.parse(ESGF_SOLR_SHARDS_XML)
        root = tree.getroot()
        for value in root:
            shard_list.append(value.text)
    return shard_list

def home(request):
    return HttpResponse('esgf-wget')

@require_http_methods(['GET', 'POST'])
@csrf_exempt
def generate_wget_script(request):

    query_url = ESGF_SOLR_URL + '/files/select'
    file_limit = WGET_SCRIPT_FILE_DEFAULT_LIMIT
    file_offset = 0
    use_sort = False
    use_distrib = True
    timestamp_from = None
    timestamp_to = None
    requested_shards = []
    script_template_file = 'wget-template.sh'
    xml_shards = get_solr_shards_from_xml()

    querys = []
    file_query = ['type:File']

    # Gather dataset_ids and other parameters
    if request.method == 'POST':
        url_params = request.POST.copy()
    elif request.method == 'GET':
        url_params = request.GET.copy()
    else:
        return HttpResponse('Request method must be POST or GET.')

    # Create list of parameters to be saved in the script
    url_params_list = []
    for param, value_list in url_params.lists():
        for v in value_list:
            url_params_list.append('{}={}'.format(param, v))

    # Set range for timestamps to query
    if url_params.get('from') or url_params.get('to'):
        if url_params.get('from'):
            timestamp_from = url_params.pop('from')[0]
            ts_from = timestamp_from
        else:
            ts_from = '*'
        if url_params.get('to'):
            timestamp_to = url_params.pop('to')[0]
            ts_to = timestamp_to
        else:
            ts_to = '*'
        timestamp_from_to = "_timestamp:[{} TO {}]".format(ts_from, ts_to)
        querys.append(timestamp_from_to)

    # Set datetime start and stop
    if url_params.get('datetime_start'):
        datetime_start = url_params.pop('datetime_start')[0]
        querys.append("datetime_start:[{} TO *]".format(datetime_start))

    if url_params.get('datetime_stop'):
        datetime_stop = url_params.pop('datetime_stop')[0]
        querys.append("datetime_stop:[* TO {}]".format(datetime_stop))

    # Set version min and max
    if url_params.get('min_version'):
        min_version = url_params.pop('min_version')[0]
        querys.append("version:[{} TO *]".format(min_version))

    if url_params.get('max_version'):
        max_version = url_params.pop('max_version')[0]
        querys.append("version:[* TO {}]".format(max_version))

    # Set bounding box constraint
    if url_params.get('bbox'):
        (west, south, east, north) = url_params.pop('bbox')[0]
        querys.append('east_degrees:[{} TO *]'.format(west))
        querys.append('north_degrees:[{} TO *]'.format(south))
        querys.append('west_degrees:[* TO {}]'.format(east))
        querys.append('south_degrees:[* TO {}]'.format(north))

    if len(querys) == 0:
        querys.append('*:*')
    query_string = ' AND '.join(querys)

    # Create a simplified script that only runs wget on a list of files
    if url_params.get('simple'):
        use_simple_param = url_params.pop('simple')[0].lower()
        if use_simple_param == 'false':
            script_template_file = 'wget-template.sh'
        elif use_simple_param == 'true':
            script_template_file = 'wget-simple-template.sh'
        else:
            return HttpResponse('Parameter \"simple\" must be set to true or false.')

    # Enable distributed search
    if url_params.get('distrib'):
        use_distrib_param = url_params.pop('distrib')[0].lower()
        if use_distrib_param == 'false':
            use_distrib = False
        elif use_distrib_param == 'true':
            use_distrib = True
        else:
            return HttpResponse('Parameter \"distrib\" must be set to true or false.')

    # Enable sorting of records
    if url_params.get('sort'):
        use_sort_param = url_params.pop('sort')[0].lower()
        if use_sort_param == 'false':
            use_sort = False
        elif use_sort_param == 'true':
            use_sort = True
        else:
            return HttpResponse('Parameter \"sort\" must be set to true or false.')

    # Use Solr shards requested from GET/POST
    if url_params.get('shards'):
        requested_shards = url_params.pop('shards')[0].split(',')

    # Set file number limit within a set maximum number
    if url_params.get('limit'):
        file_limit = min(int(url_params.pop('limit')[0]), WGET_SCRIPT_FILE_MAX_LIMIT)

    # Set the starting index for the returned records from the query
    if url_params.get('offset'):
        file_offset = int(url_params.pop('offset')[0])

    # Set boolean constraints
    boolean_constraints = ['latest', 'retracted', 'replica']
    for bc in boolean_constraints:
        if url_params.get(bc):
            bc_value = url_params.pop(bc)[0].lower()
            if bc_value == 'false' or bc_value == 'true':
                file_query.append('%s:%s'%(bc, bc_value))
            else:
                return HttpResponse('Parameter \"%s\" must be set to true or false.'%bc)
    
    # Collect remaining constraints
    for param, value_list in url_params.lists():
        # Check for negative constraints
        if param[-1] == '!':
            param = '-' + param[:-1]

        # Split values separated by commas but don't split at commas inside parentheses
        # (i.e. cases such as "CESM1(CAM5.1,FV2)")
        split_value_list = []
        for v in value_list:
            for sv in split_value(v):
                split_value_list.append(sv)

        if len(split_value_list) == 1:
            fq = '{}:{}'.format(param, split_value_list[0])
        else:
            fq = '{}:({})'.format(param, ' || '.join(split_value_list))
        file_query.append(fq)

    file_attributes = ['title', 'url', 'checksum_type', 'checksum']
    query_params = dict(q=query_string, 
                        wt='json', 
                        facet='true', 
                        fl=file_attributes, 
                        fq=file_query,
                        start=file_offset,
                        limit=file_limit,
                        rows=file_limit)

    # Sort by timestamp descending if enabled, otherwise sort by id ascending
    if use_sort:
        query_params.update(dict(sort='_timestamp desc'))
    else:
        query_params.update(dict(sort='id asc'))

    # Use shards for distributed search if 'distrib' is true, otherwise use only local search
    if use_distrib:
        if len(requested_shards) > 0:
            shards = ','.join([s + '/files' for s in requested_shards])
            query_params.update(dict(shards=shards))
        elif len(xml_shards) > 0:
            shards = ','.join([s + '/files' for s in xml_shards])
            query_params.update(dict(shards=shards))

    # Fetch files for the query
    file_list = []
    query_encoded = urllib.parse.urlencode(query_params, doseq=True).encode()
    req = urllib.request.Request(query_url, query_encoded)
    with urllib.request.urlopen(req) as response:
        results = json.loads(response.read().decode())
    num_files = results['response']['numFound']
    for file_info in results['response']['docs']:
        filename = file_info['title']
        checksum_type = file_info['checksum_type'][0]
        checksum = file_info['checksum'][0]
        for url in file_info['url']:
            url_split = url.split('|')
            if url_split[2] == 'HTTPServer':
                file_list.append(dict(filename=filename, 
                                      url=url_split[0], 
                                      checksum_type=checksum_type, 
                                      checksum=checksum))
                break

    # Limit the number of files to the maximum
    wget_warn = None
    if num_files == 0:
        return HttpResponse('No files found for datasets.')
    elif num_files > file_limit:
        wget_warn = 'Warning! The total number of files was {} ' \
                    'but this script will only process {}.'.format(num_files, file_limit)

    # Build wget script
    current_datetime = datetime.datetime.now()
    timestamp = current_datetime.strftime('%Y/%m/%d %H:%M:%S')

    context = dict(timestamp=timestamp,
                   url_params=url_params_list,
                   files=file_list,
                   warning_message=wget_warn)
    wget_script = render(request, script_template_file, context)

    script_filename = current_datetime.strftime('wget-%Y%m%d%H%M%S.sh')

    response = HttpResponse(wget_script, content_type='text/x-sh')
    response['Content-Disposition'] = 'attachment; filename={}'.format(script_filename)
    return response