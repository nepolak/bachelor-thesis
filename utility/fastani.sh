#!/bin/bash
#SBATCH --time=48:00:00
#SBATCH --mem=4GB
#SBATCH --cpus-per-task=4
#SBATCH --partition=main

# This one relies on conda being defined in the bashrc. Make sure it is.
eval "$(conda shell.bash hook)"
conda activate $5

srun nextflow -C $1 run $2 --inputs_folder=$3 --inputs_index=$4