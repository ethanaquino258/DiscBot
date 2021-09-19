from dotenv import load_dotenv
import os
from requests_oauthlib.oauth2_auth import OAuth2
import twitter
from twitter import *

load_dotenv()

apiKey = os.getenv('TWITTER_KEY')
secretKey = os.getenv('TWITTER_SECRET_KEY')
accessToken = os.getenv('TWITTER_ACCESS_TOKEN')
secretToken = os.getenv('TWITTER_SECRET_TOKEN')

# api = twitter(Auth=OAuth2(apiKey, secretKey, accessToken, secretToken))

tweeter = twitter.Api(consumer_key=apiKey, consumer_secret=secretKey,
                      access_token_key=accessToken, access_token_secret=secretToken)

# results = tweeter.GetUser(user_id='17995040')

# results = tweeter.GetUsersSearch(term='tuktukbuck')

results = tweeter.GetUserTimeline(
    user_id='17995040', screen_name='benshapiro', include_rts=False, trim_user=True)

print(results[0].text)

# results = tweeter.GetUserTimeline(
#     user_id='1413888654209163269', count=22, include_rts=True, trim_user=True)
# results = tweeter.GetUser(user_id='1413888654209163269')

# print(results)

# results = tweeter.GetUserTimeline

# print(results)

# for item in results:
#     print("==========================\n")
#     print(item)

# print(len(results))
