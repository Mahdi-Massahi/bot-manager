# Nebix Bot Manager (NBM) installation

## Install Docker Engine on local linux machine

Download Docker Engine files from link bellow, choose your Ubuntu version, then browse to `pool/stable/`, choose `amd64`, `armhf`, or `arm64`, and download the `.deb` file for the Docker Engine version you want to install.
```shell
https://download.docker.com/linux/ubuntu/dists/
````

Check your Ubuntu version:
```shell
lsb_release -a

output:
    No LSB modules are available.
    Distributor ID:	Ubuntu
    Description:	Ubuntu 20.04.2 LTS
    Release:	20.04
    Codename:	focal
```

Install all downloaded files, changing the path below to the path where you downloaded the Docker package.
```shell
sudo dpkg -i /path/to/package.deb
```

Verify that Docker Engine is installed correctly by running the `hello-world` image.
```shell
sudo docker run hello-world
```
Source: [docs.docker.com](https://docs.docker.com/engine/install/ubuntu/)


## Install Docker Engine on remote linux machine

1. Update the `apt` package index and install packages to allow `apt` to use a repository over HTTPS:
```shell
sudo apt-get update
sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
```

2. Add Docker’s official GPG key:
```shell
 curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```

3. Use the following command to set up the stable repository. 
```shell
echo \
  "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

4. Update the `apt` package index, and install the latest version of Docker Engine and containerd:
```shell
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
```

5. Verify that Docker Engine is installed correctly by running the `hello-world` image.
```shell
sudo docker run hello-world
```
This command downloads a test image and runs it in a container. When the container runs, it prints an informational message and exits.  
After installation it is recommended to empty caches. For doing this, follow the instructions is _Empty Caches_ section at the end of this documentation.

## Starting Nebix Bot Manager (NBM)

### Prepare docker files

There is a slight different on local- and server- mode, thus make sure the code is specialized for local-mode in `DockerFile`.
The differance is, the second mode enables nebixbm update via GitLab. In case of need you can enable this features by applying mentioned modifications. 

```dockerfile
# ON LOCAL BEGIN
RUN mkdir -p /nebix/nbm
WORKDIR /nebix/nbm
COPY . .
# END

# ON SERVER BEGIN
#WORKDIR /nebix/
#RUN git clone git@gitlab.com:nebix-group/nbm.git
#WORKDIR /nebix/nbm
# END
```

### Make files ready
Ignore this step if you have have the project's files on.
The general form of the copy command is: 
```shell
scp -P <potr> -r <src> <user>@<ip>:~/<dest>
```
Project file must be in the `/home/nebix/` directory in the server. You may also need to add private key manualy. 
To do so, use the extention `-i <path-to-private-key>` after scp command. 

### Running Docker

Change the path to a directory to which `DockerFile` exists.
```shell
cd /path/to/nbm
````
Build container:
```shell
docker-compose up --build
```
_Note: Adding `-d` or `--detach` runs containers in the background, print new container names._

List the docker containers name
```commandline
docker ps 
```
_Note: Adding `--format "{{.Names}}"` only lists the container names._

Before bashing to container you may need to open a new tmux session. for further information check tmux cheatsheet.

The main container for NBM may have the name `nbm_nebixbm_1`. Bash to the container by the following command:
```commandline
docker exec -it nbm_nebixbm_1 bash
```
Use the command `nebixbm` to check if everything is working fine.

Output:
```commandline
root@9ac7a9036e1f:/nebix/nbm# nebixbm
usage: nebixbm <command(s)>

Nebix Bot Manager (nebixbm)
nebixbm 2.2.1
proudly developed by Nebix Team!

optional arguments:
  -h, --help            show this help message and exit
  -p, --print-bots
  -pr, --print-running-bots
  -pt, --print-terminated-bots
  -r <bot name>, --run <bot name>
  -t <bot id>, --terminate <bot id>
  -oo, --only-output    only return results (no sugar-coating)
  -pld, --print-logs-dir
                        print logfiles directory
  --delete-all-logs     delete all logfiles
  -ta, --terminate-all  terminate all bots
  -u, --update          update codes
  -v, --version         print current version
```

## Empty Caches
It is highly recommended emptying cached files periodically every 6 month.
Use the following commands to do so.
```commandline
sudo sh -c 'echo 1 >/proc/sys/vm/drop_caches'
sudo sh -c 'echo 2 >/proc/sys/vm/drop_caches'
sudo sh -c 'echo 3 >/proc/sys/vm/drop_caches'
```
_____
Updates:  
_2021 Jul 11 19:29 by Mahdi Massahi - Initialized._
_2021 Jul 11 21:56 by Mahdi Massahi - Empty Caches added._
_2021 Jul 20 21:01 by Mahdi Massahi - SCP files to server added._
