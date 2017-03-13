News
====

13-03-2017  New option: -R autoscan robots.txt and use it as a payload

26-01-2017  Fixed 'InsecureRequestsWarning' message

10-08-2016  Added '-u' option to utils/viewer.py to show what payload you used in a given project

28-07-2016  Fixed max columns width when printing output

19-07-2016  Fixed a bug in DBManager queue which was stopping Cansina when target server responses were slow

13-07-2016  Added new feature resumable sessions

09-01-2016  Cansina supports Windows terminal
            You won't have that fancy flash in filtered HTTP codes but it works...    


Cansina
=======

[![Build Status](https://travis-ci.org/deibit/cansina.svg?branch=master)](https://travis-ci.org/deibit/cansina)

Cansina is a Web Content Discovery Application.

It is well known Web applications don't publish all their resources or public links, 
so the only way to discover these resources is requesting for them and check the response.

Cansina duty is to help you making requests and filtering the responses to tell 
apart if it is an existing resource or just an annoying or disguised 404.

Other kind of useful responses (401, 403, ...) are processed in a similar fashion.

Responses are kept in a sqlite database for later process or viewing.

You can stop and resume a task by ctrl-c, a resume file will be generated for you.

Check the options '-h' for more features.

There is an ongoing effort to add features via plugins.

Feature requests and comments are welcome.

Cansina is included in [BlackArch Linux](https://www.blackarch.org/), give it a try! 

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
- Resume

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

**Resume session**

*cansina.py -r resume_file*

Resume last interrupted session with all options and payload with former linenumber

**Parse robots.txt**

*cansina.py -R*

Cansina will parse the robots.txt file an use it as a payload if it exists


Important
---------

This tool is intended to be used in a fair and legal context, meaning, for example,
a penetration testing for which you have been provided previous authorization.

One of its legitimate uses might be the one described in the following article:

- [Forced browsing](https://www.owasp.org/index.php/Forced_browsing) 


Dependencies
------------

- [requests](https://github.com/kennethreitz/requests)
- Python 2.7.x 

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
