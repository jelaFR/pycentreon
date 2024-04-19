import pycentreon.core.api

if __name__ == "__main__":

    centreon_url = "https://infdcxctn01prd.ad-conservateur.fr/centreon"
    centreon_version = "23.10"
    username = "admin"
    password = "416mETLPmP,i0rYVWnkc?tX5U"
    token = 'pfW31bFm+/AK8F03L9tTFA/ruQVvYpUGuyCFCUW+NauQW5sd+h2lRxvKc9grHUtm'

    ctn = pycentreon.api(centreon_url, token=token)
    pass