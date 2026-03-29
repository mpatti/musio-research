import requests_oauthlib
import requests
from requests_oauthlib import OAuth1
import sys

CK = "f5UzmEp6J4WxUthsG2fIHaeKy"
CS = "pRVCVLaiGwmUjgR8IW3CL4bNp7BAI4FtkjNEgV9flxc3dqtvK6"
AT = "15847656-27kiwhcq5ms2Qqy2XVKR4UefVpnrSqObZqXno0cLw"
AS = "Xb38cb8ds2o6KgMl7gLdgDvGpFUPYSTDfRJmWKZa7Ch5u"

auth = OAuth1(CK, CS, AT, AS)
session = requests.Session()
session.auth = auth

# Test: get user info
r = session.get("https://api.twitter.com/1.1/account/verify_credentials.json")
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"User: @{data.get('screen_name')}")
    print(f"Name: {data.get('name')}")
else:
    print(f"Error: {r.text}")

# Search tweets
r2 = session.get("https://api.twitter.com/1.1/search/tweets.json", params={"q": "music industry", "count": 5})
print(f"\nSearch status: {r2.status_code}")
if r2.status_code == 200:
    tweets = r2.json().get("statuses", [])
    for t in tweets:
        print(f"- @{t.get('user',{}).get('screen_name')}: {t.get('text','')[:80]}")
