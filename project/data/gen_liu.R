# =============================================================================
# Generating artificial time series data based on
# "LIU, Song et al. Change-point detection in time-series data by relative density-ratio estimation. Neural Networks, v. 43, p. 72-83, 2013."
# =============================================================================

e <- function(mu, sd) {
  rnorm(1, mean=mu, sd=sd)
}

mu <- function(N) {
  if (N == 1) {0}
  else if (N %in% 2:51) {mu(N-1) + N/16}
}

sd <-  function(N) {
  if (N %in% seq(1,51,2)) {1}
  else if (N %in% seq(2,50,2)) {log(exp(1) + N/4)}
}

w <- function(N) {
  if (N == 1) {1}
  else if (N %in% 2:51) {w(N-1)*log(exp(1) + N/2)}
} 

N <- function(t) {
  round(t/100) + 1
}

ar.buffer <- c(0,0)
ar <- function(t, mu, sd) {
  if (t == 1 || t == 2) {0}
  else {
    ar.t <- 0.6*ar.buffer[t-1] - 0.5*ar.buffer[t-2] + e(mu=mu, sd=sd)
    ar.buffer[t] <<- ar.t
    return(ar.t)
  }
}

jumping.mean <- function(t) {
  ar(t, mu=mu(N(t)),  sd=1.5) 
}

scaling.variance <- function(t) {
  ar(t, mu=0, sd=sd(N(t)))
}

changing.frequency <- function(t) {
  sin(w(N(t))) + e(mu=0, sd=0.8)
}

series <- c()
for (i in 1:5000) {
  series[i] <- changing.frequency(i)
}

plot(series, type='l')
write.table(series,file='series/series_cf.csv',row.names=FALSE,col.names=FALSE)