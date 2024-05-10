#!/usr/bin/env python3

import sys
import argparse

# Argument parsing
parser = argparse.ArgumentParser("Collapses taxa count file to genus level")
parser.add_argument("-t", "--taxa", dest="taxa_file", type=str,  help="Taxa count file: read count '\t' taxid", required=True)
parser.add_argument("-n", "--names", dest="names", type=str, help="NCBI names.dmp file. Default is /usr/share/names.dmp", required=False, default="/usr/share/names.dmp")
parser.add_argument("-s", "--nodes", dest="nodes", type=str, help="NCBI nodes.dmp file. Default is /usr/share/nodes.dmp", required=False, default="/usr/share/nodes.dmp")
parser.add_argument("-m", "--merged", dest="merged", type=str, help="NCBI merged.dmp file. Default is  /usr/share/merged.dmp", required=False, default="/usr/share/merged.dmp")
parser.add_argument("-r", "--reads", dest="reads_total", type=float, help="Total number of reads in sample", required=True)
parser.add_argument("-c", "--cutoff", dest="cutoff", type=float, help="Minimum proportion of reads required (r)", required=True)
parser.add_argument("-a", "--sample", dest="sample", type=str, help="Output sample name", required=False, default="placeholder")
args = parser.parse_args()

''' 
./genus_collapse.py -t sample_count.tsv -c 0.0001 -r 1000000 -n taxonomy/names.dmp -s taxonomy/nodes.dmp -m taxonomy/merged.dmp
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

# Checks if taxid is a member of taxid_2
def check_member(tid, tid_2):
    while tid != "1":
        if parent_dict[tid][0] == tid_2:
            return True
        else:
            tid = parent_dict[tid][0]
    return False


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

    # Check if taxid is in parent_dict, otherwise use merged
    try:
        if parent_dict[l[1]]:
            curr_taxid = l[1]
    except KeyError as e:
        #Looks through merged.dmp for
        for tokens in line_splitter(args.merged):
            found = False
            #If the taxid is found
            if tokens[0] == l[1]:
                curr_taxid = tokens[2]
                found = True
                #print("Taxid: {} match found in merged.dmp".format(ti), file=sys.stderr)
                break
        if not found:
            print("Taxid: {} not found in merged.dmp! Try downloading an updated taxdump".format(ti), file=sys.stderr)
            break

    # If it's at family level or lower
    if taxon_or_lower(curr_taxid, "family") or l[1] == "2":
        reads_dict[curr_taxid] = int(l[0])

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

# Calculates number of Embyophyta reads
embryo_reads = 0
for entry in genus_dict:
    if check_member(entry, "3193"):
        embryo_reads += genus_dict[entry]

# Sets minimum reads cutoff for taxa presence
min_reads = embryo_reads * args.cutoff

######### UGLY SETTING HARD CUTOFF ##############
if min_reads < 10:
    min_reads = 10

print(f"Embryophta reads: {embryo_reads}\t{embryo_reads / args.reads_total}", file=sys.stderr)

# output
for ent in sorted(genus_dict, key=genus_dict.get):
    if genus_dict[ent] >= min_reads:
        print(f"{genus_dict[ent]}\t{genus_dict[ent] / embryo_reads}\t{genus_dict[ent] / args.reads_total}\t{ent}\t{name_dict[ent]}\t{args.sample}")
