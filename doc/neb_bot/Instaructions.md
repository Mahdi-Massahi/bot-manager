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
Strating the bot executes some scripts and it may take a while to make every thing ready.
To continue to the next step, this process must be done completely.

### 5. Set and check RedisDB 
Some variables must be initialized or reset before the first schedule. List of all required variables are in 
`nebixbm/neb_bot/enums.py` as `StrategyVariables` and `StrategySettings`.

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

## Bot Update Method  
   
 