#!/bin/bash

mkdir -P intermediates/cwd/fastANI
cd intermediates/cwd/fastANI

sbatch ../../../utility/fastani.sh ../../mags ../../mags_to_cluster.csv