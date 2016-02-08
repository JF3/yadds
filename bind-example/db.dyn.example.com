$ORIGIN .
$TTL 604800	; 1 week
dyn.example.com	IN SOA	ns1.dyn.example.com. dyndns.example.com. (
				2015072929 ; serial
				60         ; refresh (1 minute)
				60         ; retry (1 minute)
				1296000    ; expire (2 weeks 1 day)
				60         ; minimum (1 minute)
				)
			NS	ns1.dyn.example.com.
			A	12.34.56.78

checkip			A	12.34.56.78
checkipv6		A	12.34.56.78
update			A	12.34.56.78
