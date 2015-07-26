from bottle import route, run, request, parse_auth, abort, auth_basic
from string import Template
import subprocess
import os, configparser
from passlib.hash import sha256_crypt
import ipaddress

ZONESFNAME = 'zones.ini'
USERSFNAME = 'users.ini'
CFGPATHS  = [os.path.join(os.path.dirname(__file__), '../etc/'), ]


nsupdate_template = Template(
"""
server $server
key $keyalgo:$keyname $key
zone $zone
update delete $host $rr
update add $host $ttl $rr $ip
send
"""
)



class ddnsZone:
    server  = ""
    keyname = ""
    keyalgo = ""
    key     = ""
    zone    = ""
    ttl     = 60
    
    #zonename is the name of the section
    def initFromConfig(this, config, zonename):
        this.zone    = zonename
        this.server  = config.get(zonename, 'server')
        this.keyname = config.get(zonename, 'keyname')
        this.keyalgo = config.get(zonename, 'keyalgo')
        this.key     = config.get(zonename, 'key')
        this.ttl     = config.get(zonename, 'ttl')

    def callNsupdate(this, cmds):
        cmdsB = cmds.encode(encoding='ascii')

        p = subprocess.Popen("nsupdate", stdin  = subprocess.PIPE,
                                         stdout = subprocess.PIPE,
                                         stderr = subprocess.PIPE)
        stdout, stderr = p.communicate(input=cmdsB)

        if (not stdout == b'') or (not stderr == b''):
            print(stderr)
            print(stdout)
            return "dnserr"
        return None

    def do_update(this, host, ip, ipv):
        if (ipv == 4):
            rr = "A"
        elif (ipv == 6):
            rr = "AAAA"
        else:
            return "error: "+str(ipv)
    
        c = { 'server'  : this.server,
              'keyname' : this.keyname,
              'keyalgo' : this.keyalgo,
              'key'     : this.key,
              'zone'    : this.zone,
              'ttl'     : this.ttl,
              'host'    : host,
              'ip'      : ip,
              'rr'      : rr }
    
        nsupd  = nsupdate_template.substitute(c)

        return this.callNsupdate(nsupd)


class ddnsUser:
    username  = ""
    password  = ""
    hostnames = []

    def initFromConfig (this, config, username):
        this.username  = username
        this.password  = config.get(username, 'password')
        hostnames      = config.get(username, 'hostnames')
        this.hostnames = hostnames.split(",")

    def ownsHostname (this, hostname):
        for h in this.hostnames:
            if (hostname == h):
                return True
        return False

    def checkPassword (this, password):
        return sha256_crypt.verify(password, this.password)

def auth(user, pw):
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

    return None
        

@route('/nic/update')
@auth_basic(auth)
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


configfiles = [ os.path.join(p, ZONESFNAME) for p in CFGPATHS]
config = configparser.ConfigParser()
config.read(configfiles)

usersfiles = [ os.path.join(p, USERSFNAME) for p in CFGPATHS]
usersC = configparser.ConfigParser()
usersC.read(usersfiles)

ddnsZones = []
for s in config.sections():
    d = ddnsZone()
    d.initFromConfig(config, s)
    ddnsZones.append(d)

ddnsUsers = []
for s in usersC.sections():
    u = ddnsUser()
    u.initFromConfig(usersC, s)
    ddnsUsers.append(u)

run(host='localhost', port=8080)
