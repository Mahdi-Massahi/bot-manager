# Redis Values
# bot_name:[R]-PP-Done
# bot_name:[R]-EX-Done
# bot_name:[R]-Strategy-LEn
# bot_name:[R]-Strategy-SEn
# bot_name:[R]-Strategy-LEx
# bot_name:[R]-Strategy-SEx
# bot_name:[R]-Strategy-SLV
# bot_name:[R]-Strategy-PSM
# bot_name:[R]-Strategy-TIM
# bot_name:[R]-Strategy-CLS
# bot_name:[R]-Next-Open
# bot_name:[R]-StrategyVals

bot_name <- commandArgs(trailingOnly=TRUE)[1]

# source("DBConnection.R", echo = F, print.eval = F, max.deparse.length = 0)
system(paste("Rscript", "DBConnection.R", bot_name))

# preprocess
message("Preprocessing data...")
# source("Preprocess.R", echo = F, print.eval = F, max.deparse.length = 0)
system(paste("Rscript", "Preprocess.R", bot_name))

if (redisGet(paste0(bot_name, ":[R]-PP-Done")) == "1") {
  message("Data preprocessed.")

  # Execute Strategy
  source("Strategy.R", echo = F, print.eval = F, max.deparse.length = 0)
  message("Executing strategy...")

  redisSet(paste0(bot_name, ":[R]-EX-Done"), charToRaw("0"))
  load("chain.dll")
  aData   <- read.csv(header = T, file = "Temp/aData.csv")
  tData   <- read.csv(header = T, file = "Temp/tData.csv")
  rmrule  <- as.numeric(redisGet(paste0(bot_name, ":[S]-RMRule")))
  fee     <- as.numeric(redisGet(paste0(bot_name, ":[S]-Bybit-Taker-Fee")))
  nextOpen <- redisGet(paste0(bot_name, ":[R]-Next-Open"))

  run_test_strategy <- redisGet(paste0(bot_name, ":[S]-Run-Test-Strategy"))
  if(as.logical(run_test_strategy)){
    result  <- Strategy(aData = aData,
                        tData = tData,
                        x = c(c(redisGet(paste0(bot_name, ":[R]-StrategyVals")),
                                rmrule, fee)))
  }else{
    result <- cmp.s(
      x=c(redisGet(paste0(bot_name, ":[R]-StrategyVals")), fee, rmrule),
      tData=tData,
      aData=aData,
      nextOpen=nextOpen)
  }

  lastRow <- result[dim(result)[1], ]

  redisSet(paste0(bot_name, ":[R]-Strategy-LEn"), charToRaw(toString(lastRow$LongEntry)))
  redisSet(paste0(bot_name, ":[R]-Strategy-SEn"), charToRaw(toString(lastRow$ShortEntry)))
  redisSet(paste0(bot_name, ":[R]-Strategy-LEx"), charToRaw(toString(lastRow$LongExit)))
  redisSet(paste0(bot_name, ":[R]-Strategy-SEx"), charToRaw(toString(lastRow$ShortExit)))
  redisSet(paste0(bot_name, ":[R]-Strategy-SLV"), charToRaw(toString(lastRow$SL)))
  redisSet(paste0(bot_name, ":[R]-Strategy-PSM"), charToRaw(toString(lastRow$PSM)))
  redisSet(paste0(bot_name, ":[R]-Strategy-TIM"), charToRaw(toString(date())))
  redisSet(paste0(bot_name, ":[R]-Strategy-CLS"), charToRaw(toString(lastRow$Close)))

  redisSet(paste0(bot_name, ":[R]-EX-Done"), charToRaw("1"))
}else {
  redisClose()
  stop("Preprocess error.")
}

# source("readRedis.R", echo = F, print.eval = F, max.deparse.length = 0)
system(paste("Rscript", "readRedis.R", bot_name))

redisClose()
message("Redis disconnected.")

rm(list = ls())
message("Environment cleared.")