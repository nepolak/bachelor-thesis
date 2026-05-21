# Characterizing the genomic diversity of prevalent gut microbiome bacterial species using metagenome-assembled genomes

This repository as attached to BSc thesis in that topic. Here are the tools I used to produce the results I described in the thesis. 

## Project structure
As some of stuff done here requires significantly more computation power than available in an average desktop PC, it is assumed that the work here is done on cluster. In particular, cluster that is working on SLURM. 
Make sure your .bashrc includes conda, as it's used here to load environment when scheduling jobs.

### Tools

The files describing steps here are written in Jupyter Notebook to allow investigation of datasets in the middle of pipeline. Python version is assumed to be 3.14.4.
Files in `src` contain Python code which I decided to not include in the notebooks. 
Files in `conda_defs` define environment files for conda.
Files in `utility` contain scripts I used.

### Artifacts

Code produces several artifacts. In particular, in `intermediate` folders there are produced .csv files with intermediate data. Some of them are used to avoid doing expensive operations several times.

The `output` folder contains the figures for the thesis.

### Nextflow

You probably should tune the nextflow config to the liking of your machine.

## Workflow

First thing, create the venv to be used in this project and install necessary packages. Use this venv as kernel for jupyter notebook.
```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
```
Then, create conda environments for gtdbtk and nextflow. The definitions are in `conda_defs`. You can replace `conda` with any conda-like package manager of your choice.
```bash
conda env create --prefix ./intermediates/conda/gtdbtk --file conda_defs/gtdbtk.yaml
conda env create --prefix ./intermediates/conda/nextflow --file conda_defs/nextflow.yaml
```

Then the workflow proceeds this way:
- Preprocessing in `pre_classify.ipynb`
- Classification with `gtdbtk`
- Processing in `classified.ipynb`
- Many-to-many comparison with `fastANI`
- Processing in `compared.ipynb`

### Preprocessing

Here the sample metadata is downloaded, we scrape genomes metadata from SPIRE, and download the MAGs for them. Then we filter samples (age, source), filter genomes (completeness, contamination) and store it in an intermediate file.

- `intermediates/core_scraped_genomes.csv` - will contain scraped genomes
- `intermediates/mags` - will contain downloaded MAGs
- `intermediates/mags_to_classify.csv` - Metadata of MAGs that will be passed to gtdbtk
- `output/figures/pyramid_panel.svg` - Panel with population structures.

### Classification

Run the classification on cluster:

```bash
bash utility/classify_slurm.sh
```
The results will be stored in `intermediates/cwd/gtdbtk/gtdb_out`. They will be used in next step.

### Processing classified MAGs

Here we select the prevalent species across the selected countries, rank them by prevalence score, and prepare them for fastANI comparisons. Intermediates stored:

- `intermediates/mags_classified.csv` - Metadata of MAGs with `classification` column with species name coming from gtdbtk results.
- `intermediates/mags_to_cluster.csv` - Metadata of MAGs from five prevalent species that will be passed to fastANI. 

### Many-to-many comparison

Run the comparison on cluster:

```bash
bash utility/fastani_slurm.sh
```
The results will be stored in `intermediates/cwd/fastANI/fastani_results`. These are raw matrices with comparisons.

### Processing compared MAGs

Here we build the clustermaps and histograms from fastANI comparisons.

- `output/figures/{species}` - per-species folder with panels.
- `output/figures/{species}/{country}.svg` - per-country clustermap-histogram panel for given species
- `output/figures/{species}/Pooled.svg` - pooled clustermap for given species
- `output/figures/{species}/Multi.svg` - panel with four clustermap with each country and pooled for given species

## Inclusion of figures

As the thesis was done in Google, which is evil, Docs that doesn't allow SVG figures, I had to convert them all to PNG with the 300 DPI as said by the guideline. For this, I used script `utility/convert_figures_to_png.sh` that walks the output folder recursively and creates a .png for each .svg found. It assumes Inkscape installed and available in the environment, though.