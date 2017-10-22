library(dlm)

main <- function(holout.ts, data.ts, start_, ahead_,
  genGraphName, foreGraphName){
  lData <- holout.ts
  dlmModel <- dlmModPoly() + dlmModSeas(4)
  buildFun <- function(x) {
    diag(W(dlmModel))[2:3] <- exp(x[1:2])
    V(dlmModel) <- exp(x[3])
    return(dlmModel)
  }
  (fit <- dlmMLE(lData, parm = rep(0, 3), build = buildFun))$conv
  dlmModel <- buildFun(fit$par)
  dataSmooth <- dlmSmooth(lData, mod = dlmModel)

  x <- cbind(lData, dropFirst(dataSmooth$s[,c(1,3)]))
  colnames(x) <- c("Cars", "Trend", "Seasonal")
  plot(x, type = 'o', main = genGraphName)

  dataFilt <- dlmFilter(lData, mod=dlmModel)
  dataFore <- dlmForecast(dataFilt, nAhead=ahead_)
  sqrtR <- sapply(dataFore$R, function(x) sqrt(x[1,1]))
  #pl <- dataFore$a[,1] + qnorm(0.05, sd = sqrtR)
  #pu <- dataFore$a[,1] + qnorm(0.95, sd = sqrtR)

  x <- ts.union(window(lData, start = start_),
    window(dataSmooth$s[,1], start = start_),
    dataFore$a[,1])
  plot(x, plot.type = "single", type = 'o', pch = c(1, 0, 20, 3, 3),
    col = c("darkgrey", "darkgrey", "brown"),
    ylab = foreGraphName)
  legend("bottomright", legend = c("Observed",
    "Smoothed (deseasonalized)"),
    bty = 'n', pch = c(1, 0, 20, 3, 3), lty = 1,
    col = c("darkgrey", "darkgrey", "brown")
  )

  lines(data.ts)
}