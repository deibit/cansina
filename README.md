# Cansina

[![Build Status](https://travis-ci.org/deibit/cansina.svg?branch=master)](https://travis-ci.org/deibit/cansina)

Cansina is a Web Content Discovery Application.

It is well known Web applications don't publish all their resources or public links,
so the only way to discover these resources is requesting for them and check the response.

Cansina duty is to help you making requests and filtering and inspecting the responses to tell
apart if it is an existing resource or just an annoying or disguised 404.

Feature requests and comments are welcome.

Cansina is included in [BlackArch Linux](https://www.blackarch.org/), give it a try!

![CansinaImage](https://github.com/deibit/cansina/raw/gh-pages/images/cansina-showcase.png "Image")

## Installation

```
pip install cansina
```

If you don't want to pollute your environment to try cansina just create a virtual env

## Usage

[Wiki](https://github.com/deibit/cansina/wiki) is full of documentation and examples. But as a fast example:

```
cansina -u <site_url> -p <payload_file>
```

Help summary:

```
cansina.py -h
```

## Features

- Data persistence with sqlite database
- Optional output in CSV format
- Multithreading
- Multiextension
- Custom headers
- Multiple wordlists from directories
- Content detection
- Filter results by size
- Filter results by content
- URL pattern (\*\*\*) to interpolate strings
- SSL support
- Proxy support
- Basic Authentication
- Cookie jar
- Resuming
- Path recursion
- Persistent connections
- Complementary tools

## Speed

Wanna make Cansina run faster? Grab my cup of coffee.

Cansina downloads page content for inspection by default (Yep, Cansina does not racing for speed). but you can disable GET requests and make them HEAD (no body page download). Also, do no print the fancy terminal interface (you will lost some hackish points).

- Put **-H** to make requests lighter
- Put **--no-progress** to print no fancy information in the screen
- Raise default threads to ten with **-t 10** (or even more if you don't mind noise and faulty tries)

## Integrated tree viewer

Cansina integrates a tree viewer (thanks to asciitree package) to output a project sqlite base stored results (http 200 status code by now).

```
cansina -V output/http_testphp.vulnweb.com.sqlite
```

![ViewerImage](https://github.com/deibit/cansina/raw/gh-pages/images/viewer.png "Image")

## Important

This tool is intended to be used in a fair and legal context, meaning, for example,
a penetration testing for which you have been provided previous authorization.

One of its legitimate uses might be the one described in the following article:

- [Forced browsing](https://www.owasp.org/index.php/Forced_browsing)

## Dependencies

- [requests](https://github.com/kennethreitz/requests)
- [asciitree](https://github.com/mbr/asciitree)

## Windows

Untested in Windows. It should work with **--no-progress**

## Wordlists

- [SecList](https://github.com/danielmiessler/SecLists)

## License information

License: GNU General Public License, version 3 or later; see LICENSE.txt
included in this archive for details.
