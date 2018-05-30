import sys
from BeautifulSoup import BeautifulSoup as bs

try:
    import urlparse
except:
    import urllib.parse as urlparse

def get_links(page):
    soup = bs(page)
    links = []

    links_from_a = soup.findAll('a')
    for tag in links_from_a:
        links.append(tag.get('href', None))
    return set(links)

def purify(links):
    purified = []
    for link in links:
        if link.startswith('//'):
            link = link[1:]

if __name__ == '__main__':
    with open(sys.argv[1]) as f:
        for i in get_links(f.read()):
            if i and urlparse.urlparse(i).path and not urlparse.urlparse(i).netloc:
                print urlparse.urlparse(i).path

