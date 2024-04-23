library(ggtree)
library(treeio)
library(tidytree)
library(ggplot2)
library(scales)
library(ggtext)

tree <- read.newick("../wholeskim/code/test_tree.nwk")
x <- as_tibble(tree)

tree_meta <- read.csv("test_tree.tsv", sep="\t", header=FALSE, colClasses = c("character", "numeric", "character"))
colnames(tree_meta) <- c("label", "count", "sci_name")

y <- full_join(x, tree_meta, by="label")
y_phylo <- as.treedata(y)

ggtree(y_phylo, aes(color=count)) + geom_nodepoint(aes(size=count), alpha=0.7) + 
  geom_tippoint(aes(size=count), alpha=0.7) +
  geom_tiplab(aes(label=sci_name), color="black") + 
  geom_nodelab(aes(label=sci_name), nudge_x = 0.4, nudge_y = 0.4, color="black") +
  scale_size(range = c(0,40)) + 
  scale_color_viridis_c()

############### REAL TREE ####################

tree <- read.newick("~/Documents/paper_2/wholeskim/results/figures/betnan.nwk")
x <- as_tibble(tree)

tree_meta <- read.csv("~/Documents/paper_2/wholeskim/results/figures/betnan.tsv", sep="\t", header=FALSE, colClasses = c("character", "numeric", "character"))
colnames(tree_meta) <- c("label", "count", "sci_name")

tree_meta[,3] <- gsub("\\n", "\n", tree_meta[,3], fixed = TRUE)

y <- full_join(x, tree_meta, by="label")
#y <- mutate(y, sci_name = ifelse(sci_name == "Betula nana subsp. nana", "**Betula nana subsp. nana**", sci_name))
y_phylo <- as.treedata(y)

ggtree(y_phylo, aes(color=count)) + geom_nodepoint(aes(size=count), alpha=0.7) + 
  geom_tippoint(aes(size=count), alpha=0.7) +
  #geom_richtext(aes(label=sci_name)) +
  geom_tiplab(aes(label=sci_name), color="black", nudge_x = 0.03, size=4) + 
  geom_nodelab(aes(label=sci_name), vjust = -0.45, hjust = -0.07, color="black", angle = 90, size=4) +
#  scale_color_stepsn(low = "#ff5d5dff", high = "#73D055FF", nice.breaks = TRUE, limits=c(0, 40000), breaks=seq(0, 40000, by=10000)) +
  scale_color_gradientn(colors = c("#ff5d5dff", "#f68f46ff","#fde725", "#73D055FF"), limits=c(0, 46000), values=c(0,0.05,0.15,1), breaks=c(0,400,8000,46000)) +
  scale_size_continuous(range = c(0,16), limits=c(0, 46000), breaks=c(0,400,8000,46000)) +
  guides(color= guide_legend(title="Read count"), size=guide_legend(title = "Read count")) + 
  theme(legend.position = c(0.15, 0.85),
        plot.title = element_text(face="bold", size = 20)) + 
  xlim(0,20) + ggtitle("Betula nana subsp. nana")

################ VACCINIUM TREE

tree <- read.newick("~/Documents/paper_2/wholeskim/results/figures/vaculi.nwk")
x <- as_tibble(tree)

tree_meta <- read.csv("~/Documents/paper_2/wholeskim/results/figures/vaculi.tsv", sep="\t", header=FALSE, colClasses = c("character", "numeric", "character"))
colnames(tree_meta) <- c("label", "count", "sci_name")

tree_meta[,3] <- gsub("\\n", "\n", tree_meta[,3], fixed = TRUE)

y <- full_join(x, tree_meta, by="label")
#y <- mutate(y, sci_name = ifelse(sci_name == "Betula nana subsp. nana", "**Betula nana subsp. nana**", sci_name))
y_phylo <- as.treedata(y)

