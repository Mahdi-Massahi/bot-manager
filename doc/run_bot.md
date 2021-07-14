# How to run a bot on NBM

The general form of running any bot has the following routine. For further information please refer to documentation of the tended bot itself. 

1. Make sure you have installed nebixbm properly (check Installation.md)
2. Check available bots by using _show bots_ command:
```commandline
nebixbm -p
```
output:
```commandline
Available Bots:
        - neb_bot 3.0.0-Stable: nebixbm.command_center.bot.neb_bot.neb_bot
```
3. Select a bot name and copy it (bot names are in bold font). In this case the bot name is `neb_bot`.
   
4. Use command `nebixbm -r <bot name>` to run selected bot
    `<bot name>` is the copied name of your selected bot.
5. Check `nebixbm` message whether the operation was successful, or it has failed
6. Has it been successful you can check the status of your running bot by
    checking the running bots:
    `nebixbm -pr`
    or was it a failure/terminated you could see your bot in terminated
    bots:
    `nebixbm -pt`

_____
Updates:  
_2021 Jul 11 19:43 by Mahdi Massahi - Initialized._  