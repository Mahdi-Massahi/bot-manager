packgs <- c("xts", "formattable",
            "rredis", "crayon", "Neb")

suppressMessages(lapply(FUN =  library, packgs, character.only = T, quiet = F))

redisConnect(host = Sys.getenv("REDIS_HOST"))
message("Redis connected.")
options('redis:num'=T)

rm(packgs)