v_tree <- ggtree(y_phylo, aes(color=count)) + geom_nodepoint(aes(size=count), alpha=0.7) + 
  geom_tippoint(aes(size=count), alpha=0.7) +
  #geom_richtext(aes(label=sci_name)) +
  geom_tiplab(aes(label=sci_name), color="black", nudge_x = 0.03, size=4) + 
  geom_nodelab(aes(label=sci_name), vjust = -0.45, hjust = -0.07, color="black", angle = 90, size=4) +
  #  scale_color_stepsn(low = "#ff5d5dff", high = "#73D055FF", nice.breaks = TRUE, limits=c(0, 40000), breaks=seq(0, 40000, by=10000)) +
  scale_color_gradientn(colors = c("#ff5d5dff", "#f68f46ff","#fde725", "#73D055FF"), limits=c(0, 40000), values=c(0,0.05,0.15,1), breaks=c(0,400,8000,40000)) +
  scale_size_continuous(range = c(0,16), limits=c(0, 40000), breaks=c(0,400,8000,40000)) +
  guides(color= guide_legend(title="Read count"), size=guide_legend(title = "Read count")) + 
  theme(legend.position = c(0.15, 0.85),
        plot.title = element_text(face="bold", size = 20)) + 
  xlim(0,20) + ggtitle("Vaccinium uliginosum")

gridExtra::grid.arrange(v_tree %>% ggtree::rotate(22))

#################### BETPUB

tree <- read.newick("~/Documents/paper_2/wholeskim/results/figures/betpub.nwk")
x <- as_tibble(tree)

tree_meta <- read.csv("~/Documents/paper_2/wholeskim/results/figures/betpub.tsv", sep="\t", header=FALSE, colClasses = c("character", "numeric", "character"))
colnames(tree_meta) <- c("label", "count", "sci_name")

tree_meta[,3] <- gsub("\\n", "\n", tree_meta[,3], fixed = TRUE)

y <- full_join(x, tree_meta, by="label")
#y <- mutate(y, sci_name = ifelse(sci_name == "Betula nana subsp. nana", "**Betula nana subsp. nana**", sci_name))
y_phylo <- as.treedata(y)

v_tree <- ggtree(y_phylo, aes(color=count)) + geom_nodepoint(aes(size=count), alpha=0.7) + 
  geom_tippoint(aes(size=count), alpha=0.7) +
  #geom_richtext(aes(label=sci_name)) +
  geom_tiplab(aes(label=sci_name), color="black", nudge_x = 0.03, size=4) + 
  geom_nodelab(aes(label=sci_name), vjust = -0.45, hjust = -0.07, color="black", angle = 90, size=4) +
  #  scale_color_stepsn(low = "#ff5d5dff", high = "#73D055FF", nice.breaks = TRUE, limits=c(0, 40000), breaks=seq(0, 40000, by=10000)) +
  scale_color_gradientn(colors = c("#ff5d5dff", "#f68f46ff","#fde725", "#73D055FF"), limits=c(0, 50000), values=c(0,0.05,0.15,1), breaks=c(0,400,8000,50000)) +
  scale_size_continuous(range = c(0,16), limits=c(0, 50000), breaks=c(0,400,8000,50000)) +
  guides(color= guide_legend(title="Read count"), size=guide_legend(title = "Read count")) + 
  theme(legend.position = c(0.15, 0.85),
        plot.title = element_text(face="bold", size = 20)) + 
  xlim(0,20) + ggtitle("Betula pubescens")

gridExtra::grid.arrange(v_tree %>% ggtree::rotate(22))

########
tree <- read.newick("~/Documents/paper_2/wholeskim/results/figures/tree/salret_nounid.nwk")
x <- as_tibble(tree)

tree_meta <- read.csv("~/Documents/paper_2/wholeskim/results/figures/tree/salret_nounid_metadata.tsv", sep="\t", header=FALSE, colClasses = c("character", "numeric", "character"))
colnames(tree_meta) <- c("label", "count", "sci_name")

