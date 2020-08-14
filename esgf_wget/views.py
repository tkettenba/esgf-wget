
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
    use_distrib = True
    requested_shards = []
    xml_shards = get_solr_shards_from_xml()

    # Gather dataset_ids and other parameters
    if request.method == 'POST':
        url_params = request.POST
    elif request.method == 'GET':
        url_params = request.GET
    else:
        return HttpResponse('Request method must be POST or GET.')

    if url_params.get('distrib'):
        if url_params['distrib'].lower() == 'false':
            use_distrib = False
        elif url_params['distrib'].lower() == 'true':
            use_distrib = True
        else:
            return HttpResponse('Parameter \"distrib\" must be set to true or false.')
    if url_params.get('shards'):
        requested_shards = url_params['shards'].split(',')
    if url_params.get('limit'):
        file_limit = min(int(url_params['limit']), WGET_SCRIPT_FILE_MAX_LIMIT)
    if url_params.get('dataset_id'):
        dataset_id_list = url_params.getlist('dataset_id')
    else:
        return HttpResponse('No datasets selected.')

    # Build Solr query
    if len(dataset_id_list) == 1:
        datasets_query = 'dataset_id:{}'.format(dataset_id_list[0])
    else:
        datasets_query = 'dataset_id:({})'.format(' || '.join(dataset_id_list))

    file_query = ['type:File', datasets_query]
    file_attributes = ['title', 'url', 'checksum_type', 'checksum']
    query_params = dict(q='*:*', 
                        wt='json', 
                        facet='true', 
                        sort='id asc', 
                        fl=file_attributes, 
                        fq=file_query,
                        limit=file_limit)

    # Use shards for distributed search if 'distrib' is true, otherwise use only local search
    if use_distrib:
        if len(requested_shards) > 0:
            shards = ','.join([s + '/files' for s in requested_shards])
            query_params.update(dict(shards=shards))
        elif len(xml_shards) > 0:
            shards = ','.join([s + '/files' for s in xml_shards])
            query_params.update(dict(shards=shards))

    # Fetch the number of files for the query
    count_query_params = dict(rows=1)
    count_query_params.update(query_params)
    count_query_encoded = urllib.parse.urlencode(count_query_params, doseq=True).encode()
    req = urllib.request.Request(query_url, count_query_encoded)
    with urllib.request.urlopen(req) as response:
        results = json.loads(response.read().decode())
    num_files = results['response']['numFound']

    # Limit the number of files to the maximum
    wget_warn = None
    if num_files == 0:
        return HttpResponse('No files found for datasets.')
    elif num_files > file_limit:
        wget_warn = 'Warning! The total number of files was {} ' \
                    'but this script will only process {}.'.format(num_files, file_limit)
        num_files = file_limit

    # Fetch files for the query
    file_list = []
    file_query_params = dict(rows=num_files)
    file_query_params.update(query_params)
    file_query_encoded = urllib.parse.urlencode(file_query_params, doseq=True).encode()
    req = urllib.request.Request(query_url, file_query_encoded)
    with urllib.request.urlopen(req) as response:
        results = json.loads(response.read().decode())
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

    # Build wget script
    current_datetime = datetime.datetime.now()
    timestamp = current_datetime.strftime('%Y/%m/%d %H:%M:%S')

    context = dict(timestamp=timestamp,
                   datasets=dataset_id_list,
                   distrib=use_distrib,
                   shards=requested_shards,
                   file_limit=file_limit,
                   files=file_list,
                   warning_message=wget_warn)
    wget_script = render(request, 'wget-template.sh', context)

    script_filename = current_datetime.strftime('wget-%Y%m%d%H%M%S.sh')

    response = HttpResponse(wget_script, content_type='text/x-sh')
    response['Content-Disposition'] = 'attachment; filename={}'.format(script_filename)
    return response