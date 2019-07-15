library(ggplot2)

rawdata <-  read.csv("output.csv",header=T)

ggplot(rawdata,aes(x=Temperature,fill=Keyword))+
      geom_histogram(position="dodge")
