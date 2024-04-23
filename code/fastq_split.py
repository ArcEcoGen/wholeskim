#!/usr/bin/env python3

import argparse
import sys

'''
Script for subsetting a fasta file with reads from taxa of interest
Make it so the script only load acc2tax for reads that are present. FILE IS TOO BIG

Could be uglier!
'''

# Argument parsing
parser = argparse.ArgumentParser("Subsets fastq files into identified fastqs")
parser.add_argument("-t", "--taxids", dest="taxids", type=str, nargs="+", help="Taxids of interest", required=True)
parser.add_argument("-w", "--wholeskim", dest="wholeskim", type=str, help="wholeskim output", required=True)
parser.add_argument("-f", "--fastq", dest="fasta", type=str, help="Fasta file", required=True)
args = parser.parse_args()

# Generator function for tokenizing file lines
def line_splitter(f):
    with open(f) as inputf:
        for line in inputf:
            yield line.rstrip().split("\t")

# Populate dictionary of reads based on assigned taxa
# {taxid : [read1, read2, ...]}
taxid_read_dict = {}
for l in line_splitter(args.wholeskim):
    if l[4] in taxid_read_dict:
        taxid_read_dict[l[4]].append(l[0])
    else:
        taxid_read_dict[l[4]] = [l[0]]

# Main body
with open(args.fasta) as input_file:
	
    curr_taxid = ""
    header = ""
    body = []

    output_chunk = ""

    for line in input_file:

	    #First line to initialize
        if line.startswith(">") and not header:
            header = line.rstrip()
            h_query = header.lstrip(">")

            # Looks for header in all acc2tax dicts
            for d in acc2tax_dicts:
                if h_query in d:
                    curr_taxid = d[h_query]
                    break
            if curr_taxid == "":
                print(f"Header not found: {h_query}")
                break

        # Sequence section
        elif not line.startswith(">"):
            body.append(line.rstrip())

        # Next sequence
        else:

            h_query = line.rstrip().lstrip(">")
            q_taxid = ""
            # Looks for header in all acc2tax dicts
            for d in acc2tax_dicts:
                if h_query in d:
                    q_taxid = d[h_query]
                    break
            # Header not found, broken!
            if q_taxid == "":
                print(f"Header not found: {h_query}")
                break

            # Same output file
            if q_taxid == curr_taxid:
                output_chunk += f"{header}\n"
                for s in body:
                    output_chunk += f"{s}\n"

            # Diffent output file, write chunk
            else:
        
                with open(f"{curr_taxid}-contig.fasta", "a") as out_f:
                    out_f.write(output_chunk)
                    output_chunk = ""

                # Reset curr_taxid
                for d in acc2tax_dicts:
                    if h_query in d:
                        curr_taxid = d[h_query]
                        break
                if curr_taxid == "":
                    print(f"Header not found: {h_query}")
                    break

            header = line.rstrip()
            body = []
        
    with open(f"{curr_taxid}-contig.fasta", "a") as out_f:
        out_f.write(output_chunk)
                
