#!/usr/bin/env python3

import sys
import argparse
import re

# Argument parsing
parser = argparse.ArgumentParser("Parses kmindex output")
parser.add_argument("-k", "--kmindex", dest="kmindex", type=str, nargs="+", help="kmindex output file (tsv)", required=True)
parser.add_argument("-t", "--taxa", dest="taxa_file", type=str,  help="Mapping file of ID to taxa (tsv)", required=True)
parser.add_argument("-i", "--ID", dest="search_ID", type=str, help="IDs of reads that will be output (regex supported)", required=False, default=".*")
parser.add_argument("-n", "--names", dest="names", type=str, help="NCBI names.dmp file.", required=False, default="/usr/share/names.dmp")
parser.add_argument("-s", "--nodes", dest="nodes", type=str, help="NCBI nodes.dmp file.", required=False, default="/usr/share/nodes.dmp")
parser.add_argument("-m", "--merged", dest="merged", type=str, help="NCBI merged.dmp file.", required=False, default="/usr/share/merged.dmp")
parser.add_argument("-c", "--cutoff", dest="cutoff", type=float, help="Value which matches are cutoff under (def=0.7)", required=False, default=0.7)
parser.add_argument("-l", "--lengths", dest="lengths", type=str, help="File of header names and sequences lengths", required=False)
args = parser.parse_args()

''' 
./parse_kmindex.py -k skim.tsv -t sampleID_taxid.txt -i GCF -n taxonomy/names.dmp -s taxonomy/nodes.dmp -m taxonomy/merged.dmp
'''

###### UTILITIES #######

# Removes a suffix from string
def removesuffix(s, suf):
    if suf and s.endswith(suf):
        return s[:-len(suf)]
    return s

# Generator function for tokenizing file lines
def line_splitter(f, skip=False):
    with open(f) as inputf:
        if skip:
            next(inputf)
        for line in inputf:
            yield line.rstrip().split("\t")

# Finds shortest list length in an irregular list of lists
def find_min_list(list):
    list_len = [len(i) for i in list]
    return min(list_len)

####### TAXONOMY SET UP ##########

#Due to dictionary's unordered nature, this is necessary a couple places
tax_order = ["species", "genus", "family", "order", "class", "phylum"]

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

#Traces the path of a given taxid to root node, compiling taxonomy names along the way and returning a dict
def parseToRoot(ti):
	taxonomy = {
		"phylum" : "NA", 
		"class" : "NA",
		"order" : "NA",
		"family" : "NA",
		"genus" : "NA",
		"species" : "NA"
	}
    # If unidentified
	if ti == "0":
		return taxonomy

	#While not at the root node
	while (ti != "1"):
		#Adds names to taxonomy dictionary while tracing rootward
		try:
			level_name = name_dict[ti]
			(ti,level) = parent_dict[ti]
			if level in taxonomy:
				taxonomy[level] = level_name
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
			
	return taxonomy


######## SCRIPT ##########

# Dictionary of {fastq_header : length}
if args.lengths:
    seq_length = {}
    for seq in line_splitter(args.lengths):
        seq_length[seq[0][1:]] = seq[1]

# Dictionary of {seqID (column header in kmindex output) : taxid}
taxa_dict = {}
# Load taxa dictionary
for m in line_splitter(args.taxa_file):
    taxa_dict[m[0]] = m[1]

# Loops through kmindex output files
kmindex_dict = {}
for kmind in args.kmindex:
    
    # Makes a lookup dict for column header {i : header}
    with open(kmind) as kmindex_file:
        header_lookup = {}
        line_list = kmindex_file.readline().rstrip().split("\t")
        for i, t in enumerate(line_list[1:]):
            # Remove suffix is just for phylonorway weirdness
            header_lookup[i] = removesuffix(removesuffix(t,"OSDA_0_33090"), "OSW_0_33090")

    # Loops through reads
    for l in line_splitter(kmind, True):

        # Kmindex 0.2.0 adds "name:" to the beginning of each read
        read_name = ":".join(l[0].split(":")[1:])

        site_list = []
        for i, n in enumerate(l[1:]):
            # Only adds to list if a match is greater than n
            if float(n) > args.cutoff:
                site_list.append((n, header_lookup[i]))   
    
        # If there are hits
        if site_list:
            # Checks if the read has already been added to the dictionary
            if read_name in kmindex_dict:
                kmindex_dict[read_name] += site_list
            else:
                kmindex_dict[read_name] = site_list

        else:
             # Checks if the read has already been added to the dictionary
            if read_name not in kmindex_dict:
                kmindex_dict[read_name] = []

# Makes a list of reads of interest and sorts hits
reads_list = []
for n in kmindex_dict.keys():

    # If the read hits are empty, adds empty hit
    if kmindex_dict[n] == []:
        kmindex_dict[n] = [(0.0, "1")]
    # Else sorts the hits
    else:
        kmindex_dict[n].sort(key = lambda x : x[0], reverse=True)

    # Make list of reads
    if re.match(args.search_ID, n):
        reads_list.append(n)

# {taxid : {"phylum" : "name", }}
fulltax_dict = {}

# Loops through results
for r in reads_list:
    # If only one hit, print it
    if len(kmindex_dict[r]) == 1:
        # If match is empty
        if kmindex_dict[r][0][1] == "1":
            tid = "0"
            matches = 0
            max_ID = 0.0
        # If there's only one match
        else:
            tid = taxa_dict[kmindex_dict[r][0][1]]
            matches = 1
            max_ID = kmindex_dict[r][0][0]    
        
        taxonomy = parseToRoot(tid)

    # Else, get consensus taxonomy
    else:
        taxid_list = []
        max_ID = float(kmindex_dict[r][0][0])

        # For taxa in result
        for ti in kmindex_dict[r]:

            # If there is a bigger difference than 0.1 between matches, break
            if max_ID - float(ti[0]) > 0.1:
                break
            
            # Convert sample ID to taxa id
            tid = taxa_dict[ti[1]]

            if not tid in fulltax_dict:
                fulltax_dict[tid] = collect_taxids(tid)
            
            taxid_list.append(fulltax_dict[tid])

        tid = consensusHits(taxid_list)
        taxonomy = parseToRoot(tid)
        matches = len(kmindex_dict[r])

    # Adds length information if provided
    if args.lengths:
        first_columns = f"{r}\t{seq_length[r]}"
    else:
        first_columns = f"{r}\tNA"

    # Output
    try:
        print(f"{first_columns}\t{max_ID}\t{matches}\t{tid}\t{name_dict[tid]}", end="")
    #Catches if a taxid isn't present in names.dmp or nodes.dmp
    except KeyError as e:
        #print("Taxid: {} not found in either names.dmp or nodes.dmp, looking in merged.dmp".format(ti), file=sys.stderr)
        #Looks through merged.dmp for 
        for tokens in line_splitter(args.merged):
            found = False
			#If the taxid is found
            if tokens[0] == tid:
                tid = tokens[2]
                found = True
                #print("Taxid: {} match found in merged.dmp".format(ti), file=sys.stderr)
                break
        if not found:
            print("Taxid: {} not found in merged.dmp! Try downloading an updated taxdump".format(ti), file=sys.stderr)
            break
        print(f"{first_columns}\t{max_ID}\t{matches}\t{tid}\tunk_{tid}", end="")
    
    for l in tax_order:
        print(f"\t{taxonomy[l]}", end="")
    print()
    
    