#!/bin/bash

download_files=(
{% spaceless %}{% for filename, file in files.items %}'{{file.url}}'
{% endfor %}{% endspaceless %}
)

for i in "${download_files[@]}"
do
   {% if token %}
   wget --header="Authorization: Bearer {{ token }}" $i
   {% else %}
   wget $i
   {% endif %}
done
