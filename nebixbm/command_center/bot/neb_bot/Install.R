message("   __    __")
message("  /  \\  / /")
message(" / /\\ \\/ / ")
message("/_/  \\__/ebix (TM)")

if(!require(devtools)){
  install.packages("devtools")
}else{
  require("devtools")
}

packs <- c("rredis")
version <- c("1.7.0")

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
}

rredis::redisConnect(host = Sys.getenv("REDIS_HOST"))
message("Strategy settings' value initialized.")
fee <- NA
rredis::redisSet("neb_bot:[S]-Bybit-Taker-Fee", charToRaw(toString(fee)))
rmrule <- NA
rredis::redisSet("neb_bot:[S]-RMRule", charToRaw(toString(rmrule)))
rredis::redisSet("neb_bot:[R]-StrategyVals", rep(NA, 9))
rredis::redisClose()

rm(packs)

q(save = "no")