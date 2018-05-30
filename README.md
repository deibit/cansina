Install
=======

pip install --user requests[security]

(try removing --user and install with sudo in case of errors)

git clone --depth=1 https://github.com/deibit/cansina


Fast use
========

Use Python 3 (works on Python 2 too, but 3 is advisable)

$ python3 cansina.py -u <site_url> -p <payload_file> 


News
====

[CHANGELOG](https://github.com/deibit/cansina/blob/master/CHANGELOG.md)


Cansina
=======

[![Build Status](https://travis-ci.org/deibit/cansina.svg?branch=master)](https://travis-ci.org/deibit/cansina)

Cansina is a Web Content Discovery Application.

It is well known Web applications don't publish all their resources or public links, 
so the only way to discover these resources is requesting for them and check the response.

Cansina duty is to help you making requests and filtering and inspecting the responses to tell 
apart if it is an existing resource or just an annoying or disguised 404.

Feature requests and comments are welcome.

Cansina is included in [BlackArch Linux](https://www.blackarch.org/), give it a try! 

Screenshot
----------

![CansinaImage](https://github.com/deibit/cansina/raw/gh-pages/images/cansina-showcase.png "Image")

Features
--------

- Multithreading
- SSL support
- Proxy support
- Data persistence with sqlite database
- Basic Authentication
- Cookie jar
- Resuming
- Path recursion
- Persistent connections
- Complementary tools


Usage
-----

cansina.py -h for a comprehensive list of features and choices.

Look up the [wiki](https://github.com/deibit/cansina/wiki), it's full of information.


Important
---------

This tool is intended to be used in a fair and legal context, meaning, for example,
a penetration testing for which you have been provided previous authorization.

One of its legitimate uses might be the one described in the following article:

- [Forced browsing](https://www.owasp.org/index.php/Forced_browsing) 


Dependencies
------------

- [requests](https://github.com/kennethreitz/requests)
- Python 2.7.x or Python 3


Payloads
--------

Cansina does not come with list but there are some neat projects to supply this:

- [SecList](https://github.com/danielmiessler/SecLists)
- [fuzzdb](https://code.google.com/p/fuzzdb/)


License information
-------------------

Copyright (C) 2013-2017 David García

License: GNU General Public License, version 3 or later; see LICENSE.txt
         included in this archive for details.
