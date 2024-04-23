library(ggplot2)

data <- read.delim("~/Documents/paper_2/wholeskim/results/figures/adna_data/combined_results_readcounts_nigher_combgenus_nohordeum.csv")

data$scientific_name <- as.factor(data$scientific_name)

###### Wholeskim only #######
data_wholeskim <- data[data$workflow == "wholeskim", ]

ggplot(data_wholeskim, aes(x=sample, y=scientific_name, fill=num_reads)) +
  geom_tile() +
  scale_fill_viridis_c(name = "Number\nof reads", option = "magma", limits=c(0, 300000), oob = scales::squish, direction = -1) +
  xlab("Sample") +
  theme_bw() +
  ylim(rev(levels(data$scientific_name))) +
  theme(panel.border = element_blank(),
        text=element_text(size=17),
        axis.title.y = element_blank())