tree_meta[,3] <- gsub("\\n", "\n", tree_meta[,3], fixed = TRUE)

y <- full_join(x, tree_meta, by="label")
#y <- mutate(y, sci_name = ifelse(sci_name == "Betula nana subsp. nana", "**Betula nana subsp. nana**", sci_name))
y_phylo <- as.treedata(y)

v_tree <- ggtree(y_phylo, aes(color=count)) + geom_nodepoint(aes(size=count), alpha=0.7) + 
  geom_tippoint(aes(size=count), alpha=0.7) +
  #geom_richtext(aes(label=sci_name)) +
  geom_tiplab(aes(label=sci_name), color="black", nudge_x = 0.03, size=4) + 
  geom_nodelab(aes(label=sci_name), vjust = -0.45, hjust = -0.07, color="black", angle = 90, size=4) +
#  scale_color_stepsn(low = "#ff5d5dff", high = "#73D055FF", nice.breaks = TRUE, limits=c(0, 40000), breaks=seq(0, 40000, by=10000)) +
  scale_color_gradientn(colors = c("#ff5d5dff", "#f68f46ff","#fde725", "#73D055FF"), limits=c(0, 50000), values=c(0,0.05,0.15,1), breaks=c(0,400,8000,50000)) +
  scale_size_continuous(range = c(0,16), limits=c(0, 50000), breaks=c(0,400,8000,50000)) +
  guides(color= guide_legend(title="Read count"), size=guide_legend(title = "Read count")) + 
  theme(legend.position = c(0.15, 0.85),
        plot.title = element_text(face="bold", size = 20)) + 
  xlim(0,30) + ggtitle("Salix retusa")

gridExtra::grid.arrange(v_tree)

############### AYA

tree <- read.newick("~/Documents/paper_2/wholeskim/results/figures/adna_data/LDE002L-8.nwk")
x <- as_tibble(tree)

tree_meta <- read.csv("~/Documents/paper_2/wholeskim/results/figures/adna_data/LDE002L-8_metadata.tsv", sep="\t", header=FALSE, colClasses = c("character", "numeric", "character"))
colnames(tree_meta) <- c("label", "count", "sci_name")

tree_meta[,3] <- gsub("\\n", "\n", tree_meta[,3], fixed = TRUE)

y <- full_join(x, tree_meta, by="label")
#y <- mutate(y, sci_name = ifelse(sci_name == "Betula nana subsp. nana", "**Betula nana subsp. nana**", sci_name))
y_phylo <- as.treedata(y)

v_tree <- ggtree(y_phylo, aes(color=count)) + geom_nodepoint(aes(size=count), alpha=0.7) + 
  geom_tippoint(aes(size=count), alpha=0.7) +
  #geom_richtext(aes(label=sci_name)) +
  geom_tiplab(aes(label=sci_name), color="black", nudge_x = 0.03, size=4) + 
  geom_nodelab(aes(label=sci_name), vjust = -0.45, hjust = -0.07, color="black", angle = 90, size=4) +
  #  scale_color_stepsn(low = "#ff5d5dff", high = "#73D055FF", nice.breaks = TRUE, limits=c(0, 40000), breaks=seq(0, 40000, by=10000)) +
  scale_color_gradientn(colors = c("#ff5d5dff", "#f68f46ff","#fde725", "#73D055FF"), limits=c(0, 250000), values=c(0,0.05,0.15,1), breaks=c(0,400,8000,150000)) +
  scale_size_continuous(range = c(0,16), limits=c(0, 250000), breaks=c(0,400,8000,150000)) +
  guides(color= guide_legend(title="Read count"), size=guide_legend(title = "Read count")) + 
  theme(legend.position = c(0.15, 0.85),
        plot.title = element_text(face="bold", size = 20)) + 
  xlim(0,26) + ggtitle("GB-5")

gridExtra::grid.arrange(v_tree)
