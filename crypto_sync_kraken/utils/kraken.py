import base64
import hashlib
import hmac
import logging
import time
import urllib.parse

import requests

_logger = logging.getLogger(__name__)


def get_kraken_signature(urlpath, data, secret):
    # Source: https://docs.kraken.com/rest/#python
    postdata = urllib.parse.urlencode(data)
    encoded = (str(data["nonce"]) + postdata).encode()
    message = urlpath.encode() + hashlib.sha256(encoded).digest()

    mac = hmac.new(base64.b64decode(secret), message, hashlib.sha512)
    sigdigest = base64.b64encode(mac.digest())
    return sigdigest.decode()


def kraken_request(uri_path, data, api_key, api_sec):
    url = "https://api.kraken.com" + uri_path
    data["nonce"] = str(int(1000 * time.time()))
    headers = {
        "API-Key": api_key,
        "API-Sign": get_kraken_signature(uri_path, data, api_sec),
    }
    _logger.info("POST " + url)
    return requests.post(url, headers=headers, data=data)
