#!/usr/bin/env python3

import sys
import argparse
from ete3 import Tree

'''
The features (count and scientific name) added to the nodes and output in extended newick format aren't recognized by ggtree/treeio for plotting.
Annoying, but making the extra lookup metadata table is the quickeset workaround I think.

All leaves end up at different lengths since there are a variable number of clades between species and root. 
Seems like a difficult problem to solve, leave for when I'm trying to procrastinate on writing.
'''

# Argument parsing
parser = argparse.ArgumentParser("Creates phylogenetic tree from kmindex output")
parser.add_argument("-t", "--taxa", dest="taxa_file", type=str,  help="Taxa count file (tsv)", required=True)
parser.add_argument("-c", "--cutoff", dest="cutoff", type=float, help="Value which matches are cutoff under.", required=True)
parser.add_argument("-n", "--names", dest="names", type=str, help="NCBI names.dmp file. Default is /usr/share/names.dmp", required=False, default="/usr/share/names.dmp")
parser.add_argument("-s", "--nodes", dest="nodes", type=str, help="NCBI nodes.dmp file. Default is /usr/share/nodes.dmp", required=False, default="/usr/share/nodes.dmp")
parser.add_argument("-m", "--merged", dest="merged", type=str, help="NCBI merged.dmp file. Default is  /usr/share/merged.dmp", required=False, default="/usr/share/merged.dmp")
args = parser.parse_args()

''' 
./reads_tree.py -t count_taxa.txt -c 100
'''

###### UTILITIES #######

# Generator function for tokenizing file lines
def line_splitter(f, skip=False, sep="\t"):
    with open(f) as inputf:
        if skip:
            next(inputf)
        for line in inputf:
            yield line.lstrip().rstrip().split(sep)

# Finds shortest list length in an irregular list of lists
def find_min_list(list):
    list_len = [len(i) for i in list]
    return min(list_len)

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

#Looks for agreement in taxonomy of multiple hits to return lca taxonomy
def consensusHits(tl):
    for n in range(0,find_min_list(tl)):
        # Make set of taxids
        taxid_set = set()
        for tlist in tl:
            taxid_set.add(tlist[n])
        # If the taxids don't all agree, return the previous taxid
        if len(taxid_set) > 1:
            # If it's the first, return so it doesn't take the last item of a list
            if n == 0:
                return tl[0][0]
            else:
                return tl[0][n-1]
    # If no disagreement, return the last element
    return tl[0][find_min_list(tl)-1]

#Traces the path of a given taxid to root node, compiling taxids together
def collect_taxids(ti):
    return_taxids = []
    while (ti != "1"):
        try:
            return_taxids.append(ti)
            (ti , _level) = parent_dict[ti]
        #Catches if a taxid isn't present in names.dmp or nodes.dmp
        except KeyError as e:
            #print("Taxid: {} not found in either names.dmp or nodes.dmp, looking in merged.dmp".format(ti), file=sys.stderr)
            #Looks through merged.dmp for 
            for tokens in line_splitter(args.merged):
                found = False
				#If the taxid is found
                if tokens[0] == ti:
                    ti = tokens[2]
                    found = True
                    #print("Taxid: {} match found in merged.dmp".format(ti), file=sys.stderr)
                    break
            if not found:
                print("Taxid: {} not found in merged.dmp! Try downloading an updated taxdump".format(ti), file=sys.stderr)
                break
    return return_taxids[::-1]

###### SCRIPT ######

# Dictionary of everything present in output {taxid : count}
present_taxa_count = {}

# Dictionary of taxids to root {taxid = [0, 32, 90054, ...]}
fulltax = {}

# Populate dictionary
for l in line_splitter(args.taxa_file, sep=" "):
    if int(l[0]) >= int(args.cutoff):
        present_taxa_count[l[1]] = l[0]

# List of taxa present in results
pt_keys = list(present_taxa_count.keys())

# Full taxonomy to root {taxid = [0, 32, 90054, ...]}
fulltax = {}
for t in pt_keys:
    fulltax[t] = collect_taxids(t)

# Adds LCA for each pair of taxa present to dictionary. This fills out and connects the tree
for i in range(len(pt_keys)):
    for j in range(i+1, len(pt_keys)):
        # Gets LCA of taxa pair
        lca_tax = consensusHits([fulltax[pt_keys[i]], fulltax[pt_keys[j]]])
        # If LCA is not already added to dictionaries, add
        if lca_tax not in present_taxa_count:
            present_taxa_count[lca_tax] = 0
            fulltax[lca_tax] = collect_taxids(lca_tax)

# Find lowest parent node and create parent_child_table
parent_child_table = []
for t in present_taxa_count:
    root_node=True

    # Check if root node is present
    if len(fulltax[t]) == 1:
        parent_child_table.append(("Root", t, 1))
        continue

    # Otherwise loop through taxids back to root (starting one higher level than target taxa)
    for n, tid in enumerate(fulltax[t][-2::-1]):
        if tid in present_taxa_count:
            parent_child_table.append((tid, t, n+1))
            root_node=False
            break
        
    # If parent taxid wasn't found, this is root node
    if root_node:
        parent_child_table.append(("Root", t, 1))

# Create tree
taxa_tree = Tree.from_parent_child_table(parent_child_table)

# Add read count and scientifc name features
for node in taxa_tree.traverse():
    if node.name != "Root":
        node.add_features(count=present_taxa_count[node.name], sci_name=name_dict[node.name])

# Display ascii tree
print(taxa_tree.get_ascii(attributes=["count", "sci_name"], show_internal=True))

# Print extended newick format tree string
print(taxa_tree.write(features=["count", "sci_name"], format=1))

# Print metadata lookup table
for entry in present_taxa_count:
    print(f"{entry}\t{present_taxa_count[entry]}\t{name_dict[entry]}")