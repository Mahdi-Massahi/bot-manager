# Redis Values
# [R]-PP-Done
# [R]-EX-Done
# [R]-Strategy-LEn
# [R]-Strategy-SEn
# [R]-Strategy-LEx
# [R]-Strategy-SEx
# [R]-Strategy-SLP
# [R]-Strategy-PSM
# [R]-Strategy-TIM

source("Setup.R", echo = F, print.eval = F, max.deparse.length = 0)

# preprocess
message("Preprocessing data...")
source("Preprocess.R", echo = F, print.eval = F, max.deparse.length = 0)

if (redisGet("[R]-PP-Done") == "1") {
  message("Data preprocessed.")

  # Execute Strategy
  source("SS.R", echo = F, print.eval = F, max.deparse.length = 0)
  message("Executing strategy...")

  redisSet("[R]-EX-Done", charToRaw("0"))
  data <- read.csv(header = T, file = "Temp/Preproccessed.csv")
  buff <- SS(redisGet("[R]-StrategyVals"), data)
  lastRow <- buff[dim(buff)[1],]

  redisSet("[R]-Strategy-LEn", charToRaw(toString(lastRow$LongEntry)))
  redisSet("[R]-Strategy-SEn", charToRaw(toString(lastRow$ShortEntry)))
  redisSet("[R]-Strategy-LEx", charToRaw(toString(lastRow$LongExit)))
  redisSet("[R]-Strategy-SEx", charToRaw(toString(lastRow$ShortExit)))
  redisSet("[R]-Strategy-SLP", charToRaw(toString(lastRow$SL)))
  redisSet("[R]-Strategy-PSM", charToRaw(toString(lastRow$PSM)))
  redisSet("[R]-Strategy-TIM", charToRaw(toString(date())))

  #message("Last row:")
  #message(paste(colnames(data), collapse = ", "))
  #message(paste(lastRow, collapse = ", "))

  redisSet("[R]-EX-Done", charToRaw("1"))
}else {
  redisClose()
  stop("Preprocess error.")
}

source("readRedis.R", echo = F, print.eval = F, max.deparse.length = 0)

redisClose()
message("Redis disconnected.")

rm(list = ls())
message("Environment cleared.")