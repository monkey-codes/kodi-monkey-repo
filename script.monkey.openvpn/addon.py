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
    #TODO delete
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

def get_geo():
    try:
        url = 'http://api.ipinfodb.com/v3/ip-city/?key=24e822dc48a930d92b04413d1d551ae86e09943a829f971c1c83b7727a16947f&format=xml'
        req = urllib2.Request(url)
        f = urllib2.urlopen(req, timeout=5)
        result = f.read()
        f.close()
        result =  BeautifulSoup(result)
        return result.response
    except:
        return BeautifulSoup("""
        <?xml version="1.0" encoding="UTF-8"?>
        <Response>
            <statusCode>OK</statusCode>
            <statusMessage></statusMessage>
            <ipAddress>64.245.52.2</ipAddress>
            <countryCode>US</countryCode>
            <countryName>United States</countryName>
            <regionName>Texas</regionName>
            <cityName>Austin</cityName>
            <zipCode>78753</zipCode>
            <latitude>30.3731</latitude>
            <longitude>-97.6756</longitude>
            <timeZone>-05:00</timeZone>
        </Response>
        """).response

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

def cmd_busy(command):
    def busy_command(option):
        xbmc.executebuiltin( "ActivateWindow(busydialog)" )
        retVal = command(option)
        xbmc.executebuiltin( "Dialog.Close(busydialog)" )
        return retVal
    return busy_command

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

