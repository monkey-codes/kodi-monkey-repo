import subprocess
import os
import xbmcaddon
import xbmcgui
import xbmc
import urllib2
import json
from functools import partial

_addonid = 'kodi-openvpn-script'
addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')
openvpn_conf_path = '/etc/openvpn/client'

def log_debug(msg):
    xbmc.log( 'script.openvpn: DEBUG: %s' % msg)

def os_call(call):
    return subprocess.check_output([call], shell=True)

def get_geo():
    try:
        url = 'http://ipinfo.io/'
        req = urllib2.Request(url)
        req.add_header('Accept', '*/*')
        req.add_header('User-Agent', 'curl/7.57.0')
        f = urllib2.urlopen(req, timeout=5)
        result = json.loads(f.read())
        f.close()
        latlng = result['loc'].split(',')
        result['latitude'] = latlng[0]
        result['longitude'] = latlng[1]
        return result
    except:
        return {'latitude' : '30.3731', 'longitude': '-97.6756', 'city':'Unknown', 'country': 'Unknown'}

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
    ovpnfiles.append({'label': "Disconnect from %s" % get_geo()['city'], 'func':cmd_systemctl_vpn_factory("stop"), 'complete': select_noop})
    for path in os.listdir(openvpn_conf_path):
        if os.path.splitext(path)[1] == '.ovpn':
            log_debug('Found configuration: [%s]' % path)
            ovpnfiles.append({'label': path[:-5], 'func': cmd_switch_vpn, 'complete': select_noop, 'conf_file': path })
    select('VPN',ovpnfiles)

def cmd_busy(command):
    def busy_command(option):
        xbmc.executebuiltin( "ActivateWindow(busydialog)" )
        retVal = command(option)
        xbmc.executebuiltin( "Dialog.Close(busydialog)" )
        return retVal
    return busy_command

def cmd_systemctl_factory(service, action): return lambda option: subprocess.check_call(["sudo","systemctl", action, service])

cmd_systemctl_vpn_factory = partial(cmd_systemctl_factory, "openvpn-client@client")

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
    return True

def cmd_select_vpn(*args):
    select_vpn()

