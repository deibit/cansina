# -*- coding: utf-8 -*-

import sys
import urlparse
import threading

try:
    import requests
    from BeautifulSoup import BeautifulSoup
except:
    print("[CRAWLER] Oops, check your dependencies are installed")
    print("[CRAWLER] pip install requests bs4")


USER_AGENT = "Mozilla/5.0 (Windows; U; MSIE 10.0; Windows NT 9.0; en-EN)"
user_agent = {"user-agent": USER_AGENT}
DESIRABLE_EXTENSIONS = ['.html', '.htm', '.inc', '.php', '.asp', '.aspx', '.txt']

_non_visited_links = list()
_visited_links = list()
_loot = dict()


def visit(scheme, domain, resource):
    '''
        Visit 'url' with designated 'user_agent'
        return a 'resources' list with unique elements
    '''
    global _non_visited_links
    temporal_resource_list = list()

    if resource.startswith('/'):
        url = "%s://%s%s" % (scheme, domain, resource)
    else:
        url = "%s://%s/%s" % (scheme, domain, resource)

    print("visiting: url: %s" % url)
    request = requests.get(url, headers=user_agent)
    soup = BeautifulSoup(request.text)
    resources = {
        'anchor': (soup.find_all('a'), 'href'),
        'iframe': (soup.find_all('iframe'), 'src'),
        'frame': (soup.find_all('frame'), 'src'),
        'img': (soup.find_all('img'), 'src'),
        'link': (soup.find_all('link'), 'href'),
        'script': (soup.find_all('script'), 'src'),
        'form': (soup.find_all('form'), 'action'),
        }

    for res in resources.values():
        tags, attr = res
        for tag in tags:
            if tag.has_attr(attr):
                temporal_resource_list.append(tag[attr])

    if resource.startswith('/'):
        resource = resource[1:]

    _visited_links.append(resource)
    _non_visited_links.extend(resource_filter(domain, temporal_resource_list))


def resource_filter(domain, resource_set):
    my_non_visited_links = []
    for resource in resource_set:
        p_resource = urlparse.urlparse(resource).path
        p_domain = urlparse.urlparse(resource).netloc
        if p_resource.startswith('/'):
            p_resource = p_resource[1:]
        if p_domain and not p_domain == domain:
            continue
        if p_resource not in _visited_links and p_resource not in _non_visited_links:
            if is_interesting(p_resource):
                my_non_visited_links.append(p_resource)
    return list(set(my_non_visited_links))


def is_interesting(resource):
    '''
        Filter a resource container with non-desired resources
    '''
    if resource == '/' or resource == '':
        return False

    # Remove #resouces or javascript functions
    banned_set = set(['(', ')', '#'])
    check_set = set(resource)
    if any(banned_set & check_set):
        return False

    # Keep only desirable directories and files
    last_path_component = urlparse.urlparse(resource).path.split('/')[-1]
    if '.' not in last_path_component:
        return True
    else:
        for extension in DESIRABLE_EXTENSIONS:
            if extension in last_path_component:
                return True
    return False


def recursive_dict_key_finder(key, dictionary):
    if key in dictionary:
        dictionary = dictionary[key]
        return recursive_dict_key_finder(key, dictionary)
    else:
        dictionary[key] = {}
        return dictionary


def get_into_loot(resource):
    '''
        Take a list of resources, break them into pieces to extract directories
        and files
    '''
    pieces = resource.split('/')
    for piece in pieces:
        recursive_dict_key_finder(piece, _loot)


def check_for_302(url):
    req = requests.get(url)
    if req.status_code in ['301', '302']:
        print("[CRAWLER] Crawling relocation instead -> %s" % req.history[0].url)
        return req.history[0].url
    else:
        return url


if __name__ == '__main__':
    url = check_for_302(sys.argv[1])
    components = urlparse.urlparse(url)
    if not components.path:
        _non_visited_links.append('/')
    else:
        _non_visited_links.append(components.path)
    while len(_non_visited_links) > 0:
        try:
            current_resource = _non_visited_links.pop()
            visit(scheme=components.scheme, domain=components.netloc, resource=current_resource)
        except KeyboardInterrupt:
            print("Was visiting %s://%s%s" % (components.scheme, components.netloc, current_resource))
    print(_visited_links)
