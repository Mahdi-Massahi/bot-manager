packs <- c("xts", "formattable",
           "rredis", "crayon")

message("Downloading required packages for R...")
install.packages(packs,
                 quiet = F,
                 # repos = "https://cloud.r-project.org/",
                 INSTALL_opts = '--no-lock')

rredis::redisConnect(host = Sys.getenv("REDIS_HOST"))
message("Strategy settings' value initialized.")
rredis::redisSet("[R]-StrategyVals", c(14, 0.05, 3))
rredis::redisClose()

rm(packs)

q(save = "no")