# Nebix Bot Manager

Nebix Bot Manager (nebixbm) is a management platform for creating and controlling custom (cryptocurrency) trading bots.

**Note:** This project is only Linux compatible at the moment. Please consider using Docker for other platforms.

## Install

#### With Docker

1. Install docker and docker-compose for your platform: visit [Get Docker](https://docs.docker.com/get-docker/) to download and for installation guidance.
2. Navigate to project folder: ```cd <cloned path>/nebix-trading-bot/```
3. Build and run docker images: ```docker-compose up --build```

Access nebixbm bash through the containers: (you can use container name instead which is usually named something like: ```nebix-trading-bot_nebixbm_1```) ```docker exec -it <container-id> bash```

Redirect the logs: ```docker-compose logs --no-color >& logs.log```

#### Without Docker

1. Install dependencies: (with apt, e.g Ubuntu) ```sudo apt install -y git python3.8 python3.8-dev python3-pip python3-wheel python3.8-venv r-base```
2. Navigate to project folder: ```cd <cloned path>/nebix-trading-bot/```
3. From file ".env" change ```NEBIXBM_FILES``` value to match your current path. Also change values of keys starting with "REDIS_" keyword to match your current Redis configurations if you're going to use Redis. (It is considered you have an installed and working Redis database on your host)
4. Set the environment variables on your host: ```export $(grep -v '^#' .env | xargs)```
5. Create a virtual environment named ```env```: ```python3 -m venv env```
6. Activate the virtual environment: ```source env/bin/activate```
7. Install the requirements: ```pip3 install -r requirements.txt```
8. Install nebixbm: ```pip3 install .```

## Run

View nebixbm help: ```nebixbm -h```

## Uninstall

#### Installed with Docker

1. Stop the running containers: (or use ```stop``` to stop everything) ```docker-compose down```
2. You can also remove the images and containers if you wish: visit [How To Remove Docker Images and Containers](https://www.digitalocean.com/community/tutorials/how-to-remove-docker-images-containers-and-volumes) for more info

#### Without Docker

1. Either delete the virtual environment (delete ```env``` folder) or activate the environment and run: ```pip3 uninstall -y nebixbm```
2. And after completion you can be sure if it is uninstalled by running a sample command as described in "Run" section above.

*Warning:* It is user's responsibility to unset the environment variables from the host which were set in installation stage.

## Examples

- print available bots:
    
    ```nebixbm -p```

- run a bot:

  ```nebixbm -r <bot name>```

- pipe to cd command:

  ```cd $(nebixbm -shld -oo)```
