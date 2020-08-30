# Nebix Bot Manager

Nebix Bot Manager (nebixbm) is a trading bot manager which allows you to automate your trades and create and execute your own trader bot!


## Dependencies:

- ```sudo apt install git python3.8 python3.8-dev python3-pip python3-wheel python3.8-venv```

## Clone / Download

- ```git clone <repository>.git```

## Install

- ```cd <clone path>/nebix-trading-bot/```

- ```sh install.sh```

## Run

- ```source env/bin/activate && nebixbm -h```

## Uninstall

- ```sh uninstall.sh```

## Examples

#### print available bots:

  - ```nebixbm -p```

#### run a bot:

- ```nebixbm -r <bot name>```

#### pipe to cd command:

  - ```cd $(nebixbm -shld -oo)```
