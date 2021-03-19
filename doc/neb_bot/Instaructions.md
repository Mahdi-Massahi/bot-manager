# Instructions for `neb_bot`

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
   
 