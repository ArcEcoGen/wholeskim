#!/usr/bin/env python3

import sys
import argparse

# Argument parsing
parser = argparse.ArgumentParser("Collapses taxa count file to genus level")
parser.add_argument("-t", "--taxa", dest="taxa_file", type=str,  help="Taxa count file: read count '\t' taxid", required=True)
parser.add_argument("-n", "--names", dest="names", type=str, help="NCBI names.dmp file. Default is /usr/share/names.dmp", required=False, default="/usr/share/names.dmp")
parser.add_argument("-s", "--nodes", dest="nodes", type=str, help="NCBI nodes.dmp file. Default is /usr/share/nodes.dmp", required=False, default="/usr/share/nodes.dmp")
parser.add_argument("-m", "--merged", dest="merged", type=str, help="NCBI merged.dmp file. Default is  /usr/share/merged.dmp", required=False, default="/usr/share/merged.dmp")
parser.add_argument("-c", "--cutoff", dest="cutoff", type=float, help="Minimum number of reads required (r)", required=True)
parser.add_argument("-a", "--sample", dest="sample", type=str, help="Output sample name", required=False, default="placeholder")
args = parser.parse_args()

''' 
./genus_collapse.py -t sample_count.tsv -c 1000 -n taxonomy/names.dmp -s taxonomy/nodes.dmp -m taxonomy/merged.dmp
'''

###### UTILITIES #######

# Generator function for tokenizing file lines
def line_splitter(f, skip=False):
    with open(f) as inputf:
        # If skipping first line
        if skip:
            next(inputf)
        for line in inputf:
            yield line.rstrip().split("\t")

# Check if tid is at taxon_level or below
def taxon_or_lower(tid, taxon_level):
    while tid != "1":
        if parent_dict[tid][1] == taxon_level:
            return True
        else:
            tid = parent_dict[tid][0]
    return False

# Check if tid is lower than taxon_level
def taxon_lower(tid, taxon_level):
    tid = parent_dict[tid][0]
    while tid != "1":
        if parent_dict[tid][1] == taxon_level:
            return True
        else:
            tid = parent_dict[tid][0]
    return False

# Returns genus of tid
def get_genus(tid):
    while tid != "1":
        if parent_dict[tid][1] == "genus":
            return tid
        else:
            tid = parent_dict[tid][0]
    raise Exception(f"Genus not found for {tid} {name_dict[tid]}")

####### TAXONOMY SET UP ##########

#Makes a dict of name and taxid {taxid : name}
name_dict = {}
for tokens in line_splitter(args.names):
    #Ignores synonyms, blast names, etc.
    if tokens[6] == "scientific name":
        name_dict[tokens[0]] = tokens[2]
print("Done loading taxid to name data - {}".format(len(name_dict)), file=sys.stderr)
name_dict["0"] = "unid"

#Makes the parent node dictionary {taxid : (parent_taxid, taxonomic_level)}
parent_dict = {}
for tokens in line_splitter(args.nodes):
    parent_dict[tokens[0]] = (tokens[2], tokens[4])
print("Done loading parent data - {}".format(len(parent_dict)), file=sys.stderr)

##### Script

# Read count to taxid {taxid : read_count}
reads_dict = {}

# Populates dictionary if read_count >= cutoff
for l in line_splitter(args.taxa_file):
    # If there are suficient reads and it's at family level or lower
    if int(l[0]) >= int(args.cutoff) and (taxon_or_lower(l[1], "family") or l[1] == "2"):
        reads_dict[l[1]] = int(l[0])

# Final dictionary of everything collapsed at genus level {taxid : read_count}
genus_dict = {}

# Loops though read_dict
for entry in reads_dict:
    # If at genus level or above (or Bacteria), just add to dictionary
    if not taxon_lower(entry, "genus") or entry == "2":
        if entry in genus_dict:
            genus_dict[entry] += reads_dict[entry]
        else:
            genus_dict[entry] = reads_dict[entry]
    # Else find genus taxid and add
    else:
        genus_taxid = get_genus(entry)
        if genus_taxid in genus_dict:
            genus_dict[genus_taxid] += reads_dict[entry]
        else:
            genus_dict[genus_taxid] = reads_dict[entry]

# output
for ent in sorted(genus_dict, key=genus_dict.get):
    print(f"{genus_dict[ent]}\t{genus_dict[ent] / ((args.cutoff + 0.1) * 10000)}\t{ent}\t{name_dict[ent]}\t{args.sample}")
