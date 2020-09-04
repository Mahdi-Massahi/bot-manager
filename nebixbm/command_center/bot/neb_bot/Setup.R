packgs <- c("xts", "formattable",
            "rredis", "crayon", "Neb")

suppressMessages(lapply(FUN =  library, packgs, character.only = T, quiet = F))

redisConnect(host = Sys.getenv("REDIS_HOST"))
message("Redis connected.")

redisSet("[R]-StrategyVals", c(14, 0.05, 3))

options('redis:num'=T)

rm(packgs)