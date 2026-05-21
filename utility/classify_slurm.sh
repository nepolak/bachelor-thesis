#!/bin/bash

if [ ! -d "$GTDBTK_DATA_PATH" ]; then
    echo "GTDBTK_DATA_PATH is not defined.">&2
    echo "Check https://ecogenomics.github.io/GTDBTk/installing/index.html#gtdb-tk-reference-data">&2

    exit 1
fi

mkdir -P intermediates/cwd/gtdbtk
cd intermediates/cwd/gtdbtk

sbatch ../../../utility/gtdbtk.sh ../../mags gtdb_out