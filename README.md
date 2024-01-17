# wholeskim

Documentation and code for wholeskim pipeline.

## Workflow

`prep_indices.sh`: Create optimimzed indices from genome skims

`kmindex`: Query indices with eDNA sequences

`parse_kmindex.py`: Assign reads to lowest common ancestor (LCA)

## Overview

```
project
|- doc/                documentation for the study
|
|- data/               raw and primary data, essentially all input files, never edit!
|  |- example_workflow
|     |- input
|     |- output
|
|- code/               all code needed to go from input files to final results
|
|- intermediate/       output files from different analysis steps, can be deleted
|- scratch/            temporary files that can be safely deleted or lost
|- logs/               logs from the different analysis steps
|
|- results/            output from workflows and analyses
|  |- figures/
|  |- tables/
|
|- dockerfile          recipe to create a project container
```

## Example workflow

The following is a short tutorial on using `wholeskim` with 5 reference genome skims and simulated eDNA reads.

```
| Species               | Taxon ID | Sequencing code |
|-----------------------|----------|-----------------|
| Betula nana           | 1623466  | BMB_CC          |
| Carex maritima        | 240694   | BMB_BQ          |
| Empetrum nigrum       | 191066   | BXA_CKW         |
| Vaccinium uliginosum  | 190548   | CDM_APU         |
| Vaccinium vitis-idaea | 180772   | BMB_HT          |
```

Launch the docker image interactively and mount the `data/` directory in the container so all files are accessible

`docker run -v ./data:/root/data -it wholeskim_image`

Create indices for the genome skims provided. `prep_indices.sh` will index every fastx file present in the provided directoy. KMER_SIZE is set to 31 and a MAX_GROUP size is set to 8 (which is irrelevant since there are only 5 skims present).
```
cd data/example_project
prep_indices.sh genome_skims/ 31 8 8
```
Query the indices with simulated eDNA *Vaccinium uliginosum* reads. 

`kmindex query -i genome_skims_proj/ -z 3 -t 1 -f matrix -q vaculi_merged.fastq -o genome_skim_out`