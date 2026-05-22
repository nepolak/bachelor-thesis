#!/bin/bash

if [ ! -d "$GTDBTK_DATA_PATH" ]; then
    echo "GTDBTK_DATA_PATH is not defined.">&2
    echo "Check https://ecogenomics.github.io/GTDBTk/installing/index.html#gtdb-tk-reference-data">&2

    exit 1
fi

host_dir="$(pwd)"
intermediates_dir="$host_dir/intermediates"
cwd_dir="$intermediates_dir/cwd/gtdbtk"

mkdir -p $cwd_dir
cd $cwd_dir

sbatch "$host_dir/utility/gtdbtk.sh" "$intermediates_dir/mags" "$intermediates_dir/conda/"