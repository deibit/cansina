import random
import urllib
import hashlib
import difflib

class Inspector:

    TEST404_OK = 0
    TEST404_MD5 = 1
    TEST404_STRING = 2
    TEST404_URL = 3
    TEST404_NONE = 4

    def __init__(self, target):
        self.target = target

    def _give_it_a_try(self)
        s = []
        for n in range(0,42):
            random.seed()
            s.append(chr(random.randrange(97, 122)))
        s = "".join(s)
        target = self.target + s
        page = urllib.urlopen(target)
        content = page.readlines()
        result = {'code':str(page.code),
                  'size':len(content),
                  'md5':hashlib.md5("".join(content)).hexdigest()
                  'content':content}
        return result

    def _diff_test(self, a, b):
        return difflib.unified_diff(a,b)

    def _fire_a_404(self, target):
        first_result = self._give_it_a_try()
        if first_result['code'] == '404':
            # Ok, resquest gave a 404 so we shouldn't find problems
            return ('', Inspector.TEST404_OK)
        if first_result['code'] == '200':
            # Mmm, we were given a 200, possible fake 404
            # Trying one more time
            second_result = self._give_it_a_try()
            if second_result['code'] == '200' and first_result['md5'] == second_result['md5']:
                # Ok, the fake 200 page seems stable so we are going to spot it by md5
                return (first_result['md5'], Inspector.TEST404_MD5)
                # Well, neither is a 200 code nor is the same result so we back to diff mode
            else:
                second_content = result['content']
                diff = self._diff_test(first_result['content'], second_content['content'])
                for n in diff:
                    print n
                print("These are the diff of two request, please provide a string for detecting 404: ")
                s = raw_input()
                return (s, Inspector.TEST404_STRING)
        # Test for 302 redirection
        if first_result['code'] == '302':
            location = ""
            try:
                location = first_result.headers['location']
            except:
                return (location, Inspector.TEST404_URL)
        # We give up here :(
        return ('', Inspector.TEST404_NONE)
