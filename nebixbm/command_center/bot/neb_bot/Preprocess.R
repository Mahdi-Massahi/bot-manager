# Flag for PP
redisSet("neb_bot:[R]-PP-Done", charToRaw("0"))

# dataset creationData.csv
fileName   <- 'Temp/aData.csv'
dataset    <- read.csv(header = T, fileName)

# Heikin Ashi calculation
HA          <- Neb.HeikinAshi(dataset)
dataset$HAO <- HA$Open
dataset$HAC <- HA$Close
dataset$HAH <- HA$High
dataset$HAL <- HA$Low

#make sure volume is in numeric type not string
dataset$Volume <- as.numeric(dataset$Volume)

# Export
data       <- dataset
# data$Index <- 1:dim(data)[1]
write.csv(data, "Temp/Preproccessed.csv")

# Empty
rm(dataset, data, HA, fileName)

redisSet("neb_bot:[R]-PP-Done", charToRaw("1"))