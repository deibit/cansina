Cansina
=======

Cansina is a (yet another) Web Content Discovery Application.

It takes general available dictionaries of common path and files used by web applications
and make URL requests looking back to the server response code. Cansina stores the information
in a sqlite database (omitting 404 responses). One for every new url (think this as a project kind feature)
and the same databse for every new payload on the same url.

It tries to be simple and directed to use doing only one thing: Discover content.

The app is far from being finished, probably is poorly coded and I wouldn't recommend it
to use in a serious pentesting session. If you are looking for a true tool take a look at
[wfuzz](http://www.edge-security.com/wfuzz.php)

Feature requests and comments are welcome.

Features
--------

- Threads (well, multiprocesses)
- HTTP/S Proxy support (thanks to requests)
- Data persistance (sqlite3)
- (more planned)


Use
---

python cansina.py -h

Dependencies
------------

- [requests](https://github.com/kennethreitz/requests)
- Python 2.7 (I didn't test it before or above 2.7 version)

Thanks
------

- [Dirbuster](https://sourceforge.net/projects/dirbuster/)
- [fuzzdb](https://code.google.com/p/fuzzdb/)


