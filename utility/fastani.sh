#!/bin/bash
#SBATCH --time=48:00:00
#SBATCH --mem=4GB
#SBATCH --cpus-per-task=4
#SBATCH --partition=main

# This one relies on conda being defined in the bashrc. Make sure it is.
conda activate ./intermediates/conda/nextflow

srun nextflow -C nextflow.config run fastani.nf --inputs_folder=$1 --inputs_index=$2