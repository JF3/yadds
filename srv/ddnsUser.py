from passlib.hash import sha256_crypt

reservedHostnames = [ "ns1", "update" ]

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
        # FIXME There might a better place to do this.
        for r in reservedHostnames:
            if (hostname == r):
                return False

        for h in this.hostnames:
            if (hostname == h):
                return True
        return False

    def checkPassword (this, password):
        return sha256_crypt.verify(password, this.password)
