import tweepy
from credentials import *
from config import *
import json
import time
import re
import sqlalchemy as db

"""Module for simplified Twitter data collection to test visualization front-end."""


#basic text cleaning for the tweet text
def clean_tweet(tweet):
    tweet = re.sub(r'\S+\.\S+\/\S+', "", tweet) #remove links
    tweet = re.sub(r'@([A-Za-z0-9]+)', r'\1', tweet) #replace @username with username
    while "#" in tweet:
        tweet = re.sub(r'#(.+)', r'\1', tweet) #replace "#hashtag" with "hashtag"
    tweet = re.sub(r'\s(rt)|(RT)', '', tweet) #remove RT indicating retweet
    tweet = tweet.replace("\n", " ") # remove \n characters
    tweet = re.sub(r'[^\u0000-\u0080]', "", tweet) #remove non-ascii utf8 chars
    html_issues = {"&amp" : "and",
                   "&gt" : ">",
                   "&lt" : "<",
                  }
    for prob, sol in html_issues.items():
        tweet = tweet.replace(prob, sol)
    tweet = tweet.lower()
    return tweet

def create_tables(conn, metadata, engine):
    try:
        tweets = db.Table('tweets', metadata,
            #note the Id not ID here, different from retweet table
            db.Column('tweetId', db.String(100), primary_key=True),
            db.Column('user', db.String(100)),
            db.Column('text', db.String(1000)),
            db.Column('time', db.DateTime)
        )
        retweets = db.Table('retweets', metadata,
            db.Column('rt_tweetID', db.String(100), primary_key=True),
            db.Column('user_author', db.String(100)),
            db.Column('user_retweeted_by', db.String(100), primary_key=True),
            db.Column('rt_text', db.String(1000)),
            db.Column('rt_time', db.DateTime)
        )
        ngrams = db.Table('ngrams', metadata,
            #db.Column()
            #finish this
        )
        metadata.create_all(engine)
    except Exception as e:
        print(str(e))

def get_tweet_fulltext(tweet):
    try:
        return tweet.extended_tweet['full_text']
    except Exception as e:
        return tweet.text

class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        try:
            tweets_t = db.Table('tweets', metadata, autoload=True, autoload_with=engine)
            retweets_t = db.Table('retweets', metadata, autoload=True, autoload_with=engine)
            if hasattr(status, 'retweeted_status'):
                rt_tweetID = status.retweeted_status.id_str
                user_author = status.retweeted_status.user.screen_name
                user_retweeted_by = status.user.screen_name 
                rt_text = clean_tweet(get_tweet_fulltext(status.retweeted_status))
                rt_time = status.retweeted_status.created_at 
                #commit to db
                rt_ins = retweets_t.insert().values(rt_tweetID = rt_tweetID, user_author = user_author, user_retweeted_by = user_retweeted_by, rt_text = rt_text, rt_time = rt_time)
                conn.execute(rt_ins)
            else:
                tweetID = status.id_str
                user = status.user.screen_name
                text = clean_tweet(get_tweet_fulltext(status))
                time = status.created_at
                #commit to db
                ins = tweets_t.insert().values(tweetId = tweetID, user = user, text = text, time = time)
                conn.execute(ins)
        except KeyError as e:
            print(str(e))
        return True
    def on_error(self, status_code):
        print(status_code)
        if status_code == 420:
            #disconnect stream to prevent rate-limiting issues
            return False 

if __name__ == "__main__":

    #mySQL setup via SqlAlchemy
    engine = db.create_engine(f'mysql+mysqldb://{user}:{pw}@{host}/trailtweets?charset=utf8mb4', encoding='utf-8')
    conn = engine.connect()
    metadata = db.MetaData()

    create_tables(conn, metadata, engine)

    while True:
        try:
            auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
            auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
            api = tweepy.API(auth)
            streamlistener = MyStreamListener()
            tweetStream = tweepy.Stream(auth=api.auth, listener=streamlistener, tweet_mode='extended')
            tweetStream.filter(
                track=['kamala harris', 'kamalaharris', 'bernie sanders', 'berniesanders', 'elizabeth warren', 'elizabethwarren', 'joe biden', 'joebiden', 'donald trump', 'donaldtrump', 'pete buttigieg', 'petebuttigieg']
            )
        except Exception as e:
            print(e)
            time.sleep(6)
        print("digesting tweets")




        

