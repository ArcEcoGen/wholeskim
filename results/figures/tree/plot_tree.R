library(ggtree)
library(treeio)
library(tidytree)
library(ggplot2)

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

tree <- read.newick("~/Documents/paper_2/test_tree/betnan.nwk")
x <- as_tibble(tree)

tree_meta <- read.csv("~/Documents/paper_2/test_tree/betnan.tsv", sep="\t", header=FALSE, colClasses = c("character", "numeric", "character"))
colnames(tree_meta) <- c("label", "count", "sci_name")

y <- full_join(x, tree_meta, by="label")
y_phylo <- as.treedata(y)

ggtree(y_phylo, aes(color=count)) + geom_nodepoint(aes(size=count), alpha=0.7) + 
  geom_tippoint(aes(size=count), alpha=0.7) +
  geom_tiplab(aes(label=sci_name), color="black") + 
  geom_nodelab(aes(label=sci_name), nudge_x = 0.3, nudge_y = -0.2, color="black") +
  scale_size(range = c(0,40)) + 
  scale_color_viridis_c()
