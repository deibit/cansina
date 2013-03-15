Cansina
=======

Cansina is a (yet another) Web Content Discovery Application.

It takes general available lists of common path and files used by web applications
and make URL requests looking back to the server response code. Cansina stores the information
in a sqlite database (omitting 404 responses). One for every new url (think this as a kind of projects feature)
and the same database for every new payload on the same url.

It aims to be (very) simple and straight to use doing only one thing: Discover content.

The app is far from being finished, probably is poorly coded and I wouldn't recommend it
to use in a serious pentesting session.

Lists from fuzzdb are included in this repository for convenience but are
not part of the project. You can use whatever list you want.

Feature requests and comments are welcome.

![CansinaImage](https://github.com/deibit/cansina/blob/gh-pages/images/cansina-showcase.png "Image")

Features
--------

- Threads (well, processes)
- HTTP/S Proxy support (thanks to requests)
- Data persistance (sqlite3)
- Support for multiextensions list (-e php,asp,aspx,txt...)
- Content inspector (will watch for a specific string inside web page content)
- Skip fake 404 (best as possible)
- Skip by filtering content
- Replacing (for URL fuzzing)
- Reporting tool

Some use cases
--------------

Look at python cansina.py -h for a comprehensive list of features and choices

**Basic use**

cansina.py -u target_site_url -p payload_filename

**Banning HTTP responde codes to output**

cansina.py -u target_site_url -p payload_filename -b 404,400,500

**Adding a .php extension to every record in payload**

cansina.py -u target_site_url -p payload_filename -e php

**Adding a list of extensions**

cansina.py -u target_site_url -p payload_filename -e php,asp,aspx

**Inspecting content**

cansina.py -u target_site_url -p payload_filename -c look_for_this_text

**Filtering by content**

cansina.py -u target_site_url -p payload_filename -d look_for_this_text

**Autodiscriminator**

cansina.py -u target_site_url -p payload_filename -D

**Replacing**

cansina.py -u target_site_url/***_this/ -p payload_filename

Dependencies
------------

- [requests](https://github.com/kennethreitz/requests)
- Python 2.7 (I didn't test it before or above 2.7 version)

Thanks
------

- [fuzzdb](https://code.google.com/p/fuzzdb/)

License information
-------------------

Copyright (C) 2013 David García (daganu@gmail.com)

License: GNU General Public License, version 3 or later; see LICENSE.txt
         included in this archive for details.
