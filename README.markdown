# pyPerspectives #

pyPerspectives is a Python client for
[Perspectives](http://perspectives-project.org/).

## Installation ##

python setup.py install

## Script Usage ##

pyPerspectives comes with the script `notary-query.py` which can be
used to get raw notary responses.

~~~
$ notary-query.py -N http_notary_list.txt encrypted.google.com
Notary Response Version: 1 Signature type: rsa-md5
	Sig: ANpjvbPxecP6N+3+PgCJNq+WO4VOdYC6tZttASF2CAbbn4twjeeizHZlx221AZvaqMQbeboN5tkH8+ZN5NRC+aRHgBXlkr6HcDASc8QxGHXfTev5LuCEu9Xl7oF4VgwP5vdKsMAoP7r/bvta4hulxljxLnv31Yg33AvLYpDySzucXaLgOW5bEwoJozmQ+A+mEol7UtCwlxje88Kjj2TGy71m6vvapr58y+ZgSA==
...and so forth...
~~~

Run `notary-query.py -h` for a full set of options.

## API Usage ##

~~~
>>> import Perspectives
>>> notaries = Perspectives.Notaries.from_file("http_notary_list.txt")
>>> from Perspectives import Service
>>> s = Service("encrypted.google.com", 443)
>>> responses = notaries.query(s)
>>> for response in responses:
...     print response
Notary Response Version: 1 Signature type: rsa-md5
       Sig: ANpjvbPxecP6N+3+PgCJNq+WO4VOdYC6tZttASF2CAbbn4twjeeizHZlx221AZvaqMQbeboN5tkH8+ZN5NRC+aRHgBXlkr6HcDASc8QxGHXfTev5LuCEu9Xl7oF4VgwP5vdKsMAoP7r/bvta4hulxljxLnv31Yg33AvLYpDySzucXaLgOW5bEwoJozmQ+A+mEol7UtCwlxje88Kjj2TGy71m6vvapr58y+ZgSA==
Fingerprint: 3d:76:a1:94:c6:d3:c1:78:39:ab:a1:58:7c:f9:61:95 type: 2
Thu Jun 16 03:25:56 2011 - Wed Jul  6 16:05:46 2011
... and so forth ...
>>> response = responses[0]
>>> print response.last_key_seen()
Fingerprint: 3d:76:a1:94:c6:d3:c1:78:39:ab:a1:58:7c:f9:61:95 type: 2
Thu Jun 16 03:25:56 2011 - Wed Jul  6 16:05:46 2011
>>> print response.key_change_times()
[1309982746, 1308209156, 1305746492, 1306221594, 1304666319, 1306135184, 1306135183, 1307431699, 1305746493, 1306221595, 1300260961, 1295888489, 1308209155, 1307431700, 1304666318, 1300260962]
~~~
