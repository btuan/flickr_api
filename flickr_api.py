#!/usr/bin/env python3
""" flickr_api.py

Quick hack to download files from Flickr undownloadable set.

TODO:
    > Generalize page numbers.
    > Load entire page with request.
    > Refactor hackscript into CLI with click.
"""

import errno
import os
import re
import requests
from lxml import html
from random import random
from time import sleep

import colorama as c
c.init()

# CONFIGURATION SECTION
url = ''
output_dir = 'photos/'
random_delay_scale_factor = 0.5
pages = 6
# END CONFIGURATION SECTION

try:
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise e

page = requests.get(url=url)
assert(page.status_code == 200)

tree = html.fromstring(page.content)
photo_divs = tree.xpath('//div[@style]')

url_match = re.compile(r'//.+\)')
urls = ['https:' + url_match.search(el.get('style')).group()[:-1]
        for el in photo_divs if 'style' in el.keys() and 'url' in el.get('style')]

# Some API wizardry. For some reason, <photo>_c.jpg works best
photo_url_match = re.compile(r'_.\.jpg')
for ind, url in enumerate(urls):
    match = photo_url_match.search(url)
    if match:
        urls[ind] = url[:-6] + '_c.jpg'
    else:
        urls[ind] = url[:-4] + '_c.jpg'

    r = requests.get(urls[ind])
    img_name = urls[ind][url.rfind('/'):-6] + '.jpg'
    if r.status_code == 200:
        with open(output_dir + img_name, 'wb') as f:
            f.write(r.content)
        print(c.Fore.GREEN + 'WRITTEN: ' + c.Style.RESET_ALL + img_name)
    else:
        print(c.Fore.RED + 'FAILED:  ' + c.Style.RESET_ALL + img_name)

    sleep(random() * random_delay_scale_factor)

print('\nDone.')

