#!/bin/bash

host_dir="$(pwd)"
intermediates_dir="$host_dir/intermediates"
cwd_dir="$intermediates_dir/cwd/gtdbtk"

mkdir -p "$cwd_dir"
cd "$cwd_dir"

sbatch "$host_dir/utility/fastani.sh" "$host_dir/nextflow.config" "$host_dir/fastani.nf" "$intermediates_dir/mags" "$intermediates_dir/mags_to_cluster.csv" "$intermediates_dir/conda/nextflow"