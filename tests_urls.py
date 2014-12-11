
from unittest import TestCase
import requests

resp_template = 'args:<ul> %s </ul>\n'

def make_resp_exemplar(args_array):
    args_str = " ".join(["<li>%s</li>" % arg for arg in sorted(args_array)])
    resp = resp_template % args_str
    return resp

urls = {
    'http://poresopropongo.mx/card':         ['type card'],
    'http://poresopropongo.mx/card/804':     ['type card',
                                              'offset 804'],
    'http://poresopropongo.mx/300/993':      ['type view',
                                              'offset 300',
                                              'num_images 993'],
    'http://poresopropongo.mx/300':          ['type view',
                                              'offset 300'],
}

class TestUrls(TestCase):
    def test_urls(self):
        for url, expected_resp in urls.items():
            r = requests.get(url)
            self.assertEqual(r.text, make_resp_exemplar(expected_resp), url)

