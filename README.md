# Instructions

The latest version of Route-O-Matic is writen in Python/flask. To start the
server:

```
python3 route-o-matic.py 
```

This now uses waitress since it is supposed to be a production server for
flask based apps. route-o-matic.py embeds the port number which by default
is 8200.

The port can be changed by editing route-o-matic.py. 

```
http://192.168.92.100:8200
```

Python modules used:
waitress
pymysql
flask

