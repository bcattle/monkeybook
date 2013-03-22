#!/usr/bin/env python
import sys
from short_url import UrlEncoder

BLOCK_SIZE = 24
MIN_LENGTH = 2

print 'Testing block size %d' % BLOCK_SIZE

url_encoder = UrlEncoder(block_size=BLOCK_SIZE)

urls = set()
for n in xrange(0,3000000):
    url = url_encoder.encode_url(n, min_length=2)
    if url in urls:
        print 'BREAK: duplicate url found at n=%d' % n
        break
    else:
        urls.add(url)
        sys.stdout.write('%d: %s\t' % (n, url))
        sys.stdout.flush()
