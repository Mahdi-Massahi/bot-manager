# Instructions for `neb_bot`

## Running Bot 

### 1. Delete all logs [optional]
> _Note: Befor any action, it is recomanded to copy existing logs to local machine._

Logging files are in the relative directory `~/logfiles/` in outside the docker container of the bot manger. 
The volume for logging is shared. Therefore, it can be both available inside and outside the docker container. 
But it's recommended to remove logs using `nebixbm` log-removing command. 
```commandline
nebixbm --delete-all-logs
```
Once logs are removed the volume is unallocated and they would be no longer available both in and 
outside the docker container.

### 2. Check environment variables
Environment variables can be shown by the `env` command.
Required environment variables are listed in the `.env` file. 
Make sure the API key, secret, and IP-address (if provided) are correct and up-t-date. 


### 3. Check strategy internal variables
Internal variables such as symbols and interval, starting and ending time, and other hard-coded variables are 
important to have precise values. Please consider double-checking before running bot.
Make sure the starting time is set precisely. Because some minutes are required to set and check Redis internal variables.


### 4. Run the bot
Use the command bellow to start the bot.
```commandline
nebixbm neb_bot
```
Starting the bot executes some scripts, and it may take a while to make every thing ready.
To continue to the next step, this process must be done completely.

### 5. Set and check RedisDB 
Some variables must be initialized or reset before the first schedule. List of all required variables are in 
`nebixbm/neb_bot/enums.py` as `StrategyVariables` and `StrategySettings`. The method is explained in the next section. 

## Setting RedisDB variables
There are twe methods to check/set RedisDB variables.

###1. Using Redis' `redis-cli`
This method is straightforward and easy to use.

1. Exit from current container. [if needed]
```commandline
exit
```
2. `exec` to the RedisDB container. You may also need root access.
```commandline
docker exec -it nbm_redis_db_1 bash
```
3. Use `redis-cli` to read or write prameters.
```commandline
redis-cli
```

#### Example
```shell
GET neb_bot:[S]-Minimum-Trading-Balance
> "0.007"
SET neb_bot:[S]-Minimum-Trading-Balance 0.006
> OK
```

###2. Using R's `rredis` library
This method can be applied in any container which has access to RedisDB.

1. Inside nebixbm container, open R.
```commandline
R
```
2. Use the folloing commands to connect to the DB.
   set or get any parameter inside DB.
```shell
rredis::redisConnect(host = Sys.getenv("REDIS_HOST"))
```
3. Once you are connected you can manipulate DB using, `rredis::redisSet()` and `rredis::redisGet()` functions.

#### Example
```shell
rredis::redisGet("neb_bot:[S]-Minimum-Trading-Balance")
> [1] "0.006"
> attr(,"redis string value")
> [1] TRUE

rredis::redisSet("neb_bot:[S]-Minimum-Trading-Balance", charToRaw(toString(0.006)))
> "OK"
```

> Note: Some variables inside DB are R objects and its highly recommended using the second method to read or write them. 

##  Withdraw Method
1- Calculate `withdraw_amount` using the formula :  

	withdraw_amount = desired_withdraw_amount * (1 + 0.001)  
	
2- Set the value of `withdraw_amount` in `Redis_DB`
3- Set `withdraw_apply` to `TRUE`  
4- Wait until next trade is open (a notifying email must be sent by then)  
5- As withdraw exchange `desired_withdraw_amount` to desired coin  
6- immediately set `withdraw_apply` to `FALSE`  
7- also set `withdraw_amount` to zero  
8- Done  

## Deposit Method
1- During a trade or after stop-loss hit and before next schedule deposit the desired amount by exchanging or simple deposit  
2- Set `deposit_amount` to the amount you have deposited in `Redis_DB`  
3- Set `deposit_apply` to `TRUE` in `Redis_DB`  
4- Done  

## Updating or Restarting Bot Method

There are some conditions in which updating some files or restarting the bot is required. In such these circumstances, there are some points must be concidered.  
1. Log files
   1) Financial Activity
   2) Orders
   3) Signals
   4) Other log files
  
   
2. RedisDB variables
   1) `Reset-Local-Stop`
   2) `Strategy-Vals`
   3) Other important variables
  
   
3. Environment variables
   1) API keys
   2) Other important variables

In these cases you may want to remove log files or keep them continue appending to the already existing files.  
To reset all logs refer to the instructions in the 1st step of Running Bot section in this document.  
In case of keeping the `Financial-Activty`, you need to set the `<strategy-name>:[S]-Reset-Local-Stop` to `False`.
If setting this lag to `False` is being forgotten, the bot automatically will set it to `False`. 
This means new financial activities will be appended to the previous file. 
 