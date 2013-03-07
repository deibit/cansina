Cansina
=======

Cansina is a (yet another) Web Content Discovery Application.

It takes general available dictionaries of common path and files used by web applications
and make URL requests looking back to the server response code. Cansina stores the information
in a sqlite database (omitting 404 responses). One for every new url (think this as a kind of projects feature)
and the same database for every new payload on the same url.

It aims to be (very) simple and directed to use doing only one thing: Discover content.

The app is far from being finished, probably is poorly coded and I wouldn't recommend it
to use in a serious pentesting session.

Feature requests and comments are welcome.

Features
--------

- Threads (well, multiprocesses)
- HTTP/S Proxy support (thanks to requests)
- Data persistance (sqlite3)
- Support for multiextensions list (-e php,asp,aspx,txt...)
- (more planned)

Some use cases
--------------

python cansina.py -h

**Basic use**

cansina.py -u www.hispasec.com -p payload_filename

**Banning HTTP responde codes to output**

cansina.py -u www.hispasec.com -p payload_filename -b 404,400,500

**Adding a .php extension to every record in payload**

cansina.py -u www.hispasec.com -p payload_filename -e php

**Adding a list of extensions**

cansina.py -u www.hispasec.com -p payload_filename -e php,asp,aspx

Dependencies
------------

- [requests](https://github.com/kennethreitz/requests)
- Python 2.7 (I didn't test it before or above 2.7 version)

Thanks for the lists
--------------------

- [wfuzz](http://www.edge-security.com/wfuzz.php)
- [Dirbuster](https://sourceforge.net/projects/dirbuster/)
- [fuzzdb](https://code.google.com/p/fuzzdb/)


