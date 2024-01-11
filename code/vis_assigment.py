#!/usr/bin/env python3

import sys
import argparse

'''
Parsing kmindex output assingments for visualization
Do cut -f 5 | sort | uniq -c before processing
Files must end in cutoff #
'''

parser = argparse.ArgumentParser("Parses kmindex output")
parser.add_argument("-k", "--kmindex", dest="kmindex", type=str, nargs="+", help="kmindex taxa count", required=True)
parser.add_argument("-n", "--names", dest="names", type=str, help="NCBI names.dmp file.", required=False, default="/usr/share/names.dmp")
parser.add_argument("-s", "--nodes", dest="nodes", type=str, help="NCBI nodes.dmp file.", required=False, default="/usr/share/nodes.dmp")
parser.add_argument("-m", "--merged", dest="merged", type=str, help="NCBI merged.dmp file.", required=False, default="/usr/share/merged.dmp")
parser.add_argument("-t", "--taxon", dest="taxon", type=str, help="True taxon of interest", required=True)
parser.add_argument("-c", "--cutoff", dest="cutoff", type=int, help="Minimum number of reads", required=True)
parser.add_argument("-x", "--suffix", dest="suffix", type=str, help="Suffix to output to taxa name", required=False, default="")
args = parser.parse_args()

# Utilities

# Generator function for tokenizing file lines
def line_splitter(f, skip=False, sep="\t"):
    with open(f) as inputf:
        if skip:
            next(inputf)
        for line in inputf:
            yield line.rstrip().lstrip().split(sep)

### Taxonomy setup #####

#Makes a dict of name and taxid {taxid : name}
name_dict = {}
for tokens in line_splitter(args.names):
	#Ignores synonyms, blast names, etc.
	if tokens[6] == "scientific name":
		name_dict[tokens[0]] = tokens[2]
print("Done loading taxid to name data - {}".format(len(name_dict)), file=sys.stderr)

#Makes the parent node dictionary {taxid : (parent_taxid, taxonomic_level)}
parent_dict = {}
for tokens in line_splitter(args.nodes):
	parent_dict[tokens[0]] = (tokens[2], tokens[4])
print("Done loading parent data - {}".format(len(parent_dict)), file=sys.stderr)

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
                print("Taxid: {} not found in merged.dmp either! Try downloading an updated taxdump".format(ti), file=sys.stderr)
                break
    return return_taxids[::-1]

# Returns True if "ti" has same taxonomic level (level_name) as target
def check_level(ti, rel_list, level_name):
    query_ti_list = collect_taxids(ti)

    # Gets genus from query taxid
    query_level = ""
    for t in query_ti_list:
        try:
            if parent_dict[t][1] == level_name:
                query_level = t
                break
        except KeyError as e:
            #Looks through merged.dmp for
            for tokens in line_splitter(args.merged):
                found = False
				#If the taxid is found
                if tokens[0] == t:
                    t = tokens[2]
                    found = True
                    #print("Taxid: {} match found in merged.dmp".format(ti), file=sys.stderr)
                    break
            if not found:
                print("Taxid: {} not found in merged.dmp! Try downloading an updated taxdump".format(ti), file=sys.stderr)
                break
            if parent_dict[t][1] == level_name:
                query_level = t
                break
    
    # Gets genus from target taxid
    target_level = ""
    for t  in rel_list:
        try:
            if parent_dict[t][1] == level_name:
                target_level = t
                break
        except KeyError as e:
            #Looks through merged.dmp for
            for tokens in line_splitter(args.merged):
                found = False
				#If the taxid is found
                if tokens[0] == t:
                    t = tokens[2]
                    found = True
                    #print("Taxid: {} match found in merged.dmp".format(ti), file=sys.stderr)
                    break
            if not found:
                print("Taxid: {} not found in merged.dmp! Try downloading an updated taxdump".format(ti), file=sys.stderr)
                break
            if parent_dict[t][1] == level_name:
                target_level = t
                break

    if target_level == query_level and target_level != "" and query_level != "":
        return True
    else:
        return False


## SCRIPT ###

relevant_taxids = collect_taxids(args.taxon)

for f in args.kmindex:

    taxa_readcount = {"unid" : 0, "off_target" : 0, "off_genus" : 0, "off_family" : 0, "target" : 0, "higher_taxa": 0, "higher_genus" : 0, "higher_family" : 0}
    cutoff = f.split(".")[0].split("_")[0]

    for l_list in line_splitter(f, sep=" "):
        if int(l_list[0]) < args.cutoff or l_list[1] == "0":
            taxa_readcount["unid"] += int(l_list[0])
        elif l_list[1] == args.taxon or check_level(l_list[1], relevant_taxids, "species"):
            taxa_readcount["target"] += int(l_list[0])
        # Matches at a higher taxonomic level
        elif l_list[1] in relevant_taxids:
            if parent_dict[l_list[1]][1] == "genus":
                taxa_readcount["higher_genus"] += int(l_list[0])
            elif parent_dict[l_list[1]][1] == "family":
                taxa_readcount["higher_family"] += int(l_list[0])
            else:
                taxa_readcount["higher_taxa"] += int(l_list[0])
        elif check_level(l_list[1], relevant_taxids, "genus"):
            taxa_readcount["off_genus"] += int(l_list[0])
        elif check_level(l_list[1], relevant_taxids, "family"):
            taxa_readcount["off_family"] += int(l_list[0])
        else:
            taxa_readcount["off_target"] += int(l_list[0])

        
    # Output
    for item in taxa_readcount:
        try:
            print(f"{cutoff}{args.suffix}\t{item}\t{name_dict[item]}\t{parent_dict[item][1]}\t{taxa_readcount[item]}")
        except KeyError as e:
            if item == "unid":
                print(f"{cutoff}{args.suffix}\t{item}\t{'unid'}\t{'unid'}\t{taxa_readcount[item]}")
            elif item == "off_target":
                print(f"{cutoff}{args.suffix}\t{item}\t{'off_target'}\t{'off_target'}\t{taxa_readcount[item]}")
            elif item == "off_genus":
                print(f"{cutoff}{args.suffix}\t{item}\t{'genus'}\t{'genus'}\t{taxa_readcount[item]}")
            elif item == "off_family":
                print(f"{cutoff}{args.suffix}\t{item}\t{'family'}\t{'family'}\t{taxa_readcount[item]}")
            elif item == "target":
                print(f"{cutoff}{args.suffix}\t{item}\t{'target'}\t{'target'}\t{taxa_readcount[item]}")
            elif item == "higher_taxa":
                print(f"{cutoff}{args.suffix}\t{item}\t{'higher_taxa'}\t{'higher_taxa'}\t{taxa_readcount[item]}")
            elif item == "higher_genus":
                print(f"{cutoff}{args.suffix}\t{item}\t{'higher_genus'}\t{'higher_genus'}\t{taxa_readcount[item]}")
            elif item == "higher_family":
                print(f"{cutoff}{args.suffix}\t{item}\t{'higher_family'}\t{'higher_family'}\t{taxa_readcount[item]}")
                



