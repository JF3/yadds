from bottle import route, run, request, parse_auth, abort, auth_basic
from string import Template
import subprocess
import os, ConfigParser

ZONESNAME = 'zones.ini'
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
    
        nsupd = nsupdate_template.substitute(c)
        print nsupd
        p = subprocess.Popen("nsupdate", stdin=subprocess.PIPE)
        stdout, stderr = p.communicate(nsupd)
     
        # FIXME do error checking
        return 23
    


def pw_check(user, pw):
    #FIXME
    return True

@route('/nic/update')
@auth_basic(pw_check)
def update():
    auth = request.headers.get('Authorization')
#    if not auth:
#        abort(401, 'Access denied')
#
    username, password = parse_auth(auth)

    hostnames = request.query.hostname
    ipv4 = request.query.myip or ""
    ipv6 = request.query.myip6 or ""
    
    hostnames = hostnames.split(",")
    hostname = hostnames[0]
    print hostname
    ddnsZones[0].do_update(hostname, ipv4, 4)

    return hostname


configfiles = [ os.path.join(p, ZONESNAME) for p in CFGPATHS]
config = ConfigParser.ConfigParser()
config.read(configfiles)

ddnsZones = []
for s in config.sections():
    d = ddnsZone()
    d.initFromConfig(config, s)
    ddnsZones.append(d)

run(host='localhost', port=8080)
