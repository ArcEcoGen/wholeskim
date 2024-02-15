library(ggplot2)
library(dplyr)
library(plotly)

kmer_compare_1541 <- read.csv("~/Documents/paper_2/wholeskim/results/figures/kmer_count/1541_taxid_kmercount.txt", header=FALSE, sep = " ")
colnames(kmer_compare_1541) <- c("taxid", "wholeskim_kmer")
kmer_compare_contigs <- read.csv("~/Documents/paper_2/wholeskim/results/figures/kmer_count/contigs_split_kmercount_formatted.txt", header=FALSE, sep = " ")
colnames(kmer_compare_contigs) <- c("taxid", "contig_kmer")

kmer_full_compare <- full_join(kmer_compare_1541, kmer_compare_contigs, by = "taxid")

p <- ggplot(kmer_full_compare, aes(contig_kmer, wholeskim_kmer, label=taxid)) + geom_point() + 
  scale_x_continuous(trans="log") +
  scale_y_continuous(trans="log") +
  geom_abline()

ggplotly(p)
