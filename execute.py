import pycentreon.core.api
import os
from pprint import pprint

if __name__ == "__main__":

    os.environ['REQUESTS_CA_BUNDLE'] = "lc.pem"

    centreon_url = "https://infdcxctn01prd.ad-conservateur.fr/centreon"
    username = "admin"
    password = "416mETLPmP,i0rYVWnkc?tX5U"
    token = 'pfW31bFm+/AK8F03L9tTFA/ruQVvYpUGuyCFCUW+NauQW5sd+h2lRxvKc9grHUtm'

    ctn = pycentreon.api(centreon_url)
    token = ctn.create_token(username, password)
    print(token)