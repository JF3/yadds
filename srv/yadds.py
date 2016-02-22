from bottle import route, run, request, parse_auth, abort, auth_basic, Bottle, default_app, error
import os, configparser
from passlib.hash import sha256_crypt
import ipaddress

os.chdir(os.path.dirname(__file__))
import sys
sys.path.append(os.path.dirname(__file__))

from ddnsZone import *
from ddnsUser import *

ZONESFNAME = 'zones.ini'
USERSFNAME = 'users.ini'
CFGPATHS   = [os.path.join(os.path.dirname(__file__), '../etc/'), ]

def myAuth(user, pw):
    # room for optimization.... (tree/sqlite/...)
    for u in ddnsUsers:
        if (u.username == user):
            return u.checkPassword(pw)
    return False

def zoneFromHostname (hostname):
    hnps = hostname.split(".")
    domain = ""
    for hnp in hnps[1:]:
        domain = domain + hnp + "."

    domain = domain[:-1]

    # room for optimization.... (tree/sqlite/...)
    for z in ddnsZones:
        if z.zone == domain:
            return z
	# needed for updating non sub domains
        if hostname == z.zone:
            return z

    return None
        

@route('/nic/update')
@auth_basic(myAuth)
def dyndnsUpdate():
    auth = request.headers.get('Authorization')
    username, password = parse_auth(auth)


    hostnames = request.query.hostname
    ipv4 = request.query.myip or ""
    ipv6 = request.query.myip6 or ""

    # FIXME we need a way to adapt the return codes to other interfaces...
    return doUpdate(username, hostnames, ipv4, ipv6)


# Here we assume that the user is authenticated but nothing else has been 
# checked. The idea is, that several interfaces (mimicing different commercial
# providers) shall use the same internal logic.
def doUpdate(username, hostnames, ipv4, ipv6):
    user = None
    for u in ddnsUsers:
        if (u.username == username):
            user = u

    # what about ipv6?
    if (ipv4 == "auto"):
        ipv4 = request.environ.get('REMOTE_ADDR')

    try:
        if not ipv4 == "":
            ipv4 = str(ipaddress.IPv4Address(ipv4))
        if not ipv6 == "":
            ipv6 = str(ipaddress.IPv6Address(ipv6))
    except ValueError:
        return "badip"

    hostnames = hostnames.split(",")
    for hostname in hostnames:
        zone = zoneFromHostname(hostname)
        if zone == None:
            return "nohost"

        if not user.ownsHostname(hostname):
            return "nohost"

        if not ipv4 == "":
            ret = zone.do_update(hostname, ipv4, 4)
            if not ret == None:
                return ret

        if not ipv6 == "":
            ret = zone.do_update(hostname, ipv6, 6)
            if not ret == None:
                return ret

    return "good"

@route('/private/reload')
def triggerReadConfig ():
    ip = request.environ.get('REMOTE_ADDR')

    if (ip == "127.0.0.1" or ip == "::1"):
        readConfig()
        return "done"
    else:
        abort(404, ip)


ddnsZones = []
ddnsUsers = []

def readConfig ():
    del ddnsZones[:]
    del ddnsUsers[:]

    configfiles = [ os.path.join(p, ZONESFNAME) for p in CFGPATHS]
    config = configparser.ConfigParser()
    config.read(configfiles)
    
    usersfiles = [ os.path.join(p, USERSFNAME) for p in CFGPATHS]
    usersC = configparser.ConfigParser()
    usersC.read(usersfiles)
    
    for s in config.sections():
        d = ddnsZone()
        d.initFromConfig(config, s)
        ddnsZones.append(d)
    
    for s in usersC.sections():
        u = ddnsUser()
        u.initFromConfig(usersC, s)
        ddnsUsers.append(u)

readConfig()

def checkip ():
    ip = request.environ.get('REMOTE_ADDR')
    return ip


@route('/')
def slash ():
    up = request.urlparts
    h  = up.hostname.split(".")[0]
    if (h == "checkip" or h == "checkipv6"):
        return checkip()
    else:
        abort(404, "")

#run(host='localhost', port=8080)
#application = default_app()
