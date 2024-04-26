#!/bin/bash
filename='/elixir/application/backend/data/edam/current_version.txt'
version=$(head -n 1 $filename)
url="https://raw.githubusercontent.com/edamontology/edamontology/master/releases/EDAM_"${version}".owl"
writepath=/elixir/application/backend/data/edam/owl/EDAM_${version}.owl
curl $url > $writepath
python /elixir/application/backend/manage.py parse_edam
