message("   __    __")
message("  /  \\  / /")
message(" / /\\ \\/ / ")
message("/_/  \\__/ebix (TM)")

bot_name <- commandArgs(trailingOnly=TRUE)[1]

packs <- c("rredis", "xts", "zoo", "rmarkdown")

message("Checking local packages for R...")

suppressWarnings(
  do_install <- !unlist(lapply(packs, require, character.only = T))
)

if(any(do_install)){
  message("Downloading required packages for R.")
  packs <- packs[do_install]
  for(i in 1:length(packs)){
    message(paste0("Installing ", packs[i], "..."))
    if(packs[i] == "rredis"){
      devtools::install_github("Mahdi-Massahi/rredis")
    }else{
      install.packages(package = packs[i])
    }
  }
}else{
  message("Required libraries are already installed.")
}

rredis::redisConnect(host = Sys.getenv("REDIS_HOST"))

run_test_strategy <- rredis::redisGet(paste0(bot_name, ":[S]-Run-Test-Strategy"))
if(as.logical(run_test_strategy)){
  fee <-  0.075
  rmrule <- 3
  StrategyVals <- c(14, 0.05)
}else{
  fee <- NA
  rmrule <- NA
  StrategyVals <- rep(NA, 9)
  warning("Strategy values must be entered manually.")
}
rredis::redisSet(paste0(bot_name, ":[S]-Bybit-Taker-Fee"),
                 charToRaw(toString(fee)))
rredis::redisSet(paste0(bot_name, ":[S]-RMRule"),
                 charToRaw(toString(rmrule)))
rredis::redisSet(paste0(bot_name, ":[R]-StrategyVals"),
                 StrategyVals)
message("Strategy settings' value initialized.")

rredis::redisClose()

rm(packs)

q(save = "no")