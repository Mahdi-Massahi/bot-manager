# Flag fo PP
redisSet("[R]-PP-Done", charToRaw("0"))

# Data trim percentage
Train_SetP <- 50 # %

# dataset creationData.csv
fileName   <- 'Temp/Data.csv' 
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
data$Index <- 1:dim(data)[1]
write.csv(data, "Temp/FULL_SET.csv")

data       <- dataset[1:floor(dim(dataset)[1] * Train_SetP / 100),]
data$Index <- 1:dim(data)[1]
write.csv(data, "Temp/TRAIN_SET.csv")

data       <- dataset[(floor(dim(dataset)[1] * Train_SetP / 100)):dim(dataset)[1],]  
data$Index <- 1:dim(data)[1]
write.csv(data, "Temp/TEST_SET.csv")

# Pair Name handling
pair <- rev(setdiff(strsplit(fileName,"/|\\\\")[[1]], ""))[c(3,2)]
pair <- paste(pair[1], pair[2], sep = " - ")

# Empty
rm(Train_SetP, dataset, data, HA, fileName, pair)

redisSet("[R]-PP-Done", charToRaw("1"))