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

The following is a short tutorial on using `wholeskim` with 5 reference genome skims and simulated eDNA reads. Note these skims have been truncated to 75 000 reads for the purposes of this example.

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

`cd data/example_workflow/output`
`prep_indices.sh /root/data/example_workflow/input/example_skims/ 31 8`

Query the indices with simulated eDNA *Vaccinium uliginosum* reads.

`kmindex query -i example_skims_proj/ -z 3 -t 1 -f matrix -q /root/data/example_workflow/input/vaculi_merged.fastq -o exskims_out`

Assign LCA to each read. `sampleID_taxid.txt` is a map of the genome skim IDs (column headers in kmindex output) to taxid.

`parse_kmindex.py -k exskims_out/example_skims_1.tsv -t /root/data/example_workflow/input/sampleID_taxid.txt > exskims_lca.tsv`

The output has the following columns:

```
Read header
Read length (if provided)
Maximum proportion identity
Number of matches above proportion identity cutoff value (default = 0.7)
Taxid of LCA
Scientific name of LCA
```

Summarize the number of reads assigned to each taxa.

`cut -f 6 exskims_lca.tsv | sort | uniq -c | sort -n > exskims_lca_summary.txt`

Optionally check the accuracy of assignments to one specific taxon of interest (in this case *V. uliginosum* with taxid 190548). This script assumes all input reads come from the taxon of interest (i.e. any other assignments are considered wrong, this script is only informative for a simulated dataset). Taxa with less than the cutoff number of reads are considered to be artifacts and added to the "unidentified" total (recommended setting this to 0.001% of the number of input reads).

`vis_assignment.py --kmindex exskims_lca_summary.txt --taxon 190548 --cutoff 2`

Subset all reads that match exactly to *V. uliginosum*. `sed` portion of this command might be necessary to avoid matching more than one sequence. 

`grep -P "\t190548\t" exskims_lca.tsv | cut -f 1 | sed -i 's/$/ /' | grep -f - -A 3 --no-group-separator ../input/vaculi_merged.fastq > exskims_vaculi.fastq`