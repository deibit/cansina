Changelog
=========

20-06-2018  Added new option --capitalize to transform words into Words

17-06-2018  Added new option --headers to allow you to insert your own headers

29-11-2017  Added new option. --line <n> will continue you task on line <n>

15-09-2017  Payloads can be now a single file, a directory or a file containing references to other files

14-09-2017  New console interface and new option 'show-type' to reflect 'Content-Type' in output

11-09-2017  Added a new option 'full-path' for show the entire path in console

07-09-2017  Added an 'eta' clock

06-09-2017  Viewer (from utils/viewer.py) received some love. A tree struct view and a
            couple of filters. Give it a try (utils/viewer.py -h)

03-09-2017  Added persistent connections (--persist). You will definitely want this.

31-08-2017  Added recursive (--recursive) feature

31-08-2017  Support for Python 3 has been tested and seems stable

22-08-2017  Cookie support. With option -C you can now provide a set of cookie like "JSESSIONID:blablabla,admin=1"

14-08-2017  Size filtering. Now can be a list of sizes you want to ignore

13-03-2017  New option: -R autoscan robots.txt and use it as a payload

26-01-2017  Fixed 'InsecureRequestsWarning' message

10-08-2016  Added '-u' option to utils/viewer.py to show what payload you used in a given project

28-07-2016  Fixed max columns width when printing output

19-07-2016  Fixed a bug in DBManager queue which was stopping Cansina when target server responses were slow

13-07-2016  Added new feature resumable sessions

09-01-2016  Cansina supports Windows terminal
            You won't have that fancy flash in filtered HTTP codes but it works...


License information
-------------------

Copyright (C) 2013-2017 David García

License: GNU General Public License, version 3 or later; see LICENSE.txt
         included in this archive for details.
