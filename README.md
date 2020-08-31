# Nebix Bot Manager

Nebix Bot Manager (nebixbm) is a trading bot manager which allows you to automate your trades and create and execute your own trader bot!

**Note:** This project is only Linux compatible at the moment. Please consider using Docker for other platforms.

## Install

#### Docker

Install docker and docker-compose for your platform:

- visit [Get Docker](https://docs.docker.com/get-docker/) to download and for installation guidance.

Navigate to project folder:

- ```cd <cloned path>/nebix-trading-bot/```

Build and run docker images:

- ```docker-compose up --build```

Access nebixbm bash through the containers: (you can use container name instead which is usually named something like: ```nebix-trading-bot_nebixbm_1```)
- ```docker exec -it <container-id> bash```

#### Without Docker

Install dependencies: (with apt, e.g Ubuntu)

- ```sudo apt install -y git python3.8 python3.8-dev python3-pip python3-wheel python3.8-venv r-base```


Navigate to project folder:

- ```cd <cloned path>/nebix-trading-bot/```

From file ".env" change ```NEBIXBM_FILES``` value to match your current path. Also change values of keys starting with "REDIS_" keyword to match your current Redis configurations if you're going to use Redis. (It is considered you have an installed and working Redis database on your host)

Set the environment variables on your host:

- ```export $(grep -v '^#' .env | xargs)```


Create a virtual environment named ```env```:

- ```python3 -m venv env```

Activate the virtual environment:

- ```source env/bin/activate```

Install the requirements:

- ```pip3 install -r requirements.txt```

Install nebixbm:

- ```pip3 install .```

## Run

View nebixbm help:

- ```nebixbm -h```

## Uninstall

#### Docker

Stop the running containers: (or use ```stop``` to stop everything)

- ```docker-compose down```

You can also remove the images and containers if you wish: visit (How To Remove Docker Images and Containers)[https://www.digitalocean.com/community/tutorials/how-to-remove-docker-images-containers-and-volumes]

#### Without Docker

Either delete the virtual environment (delete ```env``` folder) or activate the environment and run:  

- ```pip3 uninstall -y nebixbm```

And after completion you can be sure if it is uninstalled by running a sample command as described in "Run" section above.

**Warning:** It is user's responsibility to unset the environment variables from the host which were set in installation stage.

## Examples

#### print available bots:

  - ```nebixbm -p```

#### run a bot:

- ```nebixbm -r <bot name>```

#### pipe to cd command:

  - ```cd $(nebixbm -shld -oo)```
