#!/bin/bash -l

#### Programs in path ####
# ntcard
# kmtricks
# parallel

INPUTDIRECT=$1
KMER_SIZE=$2
MAX_GROUP=$3

# The minimum number of skims to be included in one group. Should be divisible by 8 for storage efficiency
MIN_GROUP=8

# The number of unique kmer difference to divide subsets
KMER_DIFF_THRESH=100000000

# Set this value to the number of CPUs available
# N_CPU=$(oarprint core | wc -l)
N_CPU=16

DIRECTBASE=$(basename $INPUTDIRECT)

# Check if kmer estimates have already been calculated
if [[ ! -f "${DIRECTBASE}_kmercount.tmp" ]]
then
	# Computes kmers for each file in directory (~20 seconds per file in directory)
	for f in $1*.fast?*
	do
		echo "echo \$(readlink -e $f) \$(ntcard -k $2 -o /dev/null $f 2>&1 | head -2 | tail -1) >> ${DIRECTBASE}_kmercount.tmp" 
	done | parallel -j $N_CPU
fi

# Sorts files by kmer size
cut -d " " -f 1,4 ${DIRECTBASE}_kmercount.tmp | sort -k 2 -r -n > ${DIRECTBASE}_kmercount_sorted.tmp

# Keeps track of number of subsets
SUBSETNUM=1

# Keeps track of previous largest uniq kmer count
BUFFER_KMER="0"

# Clears subset files
rm -f ${DIRECTBASE}_[0-9]*.txt

# Group minimum $MIN_GROUP number of files into kmtricks input files
while mapfile -t -n $MIN_GROUP ary && ((${#ary[@]}))
do
	LINE1=(${ary[0]})
	UNIQ_KMER=${LINE1[1]}
	
	# Check if a subset list already exists
	if [[ -f "${DIRECTBASE}_${SUBSETNUM}.txt" ]]
	then
		# Check if current subset has a large kmer difference.
		KMER_DIFF=$(($BUFFER_KMER - $UNIQ_KMER))
		>&2 echo $BUFFER_KMER $UNIQ_KMER $KMER_DIFF
		if [ $KMER_DIFF -ge $KMER_DIFF_THRESH ] || [ $(cat "${DIRECTBASE}_${SUBSETNUM}.txt" | wc -l) -ge $MAX_GROUP ]
		then
			>&2 echo "Running with kmer diff of $KMER_DIFF and UNIQ_KMER of $UNIQ_KMER"
			# If it does, build the index from the current list
			kmindex build --fof ${DIRECTBASE}_${SUBSETNUM}.txt --index ${DIRECTBASE}_proj --register-as ${DIRECTBASE}_${SUBSETNUM} --run-dir ${DIRECTBASE}_${SUBSETNUM}_index --kmer-size $KMER_SIZE -t $N_CPU --nb-partitions 10 --hard-min 1 --bloom-size $((UNIQ_KMER * 10))

			# Increment subset number and reset buffer kmer value
			((SUBSETNUM++))
			>&2 echo "Setting BUF from $BUFFER_KMER to ${LINE1[1]} from ${LINE1[0]}"
			BUFFER_KMER=${LINE1[1]}
		fi

	# If one does not exist (first set), initialize buffer value.
	else
		>&2 echo "FIRST: Setting BUF from $BUFFER_KMER to ${LINE1[1]} from ${LINE1[0]}"
		BUFFER_KMER=${LINE1[1]}
	fi
		
	# For each file in group, add info to kmtricks input file
	for i in "${ary[@]}"
	do
		FILENAME=${i[0]}
		BASENAME=$(basename $FILENAME)

		echo ${BASENAME%%.*} \: $(readlink -e $FILENAME) >> ${DIRECTBASE}_${SUBSETNUM}.txt
	done

done < ${DIRECTBASE}_kmercount_sorted.tmp

# Build the last subset, if it hasn't been done
if [[ ! -d "${DIRECTBASE}_${SUBSETNUM}_index" ]]
then
	>&2 echo "Building last subset index with UNIQ_KMER of $UNIQ_KMER"
	kmindex build --fof ${DIRECTBASE}_${SUBSETNUM}.txt --index ${DIRECTBASE}_proj --register-as ${DIRECTBASE}_${SUBSETNUM} --run-dir ${DIRECTBASE}_${SUBSETNUM}_index --kmer-size $KMER_SIZE -t $N_CPU --nb-partitions 10 --hard-min 1 --bloom-size $((UNIQ_KMER * 10))
fi