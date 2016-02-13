[![Build Status](https://travis-ci.org/Diviei/cansina.svg?branch=master)](https://travis-ci.org/Diviei/cansina)

News
====

9-1-2016    Cansina support Windows terminal (sorry I didn't test Cansina on Windows boxes)
            You won't have that fancy flash in filtered HTTP codes but it works...    

Cansina
=======

Cansina is a Web Content Discovery Application.

It is well known Web applications doesn't publish all their resources or links to them, 
so the only way to discover those resources is....asking for them!

Useful during a pentesting or web security audit. Cansina mission is to help making 
requests and filtering the responses to tell apart if it is an existing resource or
just an annoying or disguised 404. Of course other kind of useful responses 
(401, 403, ...) are processed in a similar fashion.

The responses are kept in a sqlite database for later process.

There is an ongoing effort to add features via plugins.

Feature requests and comments are welcome.

Screenshot
----------

![CansinaImage](https://github.com/deibit/cansina/raw/gh-pages/images/cansina-showcase.png "Image")

Features
--------

- Multithreading
- Http / Https
- Proxy support
- Data persistence
- Basic Authentication

Usage
-----

cansina.py -h for a comprehensive list of features and choices

**Simple case**

*cansina.py -u target_url -p payload_filename*

Will make GET requests using 4 threads by default 

**Banning HTTP responde codes to output**

*cansina.py -u target_url -p payload_filename -b 404,400,500*

Selected codes will be skipped

**Adding a .php extension to every record in payload**

*cansina.py -u target_url -p payload_filename -e php*

Make all payload entries end with an extension

**Adding a list of extensions**

*cansina.py -u target_url -p payload_filename -e php,asp,aspx*

Same as above but will repeat every request for every extension provided

**Inspecting content**

*cansina.py -u target_url -p payload_filename -c look_for_this_text*

Cansina will report to screen if the content is detected in response

**Filtering by content**

*cansina.py -u target_url -p payload_filename -d look_for_this_text*

If the content is found it will be processed as a 404 Not Found page

**Autodiscriminator**

*cansina.py -u target_url -p payload_filename -D*

First, Cansina will try to make and remember a 404 response and will skip similar responses

**Replacing**

*cansina.py -u target_url/***_this/ -p payload_filename*

Simple string replacing. Useful when a URL pattern is observable

**Size filtering**

*cansina.py -u target_url -s 1495 -p payload_filename*

If you don't want a response and know its size is fixed this could help skipping all those responses

**Uppercase all requests**

*cansina.py -u target_url -U -p payload_filename*

Just make every payload UPPERCASE

**Threading**

*cansina.py -u target_url -t8 -p payload_filename*

Set the threading level. 4 by default.

**Change GET -> HEAD requests**

*cansina.py -u target_url -H -p payload_filename*

Make requests using HEAD HTTP method. Be aware size and content filtering won't work

**Delay between requests**

*cansina.py -u target_url -T 1.25 -p payload_filename*

Set a delay between resquests. Time is set in float format. E.g: 1.25 seconds

**User agent**

*cansina.py -u target_url -p payload_filename -a user_agent*

Set an alternative User-Agent string

**Proxy requests**

*cansina.py -u target_url -p payload_filename -Phttp://127.0.0.1:8080*

Simple http proxy

**Basic authentication**

*cansina.py -u target_url -p payload_filename -Auser:password*

Manages basic authentication

Dependencies
------------

- [requests](https://github.com/kennethreitz/requests)
- Python 2.7.x 
- Python 3.x (soon)

Payloads
--------

- [fuzzdb](https://code.google.com/p/fuzzdb/)

License information
-------------------

Copyright (C) 2013-2015 David García (daganu@gmail.com)

License: GNU General Public License, version 3 or later; see LICENSE.txt
         included in this archive for details.
