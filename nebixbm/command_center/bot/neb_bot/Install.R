packs <- c("xts", "formattable",
           "rredis", "crayon")

message("Downloading required packages for R...")
install.packages(packs,
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