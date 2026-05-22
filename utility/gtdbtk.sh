#!/bin/bash
#SBATCH --time=48:00:00
#SBATCH --mem=160GB
#SBATCH --cpus-per-task=128
#SBATCH --partition=main

# This one relies on conda being defined. Make sure it is.
eval "$(conda shell.bash hook)"
conda activate $2

gtdbtk classify_wf --out_dir gtdb_out --skip_ani_screen --cpus 128 --genome_dir $1 --extension .fa

conda deactivate