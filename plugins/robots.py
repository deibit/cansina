import requests
import sys

def process_robots(target):
    '''
        Return a list of entries if robots.txt is found and has meat otherwise
        return None
    '''
    interesting_entries = []
    try:
        result = requests.get(target + "robots.txt")
        if not result.status_code == 200:
            return
        for line in result.text.splitlines():
            if line.startswith("Disallow:") or line.startswith("Allow:"):
                if len(line.split(":")) > 1:
                    interesting_entries.append(line.split(":")[1])
        return list(set(interesting_entries))
    except Exception as e:
        sys.stderr.write("[robots] Error getting robots.txt")
        sys.stderr.write(e)
        return None
