**yadds** is **yet another dynamic dns server**. It uses BIND and wraps a http 
interface compatible with the one of a commercial provider around nsupdate. It 
supports multiple users and multiple zones, but it has not been developed with 
a focus on scalabality to huge setups.

Requirements
============
 * BIND
 * nsupdate
 * Python 3 (including bottle and a lot of other packages)
 * Some WSGI-capable webserver

An imcomplete list of debian packages needed:
```
apt-get install bind9 python3-bottle python3-passlib libapache2-mod-wsgi-py3
```
and a lot of dependencies.


Setup
=====

WIP
