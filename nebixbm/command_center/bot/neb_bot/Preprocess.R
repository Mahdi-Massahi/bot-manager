# Flag for PP
redisSet("neb_bot:[R]-PP-Done", charToRaw("0"))

# dataset creationData.csv
fileName   <- 'Temp/aDataRaw.csv'
dataset    <- read.csv(header = T, fileName)

# Heikin Ashi calculation
HA          <- Neb.HeikinAshi(dataset)
dataset$HAO <- HA$Open
dataset$HAC <- HA$Close
dataset$HAH <- HA$High
dataset$HAL <- HA$Low

# make sure volume is in numeric type not string
# dataset$Volume <- as.numeric(dataset$Volume)

# Export
write.csv(dataset, "Temp/aData.csv")

# Empty
rm(list = ls())

redisSet("neb_bot:[R]-PP-Done", charToRaw("1"))