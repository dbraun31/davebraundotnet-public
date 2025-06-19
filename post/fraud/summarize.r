library(tidyverse)

d <- read.csv('preds_cv.csv')


confusion <- function(y_test, y_pred) {
    fp <- sum(y_test == 0 & y_pred == 1)
    fn <- sum(y_test == 1 & y_pred == 0)
    tp <- sum(y_test == 1 & y_pred == 1)
    tn <- sum(y_test == 0 & y_pred == 0)
    
    fpr <- fp / (fp + tn)
    recall <- tp / (tp + fn)
    precision <- tp / (tp + fp)
    
    return(c(recall, precision, fpr))
}

thresholds <- seq(0, 1, .001)

get_roc <- function(threshold, d) {
    y_pred <- ifelse(d$y_prob > threshold, 1, 0)
    out <- confusion(d$y_test, y_pred)
    return(data.frame(threshold=threshold, tpr = out[1], fpr = out[3]))
}

get_f1 <- function(threshold, d) {
    y_pred <- ifelse(d$y_prob > threshold, 1, 0)
    y_test <- d$y_test
    out <- confusion(y_test, y_pred)
    recall <- out[1]
    precision <- out[2]
    
    out <- 2 * ((precision * recall) / (precision + recall))
    return(data.frame(threshold, out))
}

get_pr <- function(threshold, d) {
    y_pred <- ifelse(d$y_prob > threshold, 1, 0)
    y_test <- d$y_test
    out <- confusion(y_test, y_pred)
    return(data.frame(threshold=threshold, precision=out[2], recall=out[1]))
}

# F1
f1 <- do.call(rbind, lapply(thresholds, get_f1, d))

f1 %>% 
    ggplot(aes(x = threshold, y = out)) + 
    geom_point() +
    ylim(0,1)

# ROC
roc <- do.call(rbind, lapply(thresholds, get_roc, d))

roc %>% 
    ggplot(aes(x = fpr, y = tpr)) + 
    geom_point(aes(color = threshold))

# PR

pr <- do.call(rbind, lapply(thresholds, get_pr, d))

pr %>% 
    ggplot(aes(x = recall, y = precision)) + 
    geom_point() + 
    scale_x_continuous(labels = seq(0, 1, .1), breaks = seq(0, 1, .1))

























