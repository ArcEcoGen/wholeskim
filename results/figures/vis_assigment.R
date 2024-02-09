library(ggplot2)
library(tidyverse)
library(viridis)
library(ggpubr)
require(grid)

data_skims <-  read.csv("~/Documents/paper_2/wholeskim/intermediate/skims_test/plot_min20.tsv", header=FALSE, sep = "\t", na.strings = "NOT")

data_skims <- group_by(data_skims, V1) %>% 
  mutate(percent = V3/sum(V3)) %>%
  mutate(grouped = ifelse(str_detect(V2, "higher|\\btarget"), paste("corr_", "", sep=""), paste("incorr_", "", sep="")))

data_skims$V2 <- factor(data_skims$V2, levels = c("higher_taxa",
                                                  "higher_family",
                                                  "higher_genus",
                                                  "target",
                                                  "unid",
                                                  "off_family",
                                                  "off_genus",
                                                  "off_target"))


plot_corr <- function(prefix, title_string, yform) {
  init_data <- data_skims[str_detect(data_skims$V1, prefix), ]
  temp_data <- init_data[!(init_data$V2=="unid"),]
  temp_data <- droplevels(temp_data)
  
  facet_labs <- c("wholeskim\n(full)", "Holi", "wholeskim\n(contigs)", "wholeskims\n(subset)")
  names(facet_labs) <- levels(factor(temp_data$V1))
  
  scale_axis <- function(x) sprintf(yform, x)
  
  p_plot <- ggplot(temp_data, aes(fill = V2, y=percent, x=grouped)) + 
    geom_bar(position="stack", stat="identity", show.legend = TRUE) + 
    scale_fill_manual(values=(c("#440154FF", "#39568CFF", "#1F968BFF","#73D055FF","#fde725FF", "#f68f46ff", "#ff5d5dff")), 
                      labels=c("Higher target level", "Target family", "Target genus", "Target species","Confamilial taxa", "Congeneric species", "Misassignment"), 
                      name="Assignment", drop = FALSE) + 
    scale_x_discrete(labels = c("wholeskim\n(full)", "Holi", "wholeskim\n(contigs)", "wholeskims\n(subset)")) + ggtitle(title_string) +
    theme_bw() +
    theme(axis.title.x = element_blank(),
          axis.text.x = element_blank(),
          axis.ticks.x = element_blank(),
          axis.title.y = element_blank(),
          axis.line = element_line(colour = "black"),
          panel.border = element_blank(),
          strip.background = element_rect(fill = NA, color = "white"),
          text=element_text(size=17)) + 
    scale_y_continuous(labels=scale_axis, expand=c(0,0)) +
    facet_grid(~ V1, switch = "x", labeller = labeller(V1 = facet_labs))
  
  return(p_plot)
}

p_betnan <- plot_corr("betnan", "Betula nana", "%.1f")
p_avefle <- plot_corr("avefle", "Avenella flexuosa", "%.2f")
p_salret <- plot_corr("salret", "Salix retusa", "%.1f")
p_thealp <- plot_corr("thealp", "Thesium alpinum", "%.2f")

figure <- ggarrange(p_betnan, p_avefle,
                    p_salret, p_thealp,
                    ncol = 2,
                    nrow = 2,
                    common.legend = TRUE,
                    legend="right",
                    heights = c(1,1,1,1))

annotate_figure(figure, left = textGrob("Proportion of reads", rot = 90, vjust = 0.5, gp = gpar(cex = 2.4)),
                bottom = textGrob("Workflow", vjust = 0.3, hjust=1.3, gp = gpar(cex = 2.4)))

######################## ONE OUT FINAL ################################
skim_order <- c("vaculino_vacc_no_erica",
                "vaculino_vacc_all_erica",
                "vaculi0",
                "vaculi1",
                "vaculi2",
                "vaculi3",
                "vaculi4",
                "vaculi5",
                "vaculi6",
                "vaculi7",
                "vaculi8",
                "vaculi9",
                "vaculi10",
                "vaculi11",
                "vaculi12",
                "vaculi13",
                "vaculi14",
                "vaculi15")

oneout_skims <-  read.csv("~/Documents/paper_2/wholeskim/results/figures/erica_dropout/overall.txt", header=FALSE, sep = "\t", na.strings = "NOT")
oneout_skims <- group_by(oneout_skims, V1) %>% 
  mutate(percent = V3/sum(V3)) %>%
  mutate(grouped = ifelse(str_detect(V2, "higher|\\btarget"), paste("corr_", "", sep=""), paste("incorr_", "", sep=""))) %>%
  arrange(match(V1, skim_order))
  

oneout_skims <- oneout_skims[!(oneout_skims$V2=="unid"),]


oneout_skims$V2 <- factor(oneout_skims$V2, levels = c("higher_taxa",
                                                      "higher_family",
                                                      "higher_genus",
                                                      "target",
                                                      "off_family",
                                                      "off_genus",
                                                      "off_target"))


oneout_skims$V1 <- factor(oneout_skims$V1, levels = skim_order)

facet_labs_oneout <- c("No Ericaceae", 
                       "Ericaceae, \nno Vaccinium", 
                       "Ericaceae,\nVaccinium,\nno uliginosum", 
                       "1 median\nV. uliginosum",
                       "2 median\nV. uliginosum",
                       "3 median\nV. uliginosum",
                       "4 median\nV. uliginosum",
                       "5 median\nV. uliginosum",
                       "6 median\nV. uliginosum",
                       "7 median\nV. uliginosum",
                       "8 median\nV. uliginosum",
                       "9 median\nV. uliginosum",
                       "10 median\nV. uliginosum",
                       "11 median\nV. uliginosum",
                       "12 median\nV. uliginosum",
                       "13 median\nV. uliginosum",
                       "14 median\nV. uliginosum",
                       "15 complete\nV. uliginosum")
#  median\nV. uliginosum
names(facet_labs_oneout) <- levels(factor(oneout_skims$V1))

p_plot <- ggplot(oneout_skims, aes(fill = V2, y=percent, x=grouped)) + 
  geom_bar(position="stack", stat="identity", show.legend = TRUE) + 
  scale_fill_manual(values=(c("#440154FF", "#39568CFF", "#1F968BFF","#73D055FF","#fde725FF", "#f68f46ff", "#ff5d5dff")), 
                    labels=c("Higher tax. level", "Target family", "Target genus", "Target species","Confamilial taxa", "Congeneric species", "Misassignment"), 
                    name="Assignment", drop = FALSE) + 
  ggtitle("Vaccinium uliginosum") +
  theme_bw() +
  theme(axis.title.x = element_blank(),
        axis.text.x = element_blank(),
        axis.ticks.x = element_blank(),
        axis.title.y = element_blank(),
        axis.line = element_line(colour = "black"),
        strip.text.x = element_text(angle=270),
        panel.border = element_blank(),
        strip.background = element_rect(fill = NA, color = "white"),
        text=element_text(size=17)) +
  facet_grid(~ V1, switch = "x", labeller = labeller(V1 = facet_labs_oneout))

vaccfig <- ggarrange(p_plot,
                     ncol = 1,
                     nrow = 1,
                     common.legend = TRUE,
                     legend="right",
                     heights = c(1,1))

annotate_figure(vaccfig, left = textGrob("Proportion of reads", rot = 90, vjust = 0.5, gp = gpar(cex = 2.4)),
                bottom = textGrob("Database composition", vjust = 0.3, hjust=0.7, gp = gpar(cex = 2.4)))

####### Genome completeness


