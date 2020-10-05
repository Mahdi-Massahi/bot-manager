packs <- c("xts", "formattable",
           "rredis", "crayon")

message("Checking local packages for R...")

suppressWarnings(
  do_install <- !unlist(lapply(packs, require, character.only = T))
)

message(do_install)

if(any(do_install))
  message("Downloading required packages for R...")
  install.packages(packs[do_install],
                   quiet = F,
                   # repos = "https://cloud.r-project.org/",
                   INSTALL_opts = '--no-lock')

rredis::redisConnect(host = Sys.getenv("REDIS_HOST"))
message("Strategy settings' value initialized.")
fee <- 0.075
rredis::redisSet("neb_bot:[S]-Bybit-Maker-Fee", charToRaw(toString(fee)))
rmrule <- 3
rredis::redisSet("neb_bot:[S]-RMRule", charToRaw(toString(rmrule)))

rredis::redisSet("neb_bot:[R]-StrategyVals", c(14, 0.05, rmrule, fee))
rredis::redisClose()

rm(packs)

q(save = "no")