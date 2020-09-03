import tweepy
from twitterCreds import *
import json
import pprint
from datetime import datetime

class TrumpStreamListener(tweepy.StreamListener):

    def __init__(self, api, id):
        self.api = api
        self.id = id
        self.TWEET_LENGTH = 280
        self.SIGNATURE = "- The Governator"

    def reformat_text(self, text):
        if (len(text) < 280 - len(self.SIGNATURE)):
            return text + "\n" + self.SIGNATURE

    def is_mention(self, status):
        return status["user"]["id_str"] != str(self.id)

    def is_reply(self, status):
        return status["in_reply_to_status_id"] != None

    def is_retweet(self, status):
        return "retweeted_status" in status

    def is_quoted(self, status):
        return "quoted_status" in status

    def on_status(self, status):
        status = status._json
        pprint.pprint(status)
        if self.is_mention(status) or self.is_reply(status) or self.is_retweet(status):
            return

        new_text = ""
        if status["truncated"]:
            new_text = self.reformat_text(status["extended_tweet"]["full_text"])
        else:
            new_text = self.reformat_text(status["text"])

        if self.is_quoted(status):
            tweet_url_base = "https://twitter.com"
            quoted_status = status["quoted_status"]
            new_text += " " + tweet_url_base + "/" + quoted_status["user"]["name"] + "/status/" + quoted_status["id_str"]

        self.api.update_status(status = new_text)
        
    def on_error(self, status):
        # Returning False on_data method in case rate limit occurs.
        if status == 420:
            return False
        print(status)

def authenticate():
    auth = tweepy.OAuthHandler(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    auth.set_access_token(CONSUMER_KEY, CONSUMER_SECRET)

    return tweepy.API(auth)

def main():

    api = authenticate()
    user = api.get_user("Schwarzenegger")
    user_id = user.id

    stream_listener = TrumpStreamListener(api, user_id)
    stream = tweepy.Stream(auth = api.auth, listener = stream_listener)
    while True:
        try:
            stream.filter(follow=[str(user_id)])
        except Exception as e:
            with open("log.txt", "a") as file:
                now = datetime.now()
                file.write(str(now.strftime("%m/%d/%Y %H:%M:%S")) + " - " + e)
            continue

main()
