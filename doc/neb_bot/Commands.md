
## Connection to Redis
`rredis::redisConnect(host = Sys.getenv("REDIS_HOST"))`  

## Withdraw
`rredis::redisSet("neb_bot:[S]-Withdraw-Amount", charToRaw("0.002"))`  
`rredis::redisSet("neb_bot:[S]-Withdraw-Apply", charToRaw("TRUE"))`  

## Deposit
`rredis::redisSet("neb_bot:[S]-Deposit-Amount", charToRaw("0.00034955"))`  
`rredis::redisSet("neb_bot:[S]-Deposit-Apply", charToRaw("TRUE"))`  

## Allowed Draw Down
`rredis::redisSet("neb_bot:[S]-Allowed-Drawdown", charToRaw("0.8"))`  

## Reset Local Stop
`rredis::redisSet("neb_bot:[S]-Reset-Local-Stop", charToRaw("FALSE"))`  

## Minimum Trading Balance
`rredis::redisSet("neb_bot:[S]-Minimum-Trading-Balance", charToRaw("0.02"))`  

## RMRule
`rredis::redisGet("neb_bot:[S]-RMRule")`  

`rredis::redisSet("neb_bot:[S]-RMRule", charToRaw(toString(6)))`