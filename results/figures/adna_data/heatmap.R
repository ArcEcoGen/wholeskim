library(ggplot2)

data <- read.delim("~/Documents/paper_2/wholeskim/results/figures/adna_data/combined_results_readcounts_nigher_combgenus.csv")

data$scientific_name <- as.factor(data$scientific_name)

ggplot(data, aes(x=workflow, y=scientific_name, fill=num_reads)) +
  geom_tile() +
  scale_fill_viridis_c(name = "Number\nof reads", option = "magma", limits=c(0, 250000), oob = scales::squish, direction = -1) +
  scale_x_discrete(labels=c("Holi-\nassembled", "wholeskim-\nunassembled")) +
  facet_wrap(~sample) +
  xlab("Workflow") +
  theme_bw() +
  ylim(rev(levels(data$scientific_name))) +
  theme(panel.border = element_blank(),
        text=element_text(size=17),
        axis.title.y = element_blank())

###### Wholeskim only #######
data_wholeskim <- data[data$workflow == "wholeskim", ]

ggplot(data_wholeskim, aes(x=sample, y=scientific_name, fill=num_reads)) +
  geom_tile() +
  scale_fill_viridis_c(name = "Number\nof reads") +
  xlab("Sample") +
  theme_bw() +
  ylim(rev(levels(data$scientific_name))) +
  theme(panel.border = element_blank(),
        text=element_text(size=17),
        axis.title.y = element_blank())

# Species level
data_species <- read.delim("~/Documents/paper_2/wholeskim/results/figures/adna_data/combined_results_readcounts_nigher.csv")

data_species$scientific_name <- as.factor(data_species$scientific_name)

ggplot(data_species, aes(x=workflow, y=scientific_name, fill=num_reads)) +
  geom_tile() +
  scale_fill_viridis_c(name = "Number\nof reads") +
  scale_x_discrete(labels=c("Holi-\nassembled", "wholeskim-\nunassembled")) +
  facet_wrap(~sample) +
  xlab("Workflow") +
  theme_bw() +
  ylim(rev(levels(data_species$scientific_name))) +
  theme(panel.border = element_blank(),
        text=element_text(size=17),
        axis.title.y = element_blank())

### ELSA
data_species <- read.delim("~/Documents/duty_work/eifel/summary.csv")

data_species$scientific_name <- as.factor(data_species$scientific_name)

ggplot(data_species, aes(x=sample, y=scientific_name, fill=read_count)) +
  geom_tile() +
  scale_fill_viridis_c(name = "Number\nof reads", option="magma" ) +
  xlab("Sample") +
  theme_bw() +
#  ylim(rev(levels(data$scientific_name))) +
  theme(panel.border = element_blank(),
        text=element_text(size=17),
        axis.title.y = element_blank())
