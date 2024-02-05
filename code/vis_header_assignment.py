#!/usr/bin/env python3

import sys
import argparse

'''
Parsing kmindex output assingments individual read assignemnt
ASSUMES INPUT EDNA SAMPLE IS ENTIRELY FROM ONE TAXON

Input:
3504 header1, header2, header3
0 header4, header5
33090 header6
'''

parser = argparse.ArgumentParser("Parses kmindex output")
parser.add_argument("-k", "--kmindex", dest="kmindex", type=str, nargs="+", help="kmindex read and taxid", required=True)
parser.add_argument("-t", "--taxon", dest="taxon", type=str, help="True taxid of interest", required=True)
parser.add_argument("-c", "--cutoff", dest="cutoff", type=int, help="Minimum number of reads", required=True)
parser.add_argument("-n", "--names", dest="names", type=str, help="NCBI names.dmp file. Default is /usr/share/names.dmp", required=False, default="/usr/share/names.dmp")
parser.add_argument("-s", "--nodes", dest="nodes", type=str, help="NCBI nodes.dmp file. Default is /usr/share/nodes.dmp", required=False, default="/usr/share/nodes.dmp")
parser.add_argument("-m", "--merged", dest="merged", type=str, help="NCBI merged.dmp file. Default is /usr/share/merged.dmp", required=False, default="/usr/share/merged.dmp")
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

with open(f"header_target.txt", "a") as f_target, open(f"header_targenus.txt", "a") as f_targenus, open(f"header_tarfamily.txt", "a") as f_tarfamily, open(f"header_highertaxa.txt", "a") as f_highertaxa, open(f"header_offgenus.txt", "a") as f_offgenus, open(f"header_offfamily.txt", "a") as f_offfamily, open(f"header_miss.txt", "a") as f_miss, open(f"header_unid.txt", "a") as f_unid:
    
    # {taxid : [header1, header2, ...]}
    taxa_read_dict = {}

    for f in args.kmindex:
        for l_list in line_splitter(f, sep="\t"):
            taxa_read_dict[l_list[0]] = l_list[1].split(",")

        for taxid in taxa_read_dict:
            
            if len(taxa_read_dict[taxid]) < args.cutoff or taxid == "0":
                for header in taxa_read_dict[taxid]:
                    f_unid.write(f"{header}\n")
                
            elif taxid == args.taxon or check_level(taxid, relevant_taxids, "species"):
                for header in taxa_read_dict[taxid]:
                    f_target.write(f"{header}\n")
            
            # Matches at a higher taxonomic level
            elif taxid in relevant_taxids:
                if parent_dict[taxid][1] == "genus":
                    for header in taxa_read_dict[taxid]:
                        f_targenus.write(f"{header}\n")
                
                elif parent_dict[taxid][1] == "family":
                    for header in taxa_read_dict[taxid]:
                        f_tarfamily.write(f"{header}\n")
                
                else:
                    for header in taxa_read_dict[taxid]:
                        f_highertaxa.write(f"{header}\n")
            
            elif check_level(taxid, relevant_taxids, "genus"):
                for header in taxa_read_dict[taxid]:
                    f_offgenus.write(f"{header}\n")
            
            elif check_level(taxid, relevant_taxids, "family"):
                for header in taxa_read_dict[taxid]:
                    f_offfamily.write(f"{header}\n")
            
            else:
                for header in taxa_read_dict[taxid]:
                    f_miss.write(f"{header}\n")