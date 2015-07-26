from string import Template
import subprocess

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