def cmd_display_current_location(*args):
    #map_style='format=png&maptype=roadmap&style=element:geometry%7Ccolor:0x212121&style=element:labels.icon%7Cvisibility:off&style=element:labels.text.fill%7Ccolor:0x757575&style=element:labels.text.stroke%7Ccolor:0x212121&style=feature:administrative%7Celement:geometry%7Ccolor:0x757575&style=feature:administrative.country%7Celement:labels.text.fill%7Ccolor:0x9e9e9e&style=feature:administrative.land_parcel%7Cvisibility:off&style=feature:administrative.locality%7Celement:labels.text.fill%7Ccolor:0xbdbdbd&style=feature:administrative.neighborhood%7Cvisibility:off&style=feature:poi%7Celement:labels.text%7Cvisibility:off&style=feature:poi%7Celement:labels.text.fill%7Ccolor:0x757575&style=feature:poi.business%7Cvisibility:off&style=feature:poi.park%7Celement:geometry%7Ccolor:0x181818&style=feature:poi.park%7Celement:labels.text.fill%7Ccolor:0x616161&style=feature:poi.park%7Celement:labels.text.stroke%7Ccolor:0x1b1b1b&style=feature:road%7Celement:geometry.fill%7Ccolor:0x2c2c2c&style=feature:road%7Celement:labels%7Cvisibility:off&style=feature:road%7Celement:labels.icon%7Cvisibility:off&style=feature:road%7Celement:labels.text.fill%7Ccolor:0x8a8a8a&style=feature:road.arterial%7Cvisibility:off&style=feature:road.arterial%7Celement:geometry%7Ccolor:0x373737&style=feature:road.highway%7Celement:geometry%7Ccolor:0x3c3c3c&style=feature:road.highway%7Celement:labels%7Cvisibility:off&style=feature:road.highway.controlled_access%7Celement:geometry%7Ccolor:0x4e4e4e&style=feature:road.local%7Cvisibility:off&style=feature:road.local%7Celement:labels.text.fill%7Ccolor:0x616161&style=feature:transit%7Cvisibility:off&style=feature:transit%7Celement:labels.text.fill%7Ccolor:0x757575&style=feature:water%7Celement:geometry%7Ccolor:0x000000&style=feature:water%7Celement:labels.text%7Cvisibility:off&style=feature:water%7Celement:labels.text.fill%7Ccolor:0x3d3d3d'
    map_style = 'format=png&maptype=roadmap&style=element:geometry%7Ccolor:0x212121&style=element:labels.icon%7Cvisibility:off&style=element:labels.text.fill%7Ccolor:0x757575&style=element:labels.text.stroke%7Ccolor:0x212121&style=feature:administrative%7Celement:geometry%7Ccolor:0x757575&style=feature:administrative.country%7Celement:labels.text.fill%7Ccolor:0x9e9e9e&style=feature:administrative.land_parcel%7Cvisibility:off&style=feature:administrative.locality%7Celement:labels.text.fill%7Ccolor:0xbdbdbd&style=feature:poi%7Celement:labels.text.fill%7Ccolor:0x757575&style=feature:poi.park%7Celement:geometry%7Ccolor:0x181818&style=feature:poi.park%7Celement:labels.text.fill%7Ccolor:0x616161&style=feature:poi.park%7Celement:labels.text.stroke%7Ccolor:0x1b1b1b&style=feature:road%7Celement:geometry.fill%7Ccolor:0x2c2c2c&style=feature:road%7Celement:labels.text.fill%7Ccolor:0x8a8a8a&style=feature:road.arterial%7Celement:geometry%7Ccolor:0x373737&style=feature:road.highway%7Celement:geometry%7Ccolor:0x3c3c3c&style=feature:road.highway.controlled_access%7Celement:geometry%7Ccolor:0x4e4e4e&style=feature:road.local%7Celement:labels.text.fill%7Ccolor:0x616161&style=feature:transit%7Celement:labels.text.fill%7Ccolor:0x757575&style=feature:water%7Celement:geometry%7Ccolor:0x0d0d0d&style=feature:water%7Celement:labels.text.fill%7Ccolor:0x0d0d0d'
    map_url = 'https://maps.googleapis.com/maps/api/staticmap?key=AIzaSyDXdwZa6dduC_knaIzovbmim0JrI4CGvUE&markers=latitude,longitude&center=latitude,longitude&zoom=1&%s&size=860x325&scale=2' % map_style
    geo = get_geo()
    latitude,longitude = geo['latitude'],geo['longitude']
    systemctl = os_call("systemctl status openvpn-client@client | grep \"Active\"")
    active_config = os_call("readlink -f /etc/openvpn/client/client.conf")
    window = xbmcgui.WindowXMLDialog('custom-DialogVPNInfo.xml',xbmcaddon.Addon().getAddonInfo('path').decode('utf-8'), 'default', '1080p')
    win =xbmcgui.Window(10001)
    win.setProperty( 'VPN.ExitNode' ,  '%s, %s' % (geo['city'], geo['country']))
    win.setProperty( 'VPN.Flag' ,  'http://flagpedia.net/data/flags/normal/%s.png' % geo['country'].lower())
    win.setProperty( 'VPN.ActiveConfig' , active_config.split('/')[-1][:-6])
    win.setProperty( 'VPN.Status' , systemctl.strip())
    win.setProperty( 'VPN.Map' , map_url.replace('latitude', latitude).replace('longitude', longitude))
    log_debug(dir(window))
    window.doModal()
    log_debug(xbmcgui.getCurrentWindowId())
    del window


def cmd_noop(*args):
    pass

def select_noop():
    pass

def select_main():
    log_debug('detecting changes!!!')
    menu = [
            {'label': 'Display IP location', 'func': cmd_busy(cmd_display_current_location), 'complete': select_main},
            {'label': 'Select VPN', 'func': cmd_busy(cmd_select_vpn), 'complete': select_main}
    ]
    select('OpenVPN', menu, default=select_noop)


select_main()


