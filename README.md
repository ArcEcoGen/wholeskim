# wholeskim

Documentation and code for wholeskim pipeline.

## Workflow

`prep_indices.sh input_directory kmer_size min_group_size max_group_size`

Creates optimimzed indices 

`kmindex query -i index_project -a -z 3 -f matrix -q query.fastq`

Queries indices with kmindex

`parse_kmindex.py -k kmindex_outputs -t index_to_taxid_map.txt`

Assigns reads to lowest common ancestor (LCA)

## Overview

```
project
|- doc/                documentation for the study
|
|- data/               raw and primary data, essentially all input files, never edit!
|  |- raw_external/
|  |- raw_internal/
|  |- meta/
|
|- code/               all code needed to go from input files to final results
|- notebooks/
|
|- intermediate/       output files from different analysis steps, can be deleted
|- scratch/            temporary files that can be safely deleted or lost
|- logs/               logs from the different analysis steps
|
|- results/            output from workflows and analyses
|  |- figures/
|  |- tables/
|  |- reports/
|
|- .gitignore          sets which parts of the repository that should be git tracked
|- Snakefile           project workflow, carries out analysis contained in code/
|- config.yml          configuration of the project workflow
|- environment.yml     software dependencies list, used to create a project environment
|- Dockerfile          recipe to create a project container
```
