message("   __    __")
message("  /  \\  / /")
message(" / /\\ \\/ / ")
message("/_/  \\__/ebix (TM)")

packs <- c("rredis", "xts", "zoo", "rmarkdown")

message("Checking local packages for R...")

suppressWarnings(
  do_install <- !unlist(lapply(packs, require, character.only = T))
)

if(any(do_install)){
  message("Downloading required packages for R...")
  packs <- packs[do_install]
  for(i in 1:length(packs)){
    install.packages(package = packs[i])
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