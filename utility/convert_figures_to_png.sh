#/bin/bash

find output -name "*.svg" -exec sh -c 'inkscape --export-type=png --export-background "#FFFFFF" --export-dpi=300 --export-filename="${1%.svg}.png" "$1"' _ {} \;