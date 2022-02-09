# Installation
## Operating System
Install on every Raspberry Pi SD Card which shall be used Raspian OS. 
Details for installation can be found on their [website](https://www.raspberrypi.com/software/).

Make sure the ssh server is enabled, and you know the password or can login via [ssh-key](https://www.digitalocean.com/community/tutorials/how-to-configure-ssh-key-based-authentication-on-a-linux-server-de).
Also make sure the used password on the PIs is not blank, especially if they are exposed in the (local) network later.
## Software installation
### via Ansible 
Make sure you have ansible installed on your local machine, and the RPis are in the same Network, and you know their IP address.
Enter the hostnames in `setup/hosts.yml` and use the following command to install it on all hosts
```commandline
ansible-playbook setup/setupRPi.yml -i setup/hosts.yml
```
or instead one of the following single hosts 
```commandline
ansible-playbook setup/setupRPi.yml -i rpi1
ansible-playbook setup/setupRPi.yml -i 192.168.1.1
```
### via manual installation

Install the following packages via the system packet manager on the RPis: 
```commandline
sudo apt install git python3 python3-opencv python3-picamera
```
clone the git repo 
```commandline
git clone 
```
install pip requirements (fix the python version)
```commandline
python[37] -m pip install -r requirements.txt
```

