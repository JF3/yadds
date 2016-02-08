**yadds** is **yet another dynamic dns server**. It uses BIND and wraps a http 
interface compatible to the one of a large commercial provider around nsupdate. 
It supports multiple users and multiple zones, but it has not been developed 
with a focus on scalabality to huge setups.

Requirements
============
 * BIND
 * nsupdate
 * Python 3 (including bottle and a lot of other packages)
 * Some WSGI-capable webserver

An incomplete list of debian packages needed:
```
apt-get install bind9 python3-bottle python3-passlib libapache2-mod-wsgi-py3
```
and a lot of dependencies.


Setup
=====

```
	WSGIDaemonProcess yadds user=www-data group=www-data processes=1 threads=5 home=/var/www/yadds/srv/
	WSGIScriptAlias / /var/www/yadds/srv/yadds.wsgi

	<Directory /var/www/yadds/srv>
		WSGIProcessGroup yadds
		WSGIApplicationGroup %{GLOBAL}
                WSGIPassAuthorization On
        	Order deny,allow
	        Allow from all
	</Directory>
```
WIP

Client configuration
====================

 * FritzBox:
Use the userdefined provider and the following update url:
```
update.dyn.example.com/nic/update?hostname=<domain>&myip=<ipaddr>
```
 * ddclient:
```
login=user1
password=password
server=update.dyn.example.com,	\
protocol=dyndns2		\
host1.dyn.example.com
```
 * wget:
```
wget  --http-user="user1" --http-passwd="password" -o /dev/null -O -  "update.dyn.example.com/nic/update?hostname=host1.dyn.example.com&myip=auto"
```
