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
# bot_name:[R]-Strategy-NOP
# bot_name:[R]-StrategyVals

bot_name <- commandArgs(trailingOnly=TRUE)[1]
message(paste0("R> Current bot name is: '", bot_name, "'"))

source("Profile.R", echo = F, print.eval = F, max.deparse.length = 0)

# preprocess
message("Preprocessing data...")
source("Preprocess.R", echo = F, print.eval = F, max.deparse.length = 0)
message("Data preprocessed.")

if (rredis::redisGet(paste0(bot_name, ":[R]-PP-Done")) == "1") { #TODO: do we really need this?
  rredis::redisSet(paste0(bot_name, ":[R]-EX-Done"), charToRaw("0"))

  aData    <- read.csv(header = T, file = "Temp/aData.csv")
  tData    <- read.csv(header = T, file = "Temp/tData.csv")
  rmrule   <- as.numeric(rredis::redisGet(paste0(bot_name, ":[S]-RMRule")))
  fee      <- as.numeric(rredis::redisGet(paste0(bot_name, ":[S]-Bybit-Taker-Fee")))
  nextOpen <- as.numeric(rredis::redisGet(paste0(bot_name, ":[R]-Strategy-NOP")))

  message("Executing strategy...")

  run_test_strategy <- rredis::redisGet(paste0(bot_name, ":[S]-Run-Test-Strategy"))
  if(as.logical(run_test_strategy)){
    source("Strategy.R", echo = F, print.eval = F, max.deparse.length = 0)
    result  <- Strategy(aData = aData,
                        tData = tData,
                        x = c(c(rredis::redisGet(paste0(bot_name, ":[R]-StrategyVals")),
                                rmrule, fee)))
  }else{
    load("chain.dll") #TODO: fix this
    result <- cmp.s(
      x=rredis::redisGet(paste0(bot_name, ":[R]-StrategyVals")),
      Com = fee,
      RMRule = rmrule,
      tData=tData,
      aData=aData,
      nextOpen=nextOpen)
  }

  lastRow <- result[dim(result)[1], ]

  rredis::redisSet(paste0(bot_name, ":[R]-Strategy-LEn"), charToRaw(toString(lastRow$LongEntry)))
  rredis::redisSet(paste0(bot_name, ":[R]-Strategy-SEn"), charToRaw(toString(lastRow$ShortEntry)))
  rredis::redisSet(paste0(bot_name, ":[R]-Strategy-LEx"), charToRaw(toString(lastRow$LongExit)))
  rredis::redisSet(paste0(bot_name, ":[R]-Strategy-SEx"), charToRaw(toString(lastRow$ShortExit)))
  rredis::redisSet(paste0(bot_name, ":[R]-Strategy-SLV"), charToRaw(toString(lastRow$SL)))
  rredis::redisSet(paste0(bot_name, ":[R]-Strategy-PSM"), charToRaw(toString(lastRow$PSM)))
  rredis::redisSet(paste0(bot_name, ":[R]-Strategy-TIM"), charToRaw(toString(date())))
  rredis::redisSet(paste0(bot_name, ":[R]-Strategy-CLS"), charToRaw(toString(lastRow$Close)))

  rredis::redisSet(paste0(bot_name, ":[R]-EX-Done"), charToRaw("1"))
}else{
  rredis::redisClose()
  stop("Preprocess error.")
}

source("readRedis.R", echo = F, print.eval = F, max.deparse.length = 0)
# system(paste("Rscript", "readRedis.R", bot_name))

rredis::redisClose()
message("Redis disconnected.")

rm(list = ls())
message("Environment cleared.")