# Infrastruture

## Summary 

In this document we'll discuss the security measures that we've taken to ensure safety of the bot manager and some of the other steps we took to get infrastructure ready for production.

## Security

### New user

After loging into the server, there was the one and only user which was `root`. We created a new limited user called `nebix` and added the user to the sudo group to gain root access when necessary.

### SSH port change

We changed the default port 22 to port 16180. Some bots look for the default SSH ports to flood attack the server. This measure prevents it.

### SSH configuration

We changed some of the elements in the SSH config file such as:
- Set `PermitRootLogin` to `no` to prevent root SSH access - only people who are aware of a username (in our case, `nebix`) can access it
- Set `PasswordAuthentication` to no to prevent password exploit attacks. By denying the password athentication we only let SSH access to be gained via SSH keys.

And we generated a RSA-2048 private and public key and copied the public key outside so we could SSH via it later on. Also for more security we set a password on the key file.

### Firewall configuration

After checking for installation of UFW (Uncomplicated Firewall) since we won't use any ports other than SSH port, we denied incoming for every port (except the SSH one) and double checked it by checking the UFW table. Then enabling and restarting the service were the next steps as usual.

### Untouched security steps

As there is no incoming request to server, we did not take any measures to secure these items:

- Securing shared memory
- Disabling insecure SSL versions

And a few more which were not really relevent to our needs.


## Installation

### Updates & Upgrades

We updated and upgraded the system the first time we started to use it. 

*Warning*: Please be aware of possible unknown consequence of system update as it might break the running code! Only upgrading security packages are advised.

### Docker & Docker-Compose

Both docker and docker-compose were installed according to docker.com manual and security measures were taken as suggested.

### HTop, ZSH, Oh-My-ZSH, Vim, Cowsay and...

Several useful trusted softwares were also installed to make our lives easier and more fun :)