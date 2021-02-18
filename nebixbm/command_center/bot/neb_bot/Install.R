message("   __    __")
message("  /  \\  / /")
message(" / /\\ \\/ / ")
message("/_/  \\__/ebix (TM)")

if(!require(devtools)){
  install.packages("devtools")
}else{
  require("devtools")
}

packs <- c("rredis", "xts", "zoo", "rmarkdown")
version <- c("1.7.0", "0.12.1", "1.8-8", "2.5")

message("Checking local packages for R...")

suppressWarnings(
  do_install <- !unlist(lapply(packs, require, character.only = T))
)

if(any(do_install)){
  message("Downloading required packages for R...")
  packs <- packs[do_install]
  version <- version[do_install]
  for(i in 1:length(packs)){
    install_version(package = packs[i],
                    version = version[i])
  }
}else{
  message("Required libraries are already installed.")
}

rredis::redisConnect(host = Sys.getenv("REDIS_HOST"))

run_test_strategy <- redisGet("neb_bot:[S]-Run-Test-Strategy")
if(as.logical(run_test_strategy)){
  fee <-  0.075
  rmrule <- 3
  StrategyVals <- c(14, 0.05)
}else{
  fee <- NA
  rmrule <- NA
  StrategyVals <- rep(NA, 9)
}
rredis::redisSet("neb_bot:[S]-Bybit-Taker-Fee", charToRaw(toString(fee)))
rredis::redisSet("neb_bot:[S]-RMRule", charToRaw(toString(rmrule)))
rredis::redisSet("neb_bot:[R]-StrategyVals", StrategyVals)
message("Strategy settings' value initialized.")

rredis::redisClose()

rm(packs)

q(save = "no")