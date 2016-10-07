import subprocess
import os
import xbmcaddon
import xbmcgui
import xbmc
import urllib2
from BeautifulSoup import BeautifulSoup
from functools import partial

_addonid = 'kodi-openvpn-script'
addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')
openvpn_conf_path = '/etc/openvpn'

def log_debug(msg):
    xbmc.log( 'script.openvpn: DEBUG: %s' % msg)

def os_call(call):
    return subprocess.check_output([call], shell=True)

def get_geolocation():
    try:
        url = 'http://api.ipinfodb.com/v3/ip-city/?key=24e822dc48a930d92b04413d1d551ae86e09943a829f971c1c83b7727a16947f&format=xml'
        req = urllib2.Request(url)
        f = urllib2.urlopen(req, timeout=5)
        result = f.read()
        f.close()
        result =  BeautifulSoup(result)
        return "%s, %s" % (result.response.cityname.string, result.response.countryname.string)
    except:
        return "Unknown"

def select(heading, options, default=lambda: select_main):
    labels = [option['label'] for option in options]
    result = xbmcgui.Dialog().select(heading, labels)
    selected = options[result]
    if result == -1:
        log_debug("using default action")
        default()
        return
    selected['func'](selected)
    selected['complete']()

def select_vpn():
    ovpnfiles = []
    ovpnfiles.append({'label': "Disconnect from %s" % get_geolocation(), 'func':cmd_systemctl_vpn_factory("stop"), 'complete': select_noop})
    for path in os.listdir(openvpn_conf_path):
        if os.path.splitext(path)[1] == '.ovpn':
            log_debug('Found configuration: [%s]' % path)
            ovpnfiles.append({'label': path[:-5], 'func': cmd_switch_vpn, 'complete': select_noop, 'conf_file': path })
    select('VPN',ovpnfiles)


def cmd_systemctl_factory(service, action): return lambda option: subprocess.check_call(["systemctl", action, service])

cmd_systemctl_vpn_factory = partial(cmd_systemctl_factory, "openvpn@client")

def cmd_disconnet_vpn(option): cmd_systemctl_vpn_factory("stop")(option)
def cmd_connect_vpn(option): cmd_systemctl_vpn_factory("start")(option)


def cmd_switch_vpn(option):
    conf_path = openvpn_conf_path
    conf_file = option['conf_file']
    cmd_disconnet_vpn(None)
    log_debug("%(conf_path)s/%(conf_file)s" % locals())
    cmd_arr = ["sudo","/usr/bin/ln", "-sf", "%(conf_path)s/%(conf_file)s" % locals(), "%(conf_path)s/client.conf" % locals()]
    cmd =" ".join(cmd_arr)
    log_debug(cmd)
    subprocess.check_call(cmd_arr)
    cmd_connect_vpn(None)
    log_debug(subprocess.check_output(["whoami"]))
    return True

def cmd_select_vpn(*args):
    select_vpn()

def cmd_display_current_location(*args):
    systemctl = os_call("systemctl status openvpn@client | grep \"Active\"")
    active_config = os_call("readlink -f /etc/openvpn/client.conf")
    xbmcgui.Dialog().ok('Current Status', systemctl.strip(), 'Exit node: %s' % get_geolocation(), 'Active VPN Config: %s' % active_config.split('/')[-1][:-5])

def cmd_noop(*args):
    pass

def select_noop():
    pass

def cmd_log(message):
    def log_me(*args):
        xbmc.log( 'script.openvpn: DEBUG: %s' % message)
    return log_me

def select_main():
    menu = [
            {'label': 'Display IP location', 'func': cmd_display_current_location, 'complete': select_main},
            {'label': 'Select VPN', 'func': cmd_select_vpn, 'complete': select_main}
            #{'label': 'Exit', 'func': cmd_noop, 'complete': select_noop}
    ]
    select('OpenVPN', menu, default=select_noop)


select_main()
