
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
    xml_shards = get_solr_shards_from_xml()
    querys = []

    # Gather dataset_ids and other parameters
    if request.method == 'POST':
        url_params = request.POST
    elif request.method == 'GET':
        url_params = request.GET
    else:
        return HttpResponse('Request method must be POST or GET.')

    # Set range for timestamps to query
    if url_params.get('from') or url_params.get('to'):
        if url_params.get('from'):
            timestamp_from = url_params['from']
            ts_from = timestamp_from
        else:
            ts_from = '*'
        if url_params.get('to'):
            timestamp_to = url_params['to']
            ts_to = timestamp_to
        else:
            ts_to = '*'
        timestamp_from_to = "_timestamp:[{} TO {}]".format(ts_from, ts_to)
        querys.append(timestamp_from_to)

    if len(querys) == 0:
        querys.append('*:*')
    query_string = ' AND '.join(querys)

    # Enable distributed search
    if url_params.get('distrib'):
        if url_params['distrib'].lower() == 'false':
            use_distrib = False
        elif url_params['distrib'].lower() == 'true':
            use_distrib = True
        else:
            return HttpResponse('Parameter \"distrib\" must be set to true or false.')

    # Enable sorting of records
    if url_params.get('sort'):
        if url_params['sort'].lower() == 'false':
            use_sort = False
        elif url_params['sort'].lower() == 'true':
            use_sort = True
        else:
            return HttpResponse('Parameter \"sort\" must be set to true or false.')

    # Use Solr shards requested from GET/POST
    if url_params.get('shards'):
        requested_shards = url_params['shards'].split(',')

    # Set file number limit within a set maximum number
    if url_params.get('limit'):
        file_limit = min(int(url_params['limit']), WGET_SCRIPT_FILE_MAX_LIMIT)

    # Set the starting index for the returned records from the query
    if url_params.get('offset'):
        file_offset = int(url_params['offset'])

    file_query = ['type:File']

    # Get dataset ids
    dataset_id_list = []
    if url_params.get('dataset_id'):
        dataset_id_list = url_params.getlist('dataset_id')
        if len(dataset_id_list) == 1:
            datasets_query = 'dataset_id:{}'.format(dataset_id_list[0])
        else:
            datasets_query = 'dataset_id:({})'.format(' || '.join(dataset_id_list))
        file_query.append(datasets_query)

    file_attributes = ['title', 'url', 'checksum_type', 'checksum']
    query_params = dict(q=query_string, 
                        wt='json', 
                        facet='true', 
                        fl=file_attributes, 
                        fq=file_query,
                        start=file_offset,
                        limit=file_limit,
                        rows=file_limit)

    if use_sort:
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
                   datasets=dataset_id_list,
                   distrib=use_distrib,
                   sort=use_sort,
                   shards=requested_shards,
                   file_limit=file_limit,
                   file_offset=file_offset,
                   timestamp_from=timestamp_from,
                   timestamp_to=timestamp_to,
                   files=file_list,
                   warning_message=wget_warn)
    wget_script = render(request, 'wget-template.sh', context)

    script_filename = current_datetime.strftime('wget-%Y%m%d%H%M%S.sh')

    response = HttpResponse(wget_script, content_type='text/x-sh')
    response['Content-Disposition'] = 'attachment; filename={}'.format(script_filename)
    return response