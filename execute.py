import pycentreon.core.api
import os
from pprint import pprint

if __name__ == "__main__":

    os.environ['REQUESTS_CA_BUNDLE'] = "lc.pem"

    centreon_url = "https://infdcxctn01prd.ad-conservateur.fr/centreon"
    username = "admin"
    password = "416mETLPmP,i0rYVWnkc?tX5U"
    token = 'omr/vRiiVfh9A2QvQcEV23CmOW1KV/+p/6h1pfd4ArwyBmEeCI+8buuGbK24FeEa'

    ctn = pycentreon.api(centreon_url, token)
    #ctn.login(username, password)
    hosts = ctn.configuration.hosts.all()
    pass