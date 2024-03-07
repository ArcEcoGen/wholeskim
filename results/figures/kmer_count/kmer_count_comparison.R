library(ggplot2)
library(dplyr)
library(plotly)

kmer_compare_1541 <- read.csv("~/Documents/paper_2/wholeskim/results/figures/kmer_count/1541_taxid_kmercount.txt", header=FALSE, sep = " ")
colnames(kmer_compare_1541) <- c("taxid", "wholeskim_kmer")
kmer_compare_contigs <- read.csv("~/Documents/paper_2/wholeskim/results/figures/kmer_count/contigs_split_kmercount_formatted.txt", header=FALSE, sep = " ")
colnames(kmer_compare_contigs) <- c("taxid", "contig_kmer")

kmer_full_compare <- full_join(kmer_compare_1541, kmer_compare_contigs, by = "taxid")

kmer_full_compare <- kmer_full_compare %>% mutate(ratio = wholeskim_kmer/contig_kmer)
                            
ggplot(kmer_full_compare, aes(x=ratio)) + 
  geom_density(linewidth=3) +
  scale_x_continuous(trans="log", breaks = c(1,10,100), name = "Genome skim k-mer count / Contig k-mer count") +
  ylab("Density") +
  theme_bw() +
  theme(axis.line = element_line(colour = "black"),
        panel.border = element_blank(),
        text=element_text(size=17),
        axis.title.y = element_text(margin = margin(t = 0, r = 20, b = 0, l = 0))) +
  ggtitle("A.")

p <- ggplot(kmer_full_compare, aes(contig_kmer, wholeskim_kmer, label=taxid)) + geom_point() + 
  scale_x_continuous(trans="log") +
  scale_y_continuous(trans="log") +
  geom_abline()

ggplotly(p)

# PLot the ratio per family (bar plot)