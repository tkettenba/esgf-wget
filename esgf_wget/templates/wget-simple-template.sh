#!/bin/bash

download_files=(
{% spaceless %}{% for file in files %}'{{file.url}}'
{% endfor %}{% endspaceless %}
)

for i in "${download_files[@]}"
do
   wget $i
done
