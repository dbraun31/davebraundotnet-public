library(tidyverse)
library(RColorBrewer)

sev <- function(rew) {
    return(b_j + rew*a_j)
}

per <- function(p) {
    return(p)    
}

cost <- function(pl_e) {
    return(exp((pl_e * c_j)/e_j)-1)
}

V <- function(pl_e, pl_p, p, rew) {
    return(-sev(rew) * per(p) * (1 - pl_p) - cost(pl_e))
}

softmax <- function(z) {
    out <- c()
    count <- 0
    den <- sum(exp(z))
    for (e in z) {
        count <- count + 1
        out[count] <- exp(e) / den
    }
    return(out) 
}

a_j <- 8
c_j <- .5
e_j <- 1
b_j <- 0

d <- expand.grid(pl_e = seq(0, 5, by = .01), plan_slope = seq(0, .2, .02))
d$pl_p <- d$pl_e * d$plan_slope


d$v <- with(d, V(pl_e, pl_p, rew = 6, p = .5))

maxes <- d %>% 
    group_by(plan_slope) %>% 
    filter(v == max(v)) %>% 
    mutate(a_j = factor(a_j, levels = c('low', 'high'))) %>% 
    mutate(a_j = recode(a_j, `low` = 'Low Reward Sensitivity', `high` = 'High Reward Sensitivity'))  

colors <- c(
    '#616365',
    '#696e71',
    '#70787d',
    '#788389',
    '#808e96',
    '#899aa4',
    '#92a7b3',
    '#9cb5c4',
    '#a7c5d6'
)

blues <- rev(brewer.pal(9, 'Blues'))[1:7]
scales::show_col(blues)

d %>% 
    group_by(plan_slope) %>% 
    summarize(proba = softmax(v), pl_e = pl_e) %>% 
    ggplot(aes(x = pl_e, y = proba, group = plan_slope)) + 
    geom_ribbon(aes(ymin = 0, ymax = proba, fill = plan_slope), alpha = .6) + 
    geom_line(aes(color = plan_slope)) + 
    labs(
        x = 'Plan Effort',
        y = 'Probability of Choice',
        color = 'Security Plan Efficacy',
        fill ='Security Plan Efficacy',
    ) + 
    scale_fill_gradientn(colors = blues) + 
    scale_color_gradientn(colors = blues) + 
    theme_void() + 
    theme(axis.ticks = element_blank(),
          legend.text = element_blank(),
          axis.title = element_blank(),
          axis.text = element_blank(),
          panel.grid = element_blank(),
          legend.position = 'none',
          text = element_text(size = 8),
          legend.title = element_text(size = 6),
          panel.border = element_blank(),
          plot.tag.position = c(.002, 1),
          plot.tag = element_text(size = 10),
          panel.background = element_rect(fill = 'transparent', color = NA),
          plot.margin = unit(c(0, 0, 0, 0), 'pt'))

ggsave('static/images/about_background.png', height = 1440, width = 2560, units = 'px', dpi = 300)




g <- gridExtra::grid.arrange(p1, p2, nrow = 2)
ggsave('efficacy_two.png', g, height = 3.91, width = 3.09, units = 'in', dpi = 300)















