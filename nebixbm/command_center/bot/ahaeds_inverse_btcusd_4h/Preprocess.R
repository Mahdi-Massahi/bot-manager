# Flag for PP
rredis::redisSet(paste0(bot_name, ":[R]-PP-Done"), charToRaw("0"))

# dataset aData.csv
fileName   <- 'Temp/aDataRaw.csv'
dataset    <- read.csv(header = T, fileName)

# exclude last kline
dataset    <- dataset[1:(nrow(dataset)-1), ]

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

# dataset tData.csv
fileName   <- 'Temp/tDataRaw.csv'
dataset    <- read.csv(header = T, fileName)

nextOpen   <- dataset$Open[nrow(dataset)]
rredis::redisSet(paste0(bot_name, ":[R]-Strategy-NOP"), charToRaw(toString(nextOpen)))

# exclude last kline
dataset    <- dataset[1:(nrow(dataset)-1), ]
# Export
write.csv(dataset, "Temp/tData.csv")

rredis::redisSet(paste0(bot_name, ":[R]-PP-Done"), charToRaw("1"))
