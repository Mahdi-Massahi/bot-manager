message("   __    __")
message("  /  \\  / /")
message(" / /\\ \\/ / ")
message("/_/  \\__/ebix (TM)")

if(!require(devtools)){
  install.packages("devtools")
}else{
  require("devtools")
}

packs <- c("xts", "formattable",
           "rredis", "crayon")

version <- c("0.12-0", "0.2.0.1",
             "1.7.0", "1.3.4")

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
fee <- 0.075
rredis::redisSet("neb_bot:[S]-Bybit-Maker-Fee", charToRaw(toString(fee)))
rmrule <- 1
rredis::redisSet("neb_bot:[S]-RMRule", charToRaw(toString(rmrule)))

rredis::redisSet("neb_bot:[R]-StrategyVals", c(14, 0.05, rmrule, fee))
rredis::redisClose()

rm(packs)

q(save = "no")