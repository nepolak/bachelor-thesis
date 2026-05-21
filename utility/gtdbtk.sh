#!/bin/bash
#SBATCH --time=48:00:00
#SBATCH --mem=160GB
#SBATCH --cpus-per-task=128
#SBATCH --partition=main

# This one relies on conda being defined in the bashrc. Make sure it is.
conda activate ./intermediates/conda/gtdbtk

gtdbtk classify_wf --out_dir $2 --skip_ani_screen --cpus 128 --genome_dir $1 --extension .fa

conda deactivate