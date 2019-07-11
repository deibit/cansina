Cansina
=======

**IMPORTANT**: Clone this repository with:

```
    git clone --depth=1 https://github.com/deibit/cansina
```

---

[![Build Status](https://travis-ci.org/deibit/cansina.svg?branch=master)](https://travis-ci.org/deibit/cansina)

Cansina is a Web Content Discovery Application.

It is well known Web applications don't publish all their resources or public links,
so the only way to discover these resources is requesting for them and check the response.

Cansina duty is to help you making requests and filtering and inspecting the responses to tell
apart if it is an existing resource or just an annoying or disguised 404.

Feature requests and comments are welcome.

Cansina is included in [BlackArch Linux](https://www.blackarch.org/), give it a try!

Options
-------

```usage: cansina.py -u url -p payload [options]

Cansina is a web content discovery tool. It makes requests and analyze the
responses trying to figure out whether the resource is or not accessible.

optional arguments:
  -h, --help            show this help message and exit
  -A AUTHENTICATION     Basic Authentication (e.g: user:password)
  -C COOKIES            your cookies (e.g: key:value)
  -D                    Check for fake 404 (warning: machine decision)
  -H                    Make HTTP HEAD requests
  -P PROXIES            Set a http and/or https proxy (ex:
                        http://127.0.0.1:8080,https://...
  -S                    Remove ending slash for payloads
  -T REQUEST_DELAY      Time (a float number, e.g: 0.25 or 1.75) between
                        requests
  -U                    Make payload requests upper-case
  -a USER_AGENT         The preferred user-agent (default provided)
  -b BANNED             List of banned response codes
  -B UNBANNED           List of unbanned response codes, mark all response as
                        invalid without unbanned response codes, higher
                        priority than banned
  -c CONTENT            Inspect content looking for a particular string
  -d DISCRIMINATOR      If this string if found it will be treated as a 404
  -e EXTENSION          Extension list to use e.g: php,asp,...(default none)
  -p PAYLOAD            A single file, a file with filenames (.payload) or a
                        directory (will do *.txt)
  -s SIZE_DISCRIMINATOR
                        Will skip pages with this size in bytes (or a list of
                        sizes 0,500,1500...)
  -t THREADS            Number of threads (default 4)
  -u TARGET             Target url
  -r RESUME             Resume a session
  -R                    Parse robots.txt and check its contents
  --recursive           Recursive descend on path directories
  --persist             Use HTTP persistent connections
  --full-path           Show full path instead of only resources
  --show-type           Show content-type in results
  --no-follow           Do not follow redirections
  --line CONTINUE_LINE  Continue payload in line <n>
  --headers HEADERS     Set personalized headers: key=value;key=value...
  --capitalize          Transform 'word' into 'Word'.
  --strip-extension     Strip word extension: word.ext into word
  --alpha               Filter non alphanumeric words from wordlist
  --no-progress         Don't show tested words and progress. (For dumb terminals)
  --no-colors           Don't use output colors to keep output clean, e.g. when redirecting output to file

License, requests, etc: https://github.com/deibit/cansina
```


Screenshot
----------

![CansinaImage](https://github.com/deibit/cansina/raw/gh-pages/images/cansina-showcase.png "Image")


Installing dependencies
=======================

pip install --user requests[security] or pip install -r requirements.txt

(try removing --user and install with sudo in case of errors)

git clone --depth=1 https://github.com/deibit/cansina


Fast use
========

$ python3 cansina.py -u <site_url> -p <payload_file> --persist

Cansina is Python 2 compatible but 3 is more than advisable.

--persist is optional but it speedup the process. Also the noise.


Features
--------

- Multithreading
- Multiextension
- Custom headers
- Multiple wordlists from directories
- Content detection
- Filter results by size
- Filter results by content
- URL pattern (***) to interpolate strings
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
- Python 3 (also Python 2 is supported)


Wordlists
---------

Cansina does not come with list but there are some awesome projects to supply this:

- [SecList](https://github.com/danielmiessler/SecLists)
- [fuzzdb](https://code.google.com/p/fuzzdb/)


License information
-------------------

Copyright (C) 2013-2019 David García [@dgn1729](https://twitter.com/dgn1729)

License: GNU General Public License, version 3 or later; see LICENSE.txt
         included in this archive for details.
