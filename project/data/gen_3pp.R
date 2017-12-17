# =============================================================================
# Generating real time series data based on
# "LIU, Song et al. Change-point detection in time-series data by relative density-ratio estimation. Neural Networks, v. 43, p. 72-83, 2013."
# =============================================================================

l2.norm <- function(l) {
	sqrt(sum(l ^ 2))
}

data <- read.csv('../3pp/HASCrwdata/rwActData/person671/hasc-111018-165936-mag.csv')

series <- c()
for (i in 1:dim(data)[1]) {
	line <- data[i,]
	series[i] <- l2.norm(c(line[2][[1]], line[3][[1]], line[4][[1]]))
}

plot(series, type='l')
write.table(series,file='series/series_3pp_mag.csv',row.names=FALSE,col.names=FALSE)