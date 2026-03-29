#!/usr/bin/env python3
"""Twitter search script using OAuth 1.0a"""
from requests_oauthlib import OAuth1
import requests
import sys
import json

CK = "f5UzmEp6J4WxUthsG2fIHaeKy"
CS = "pRVCVLaiGwmUjgR8IW3CL4bNp7BAI4FtkjNEgV9flxc3dqtvK6"
AT = "15847656-27kiwhcq5ms2Qqy2XVKR4UefVpnrSqObZqXno0cLw"
AS = "Xb38cb8ds2o6KgMl7gLdgDvGpFUPYSTDfRJmWKZa7Ch5u"

def twitter_search(query, max_results=10):
    auth = OAuth1(CK, CS, AT, AS)
    r = requests.get(
        "https://api.twitter.com/2/tweets/search/recent",
        params={"query": query, "max_results": min(max_results, 100)},
        auth=auth
    )
    if r.status_code != 200:
        return {"error": r.text, "status": r.status_code}
    data = r.json()
    return data

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "music industry"
    results = twitter_search(query)
    if "error" in results:
        print(f"Error: {results}")
    else:
        for t in results.get("data", []):
            print(f"• {t.get('text','')[:120]}")
