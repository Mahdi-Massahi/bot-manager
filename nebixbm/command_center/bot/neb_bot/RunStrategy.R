# Redis Values
# neb_bot:[R]-PP-Done
# neb_bot:[R]-EX-Done
# neb_bot:[R]-Strategy-LEn
# neb_bot:[R]-Strategy-SEn
# neb_bot:[R]-Strategy-LEx
# neb_bot:[R]-Strategy-SEx
# neb_bot:[R]-Strategy-SLP
# neb_bot:[R]-Strategy-PSM
# neb_bot:[R]-Strategy-TIM
# neb_bot:[R]-Strategy-CLS

source("Setup.R", echo = F, print.eval = F, max.deparse.length = 0)

# preprocess
message("Preprocessing data...")
source("Preprocess.R", echo = F, print.eval = F, max.deparse.length = 0)

if (redisGet("neb_bot:[R]-PP-Done") == "1") {
  message("Data preprocessed.")

  # Execute Strategy
  source("Strategy.R", echo = F, print.eval = F, max.deparse.length = 0)
  message("Executing strategy...")

  redisSet("neb_bot:[R]-EX-Done", charToRaw("0"))
  load("chain.dll")
  aData <- read.csv(header = T, file = "Temp/aData.csv")
  tData <- read.csv(header = T, file = "Temp/tData.csv")
  rmrule <- as.numeric(redisGet("neb_bot:[S]-RMRule"))
  fee <- as.numeric(redisGet("neb_bot:[S]-Bybit-Taker-Fee"))
  result <- cmp.s(x=c(redisGet("neb_bot:[R]-StrategyVals"), fee, rmrule),
                  tData=tData,
                  aData=tData)
  lastRow <- result[dim(result)[1],]

  redisSet("neb_bot:[R]-Strategy-LEn", charToRaw(toString(lastRow$LongEntry)))
  redisSet("neb_bot:[R]-Strategy-SEn", charToRaw(toString(lastRow$ShortEntry)))
  redisSet("neb_bot:[R]-Strategy-LEx", charToRaw(toString(lastRow$LongExit)))
  redisSet("neb_bot:[R]-Strategy-SEx", charToRaw(toString(lastRow$ShortExit)))
  redisSet("neb_bot:[R]-Strategy-SLP", charToRaw(toString(lastRow$SL)))
  redisSet("neb_bot:[R]-Strategy-PSM", charToRaw(toString(lastRow$PSM)))
  redisSet("neb_bot:[R]-Strategy-TIM", charToRaw(toString(date())))
  redisSet("neb_bot:[R]-Strategy-CLS", charToRaw(toString(lastRow$Close)))

  redisSet("neb_bot:[R]-EX-Done", charToRaw("1"))
}else {
  redisClose()
  stop("Preprocess error.")
}

source("readRedis.R", echo = F, print.eval = F, max.deparse.length = 0)

redisClose()
message("Redis disconnected.")

rm(list = ls())
message("Environment cleared.")