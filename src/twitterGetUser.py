import requests
import json
import os
from dotenv import load_dotenv
from requests_oauthlib.oauth2_auth import OAuth2

load_dotenv()
bearer_token = os.environ.get("TWITTER_BEARER_TOKEN")


def create_url():
    usernames = "usernames=benshapiro"
    user_fields = "user.fields=description,created_at"
    url = "https://api.twitter.com/2/users/by?{}&{}".format(
        usernames, user_fields)
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


def main():
    url = create_url()
    json_response = connect_to_endpoint(url)
    print(json.dumps(json_response, indent=4, sort_keys=True))


if __name__ == "__main__":
    main()
