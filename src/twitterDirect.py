import requests
import json
import os
from dotenv import load_dotenv
from requests_oauthlib.oauth2_auth import OAuth2
import csv
import re

load_dotenv()
bearer_token = os.environ.get("TWITTER_BEARER_TOKEN")


def create_url(nextToken=None):
    usernames = "17995040"

    if nextToken is None:
        user_fields = "tweet.fields=id,text,conversation_id,created_at&media.fields=url&max_results=100&exclude=retweets"
    else:
        user_fields = f"tweet.fields=text,created_at&media.fields=url&max_results=100&pagination_token={nextToken}"

    url = "https://api.twitter.com/2/users/{}/tweets?{}".format(
        usernames, user_fields)
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


def main():
    url = create_url()
    json_response = connect_to_endpoint(url)
    print(json.dumps(json_response, indent=4, sort_keys=True))

    shapiroTweets = []
    raw = json_response['data']
    # print(raw)
    # for item in raw:
    #     # print(f'==================\n{item}\n')
    #     if item['text'][:2] == "RT":
    #         continue
    #     else:
    #         tweetID = item['id']
    #         stripper = findURL(item['text'])
    #         print("+++++++")
    #         print(stripper)
    #         print(len(stripper))
    #     tweetionary = {'id': item['id'], 'text': item['text'], ''}

    # with open('shapiro-tweets.csv', newline='') as csvfile:
    #   fieldnames = ['id', 'text', 'url', 'created_at']
    #   writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    #   writer.writeheader()


if __name__ == "__main__":
    main()