def cmd_display_current_location_2(*args):
    #log_debug(xbmcaddon.Addon().getAddonInfo('path').decode('utf-8'))
    map_url = 'https://maps.googleapis.com/maps/api/staticmap?key=AIzaSyDXdwZa6dduC_knaIzovbmim0JrI4CGvUE&markers=latitude,longitude&center=latitude,longitude&zoom=1&format=png&maptype=roadmap&style=element:geometry%7Ccolor:0x212121&style=element:labels.icon%7Cvisibility:off&style=element:labels.text.fill%7Ccolor:0x757575&style=element:labels.text.stroke%7Ccolor:0x212121&style=feature:administrative%7Celement:geometry%7Ccolor:0x757575&style=feature:administrative.country%7Celement:labels.text.fill%7Ccolor:0x9e9e9e&style=feature:administrative.land_parcel%7Cvisibility:off&style=feature:administrative.locality%7Celement:labels.text.fill%7Ccolor:0xbdbdbd&style=feature:administrative.neighborhood%7Cvisibility:off&style=feature:poi%7Celement:labels.text%7Cvisibility:off&style=feature:poi%7Celement:labels.text.fill%7Ccolor:0x757575&style=feature:poi.business%7Cvisibility:off&style=feature:poi.park%7Celement:geometry%7Ccolor:0x181818&style=feature:poi.park%7Celement:labels.text.fill%7Ccolor:0x616161&style=feature:poi.park%7Celement:labels.text.stroke%7Ccolor:0x1b1b1b&style=feature:road%7Celement:geometry.fill%7Ccolor:0x2c2c2c&style=feature:road%7Celement:labels%7Cvisibility:off&style=feature:road%7Celement:labels.icon%7Cvisibility:off&style=feature:road%7Celement:labels.text.fill%7Ccolor:0x8a8a8a&style=feature:road.arterial%7Cvisibility:off&style=feature:road.arterial%7Celement:geometry%7Ccolor:0x373737&style=feature:road.highway%7Celement:geometry%7Ccolor:0x3c3c3c&style=feature:road.highway%7Celement:labels%7Cvisibility:off&style=feature:road.highway.controlled_access%7Celement:geometry%7Ccolor:0x4e4e4e&style=feature:road.local%7Cvisibility:off&style=feature:road.local%7Celement:labels.text.fill%7Ccolor:0x616161&style=feature:transit%7Cvisibility:off&style=feature:transit%7Celement:labels.text.fill%7Ccolor:0x757575&style=feature:water%7Celement:geometry%7Ccolor:0x000000&style=feature:water%7Celement:labels.text%7Cvisibility:off&style=feature:water%7Celement:labels.text.fill%7Ccolor:0x3d3d3d&size=860x325'
    geo = get_geo()
    latitude,longitude = geo.latitude.string,geo.longitude.string
    systemctl = os_call("systemctl status openvpn@client | grep \"Active\"")
    active_config = os_call("readlink -f /etc/openvpn/client.conf")
    window = xbmcgui.WindowXMLDialog('custom-DialogVPNInfo.xml',xbmcaddon.Addon().getAddonInfo('path').decode('utf-8'), 'default', '1080p')
    win =xbmcgui.Window(10001)
    win.setProperty( 'VPN.ExitNode' ,  '%s, %s' % (geo.cityname.string, geo.countryname.string))
    win.setProperty( 'VPN.Flag' ,  'http://flagpedia.net/data/flags/normal/%s.png' % geo.countrycode.string.lower())
    win.setProperty( 'VPN.ActiveConfig' , active_config.split('/')[-1][:-6])
    win.setProperty( 'VPN.Status' , systemctl.strip())
    #win.setProperty( 'VPN.Map' , 'https://maps.googleapis.com/maps/api/staticmap?key=AIzaSyDXdwZa6dduC_knaIzovbmim0JrI4CGvUE&markers=30.3731,-97.6756&center=30.3731,-97.6756&zoom=2&format=png&maptype=roadmap&style=element:geometry%7Ccolor:0x212121&style=element:labels.icon%7Cvisibility:off&style=element:labels.text.fill%7Ccolor:0x757575&style=element:labels.text.stroke%7Ccolor:0x212121&style=feature:administrative%7Celement:geometry%7Ccolor:0x757575&style=feature:administrative.country%7Celement:labels.text.fill%7Ccolor:0x9e9e9e&style=feature:administrative.land_parcel%7Cvisibility:off&style=feature:administrative.locality%7Celement:labels.text.fill%7Ccolor:0xbdbdbd&style=feature:administrative.neighborhood%7Cvisibility:off&style=feature:poi%7Celement:labels.text%7Cvisibility:off&style=feature:poi%7Celement:labels.text.fill%7Ccolor:0x757575&style=feature:poi.business%7Cvisibility:off&style=feature:poi.park%7Celement:geometry%7Ccolor:0x181818&style=feature:poi.park%7Celement:labels.text.fill%7Ccolor:0x616161&style=feature:poi.park%7Celement:labels.text.stroke%7Ccolor:0x1b1b1b&style=feature:road%7Celement:geometry.fill%7Ccolor:0x2c2c2c&style=feature:road%7Celement:labels%7Cvisibility:off&style=feature:road%7Celement:labels.icon%7Cvisibility:off&style=feature:road%7Celement:labels.text.fill%7Ccolor:0x8a8a8a&style=feature:road.arterial%7Cvisibility:off&style=feature:road.arterial%7Celement:geometry%7Ccolor:0x373737&style=feature:road.highway%7Celement:geometry%7Ccolor:0x3c3c3c&style=feature:road.highway%7Celement:labels%7Cvisibility:off&style=feature:road.highway.controlled_access%7Celement:geometry%7Ccolor:0x4e4e4e&style=feature:road.local%7Cvisibility:off&style=feature:road.local%7Celement:labels.text.fill%7Ccolor:0x616161&style=feature:transit%7Cvisibility:off&style=feature:transit%7Celement:labels.text.fill%7Ccolor:0x757575&style=feature:water%7Celement:geometry%7Ccolor:0x000000&style=feature:water%7Celement:labels.text%7Cvisibility:off&style=feature:water%7Celement:labels.text.fill%7Ccolor:0x3d3d3d&size=860x325')
    win.setProperty( 'VPN.Map' , map_url.replace('latitude', geo.latitude.string).replace('longitude',geo.longitude.string))
    log_debug(dir(window))
    window.doModal()
    log_debug(xbmcgui.getCurrentWindowId())
    del window
    #AIzaSyDXdwZa6dduC_knaIzovbmim0JrI4CGvUE

    #xbmcgui.Dialog().ok('Current Status', systemctl.strip(), 'Exit node: %s' % get_geolocation(), 'Active VPN Config: %s' % active_config.split('/')[-1][:-5])


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
            {'label': 'Display IP location', 'func': cmd_busy(cmd_display_current_location_2), 'complete': select_main},
            {'label': 'Select VPN', 'func': cmd_busy(cmd_select_vpn), 'complete': select_main}
            #{'label': 'Exit', 'func': cmd_noop, 'complete': select_noop}
    ]
    select('OpenVPN', menu, default=select_noop)


select_main()


