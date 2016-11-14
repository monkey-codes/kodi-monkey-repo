## kodi-monkey-repo

A Kodi repository that contains an OpenVPN script addon. The addon has been tested on a 
[Raspberry Pi running Arch Linux](http://blog.monkey.codes/how-to-setup-kodi-on-a-raspberry-pi/#managevpnthroughkodi)

## Requirements
*  Only works on Linux and has been tested on Arch Linux.
*  OpenVPN installed as a systemd service
*  Kodi user has sudo privileges to stop/start openvpn systemd service and change symlinks in '/etc/openvpn' folder.

## Usage

The OpenVPN addon requires OpenVPN to be installed as a systemd service. All OpenVPN exit node configuration files need to be
in `/etc/openvpn`.

```
$ ln -sf /etc/openvpn/Switzerland.ovpn /etc/openvpn/client.conf
$ systemctl enable openvpn@client.service
$ systemctl start openvpn@client
```

Give `kodi` user permission sudo permissions:

```
$ visudo

...
##
## Cmnd alias specification
##
Cmnd_Alias SWITCH_VPN = /usr/bin/ln -sf /etc/openvpn/* /etc/openvpn/client.conf, /usr/bin/systemctl * openvpn@client

...
##
## User privilege specification
##
# Add this as the last entry in the section
kodi ALL=(ALL) NOPASSWD: SWITCH_VPN
```

Download and [install the repo](http://kodi.wiki/view/add-on_manager#How_to_install_from_a_ZIP_file)

```
$ sudo su - kodi -s /bin/bash
$ cd ~ 
$ wget http://raw.githubusercontent.com/monkey-codes/kodi-monkey-repo/master/dist/repo.monkey.zip
```
