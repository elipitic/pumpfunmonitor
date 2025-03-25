import requests
import re

pattern = re.compile(u'https://x.com/([a-zA-Z0-9_]+)')

def find_twitter(toekn_address):

    response = requests.get("https://pump.fun/coin/{}".format(toekn_address))
    if response.status_code == 200:
        return pattern.search(response.text).group(0)