library(stats)

yi.1 <- function(yi) {
  val <- yi + yi*(1-yi)*(1+yi) + rnorm(1, sd=0.135)
  if (val > 2) {1.5}
  else if (val < -2) {-1.5}
  else {val}
}

series <- c(runif(1),-2,2)
for (i in 2:1000) {
  series[i] = yi.1(series[i-1])
}

plot(series, type='l')
write.table(series,file='series.csv',row.names=FALSE,col.names=FALSE)