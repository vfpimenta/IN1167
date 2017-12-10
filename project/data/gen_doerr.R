# =============================================================================
# Generating artificial time series data based on
# "DOERR, Benjamin et al. Detecting structural breaks in time series via genetic algorithms. Soft Computing, v. 21, n. 16, p. 4707-4720, 2017."
# =============================================================================

library(stats)

yi.1 <- function(yi) {
  val <- yi + yi*(1-yi)*(1+yi) + rnorm(1, sd=0.17)
  if (val > 2) {1.5}
  else if (val < -2) {-1.5}
  else {val}
}

series <- c(runif(1),-2,2)
min.distance <- 450
last.b <- 1
b <- 11
for (i in 2:6500) {
  val <- yi.1(series[i-1])

  if (sign(val) != sign(series[i-1])) {
    if (i-last.b > min.distance && b > 0) {
      last.b <- i
      b <- b - 1
    } else {
      val <- -val
    }
  }

  series[i] <- val
}

plot(series, type='l')
write.table(series,file='series/series_11.csv',row.names=FALSE,col.names=FALSE)