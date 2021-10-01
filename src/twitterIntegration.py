import requests
import json
import os
from dotenv import load_dotenv
from requests_oauthlib.oauth2_auth import OAuth2
import re

load_dotenv()
bearer_token = os.environ.get("TWITTER_BEARER_TOKEN")


def lookup(screenName):
    url = "https://api.twitter.com/1.1/users/lookup.json?screen_name={}".format(
        screenName)
    response = connect_to_endpoint(url)

    return response[0]['id']


def create_url(screenName):
    print(screenName)
    user_fields = "tweet.fields=id,text,conversation_id,created_at,entities&media.fields=url&exclude=retweets,replies"

    url = "https://api.twitter.com/2/users/{}/tweets?{}".format(
        screenName, user_fields)

    print("\nURL: {}\n".format(url))
    return url


def bearer_oath(r):
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2UserLookupPython"
    return r


def connect_to_endpoint(url):
    response = requests.request("GET", url, auth=bearer_oath)
    print(f"\nRESPONSE STATUS CODE: {response.status_code}\n")
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )
    return response.json()


def findURL(string):

    # findall() has been used
    # with valid conditions for urls in string
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
    url = re.findall(regex, string)
    return [x[0] for x in url]


def main(arg):
    try:
        user = lookup(arg)
        url = create_url(user)
        json_response = connect_to_endpoint(url)
        print(json.dumps(json_response, indent=4, sort_keys=True))

        raw = json_response['data']
        print(raw[0]['id'])

        return raw[0]['id']
    except:
        return json_response


if __name__ == "__main__":
    main()
