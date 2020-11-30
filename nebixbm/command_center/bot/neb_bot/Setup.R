packgs <- c("rredis", "Neb")

suppressWarnings(lapply(FUN =  library, packgs, character.only = T, quiet = F))

redisConnect(host = Sys.getenv("REDIS_HOST"))
message("Redis connected.")
options('redis:num'=T)

rm(packgs)