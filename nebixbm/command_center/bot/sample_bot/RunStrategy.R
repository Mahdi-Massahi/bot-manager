wd <- getwd()
source(paste0(wd,"/Setup.R"), echo = F, print.eval = F, max.deparse.length = 0)

# preprocess
message("Preprocessing data...")
source(paste0(wd, "/Preprocess.R"), echo = F, print.eval = F, max.deparse.length = 0)

if(redisGet("[R]-PP-Done") == "1"){
  message("Data preprocessed.")
  
  # Execute Strategy 
  source(paste0(wd, "/SS.R"), echo = F, print.eval = F, max.deparse.length = 0)
  message("Executing strategy...")
  
  redisSet("[R]-EX-Done", charToRaw("0"))
  buff <- SS(redisGet("[R]-StrategyVals"), 
             read.csv(header = T, file = paste0(wd, "/Temp/FULL_SET.csv")))
  lastRow <- buff[dim(buff)[1], ]
  
  redisSet("[R]-Strategy-LEn", charToRaw(toString(lastRow$LongEntry)))
  redisSet("[R]-Strategy-SEn", charToRaw(toString(lastRow$ShortEntry)))
  redisSet("[R]-Strategy-LEx", charToRaw(toString(lastRow$LongExit)))
  redisSet("[R]-Strategy-SEx", charToRaw(toString(lastRow$ShortExit)))
  redisSet("[R]-Strategy-SLP", charToRaw(toString(lastRow$SL)))
  redisSet("[R]-Strategy-PSM", charToRaw(toString(lastRow$PSM)))
  redisSet("[R]-Strategy-TIM", charToRaw(toString(date())))

  redisSet("[R]-EX-Done", charToRaw("1"))
 }else{
  message("Preprocess error.")
}

source(paste0(wd, "/readRedis.R"), echo = F, print.eval = F, max.deparse.length = 0)

redisClose()
message("Redis disconnected.")

rm(list = ls())
message("Environment cleared.")