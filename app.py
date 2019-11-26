import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import tweepy
import sqlalchemy as db
from credentials import *
from config import *
import plotly
import plotly.graph_objs as go
import re
import pandas as pd 
import numpy as np
#import spacy
from country_list import countries_for_language

"""Module for running simple Dash frontend for data visualization. 
This module mostly follows the Dash tutorial by Plot.ly at 
https://dash.plot.ly/?_ga=2.241245510.535093190.1574715357-1256082571.1574715357"""

#mySQL setup via SqlAlchemy
#use trailtweets for streaming, user-based version
#use trailtracker for initial concept version, using static database of collected tweets by candidates
engine = db.create_engine(f'mysql+mysqldb://{user}:{pw}@{host}/trailtweets?charset=utf8mb4', encoding='utf-8')
conn = engine.connect()
meta = db.MetaData()
meta.reflect(bind=engine)


tweets_t = meta.tables['tweets']
retweets_t = meta.tables['retweets']

#script for sorting tweets (naively) by political topic
countries = [re.compile(f'{country[1]}'.lower()) for country in countries_for_language('en')]
fp_words = [re.compile(r'state department'), re.compile(r'foreign policy'), re.compile(r'\bnato\b'), re.compile(r'european union'), re.compile(r'\beu\b'), re.compile(r'african union'), re.compile(r'\bau\b'), re.compile(r'african?'), re.compile(r'pentagon'), re.compile(r'\bwar\b')]

for word in fp_words:
    countries.append(word)

topics_keywords = {
    "Immigration" : [re.compile(r'immigr.*'), re.compile(r'borders?'), re.compile(r'migrants?'), re.compile(r'asylum')],
    "Taxes": [re.compile(r'\btax(es)?\b'), re.compile(r'\birs\b')],
    "Economy": [re.compile(r'\beconom.*\b'), re.compile(r'recessions?'), re.compile(r'\bgdp\b'), re.compile(r'incomes?'), re.compile(r'inflation'), re.compile(r'monetary')],
    "Racism": [re.compile(r'\brace\b'), re.compile(r'racis(t|m)s?'), re.compile(r'anti-black'), re.compile(r'white suprem(acy|acist)s?'), re.compile(r'hate crimes?'), re.compile(r'minorit(ies|y)'), re.compile(r'\breparations\b')],
    "International Relations": countries,
    "Poverty": [re.compile(r'socioeconomic'), re.compile(r'the\srich'), re.compile(r'poor'), re.compile(r'poverty'), re.compile(r'low-?\s?income'), re.compile(r'working-?\s?(people|class)')],
    "Terrorism": [re.compile(r'terror(ist|ism)?s?'), re.compile(r'\bisi(l|s)\b'), re.compile(r'al-qaeda'), re.compile(r'daesh'), re.compile(r'al-shabab'), re.compile(r'islamic\sstate'), re.compile(r'bomb(ing)?s?'), re.compile(r'\bdhs\b'), re.compile(r'homeland\ssecurity')],
    "Guns": [re.compile(r'guns?'), re.compile(r'\bnra\b'), re.compile(r'bump\sstock'), re.compile(r'shoo?t(ing)?s?')],
    "Education": [re.compile(r'education'), re.compile(r'schools?'), re.compile(r'curricul(um|a)?s?')],
    "Health Care": [re.compile(r'medicare'), re.compile(r'medicaid'), re.compile(r'(health|obama|trump)-?\s?care'), re.compile(r'\baca\b'), re.compile(r'affordable\scare\sact'), re.compile(r'single-?\s?payer'), re.compile(r'public\soption'), re.compile(r'(un)?insur(ed|ance)'), re.compile(r'pre-?existing\sconditions?')],
    "Environment": [re.compile(r'environment(al)?(ism)?'), re.compile(r'green\snew\sdeal'), re.compile(r'climate\schange'), re.compile(r'global\swarming'), re.compile(r'\bcarbon\b'), re.compile(r'\bemissions?\b'), re.compile(r'pollution'), re.compile(r'water\ssupply')],
    "LGBTQ+": [re.compile(r'lgbtq?'), re.compile(r'gay'), re.compile(r'lesbian'), re.compile(r'\bbi(sexual)?\b'), re.compile(r'\btrans(gender)?\b'), re.compile(r'gender\sidentity'), re.compile(r'\btrans(gender)?\b'), re.compile(r'\bcis(gender)?\b'), re.compile(r'heterosex')],
    "Sexism": [re.compile(r'\bsexism\b'), re.compile(r'pay\sgap'), re.compile(r'wage\sgap'), re.compile(r'patriarch')],
    "Social Security": [re.compile(r'social\ssecurity'), re.compile(r'\bretired?(ment)?\b'), re.compile(r'\bpension(er)?\b'), re.compile(r'\bira\b')],
    "Employment": [re.compile(r'\b(un)?(under)?-?employ(ed)?(ment)?(er)?s?\b'), re.compile(r'\bjobs?\b'), re.compile(r'\bworks?(ing)?(ed)?\b')],
    "Refugees": [re.compile(r'refugee'), re.compile(r'displaced\spersons?'), re.compile(r'displaced\speoples?')],
    "Religion": [re.compile(r'religio'), re.compile(r'faith'), re.compile(r'god'), re.compile(r'christian'), re.compile(r'judaism'), re.compile(r'islam'), re.compile(r'jew'), re.compile(r'muslim'), re.compile(r'hindu'), re.compile(r'buddha?'), re.compile(r'atheis'), re.compile(r'humanis'), re.compile(r'secular')],
    "Drugs": [re.compile(r'drugs?'), re.compile(r'marijuana'), re.compile(r'opiod'), re.compile(r'\bheroin\b'), re.compile(r'cocaine'), re.compile(r'\bdea\b')],
    "Policing": [re.compile(r'police?(ing)?'), re.compile(r'prison'), re.compile(r'\blaw\senforcement\b')]
}

candidate_fullnames = ["kamala harris", "joe biden", "pete buttigieg", "elizabeth warren", "bernie sanders", "donald trump"]

topic_list = pd.Series([topic for topic in topics_keywords.keys()])

tweet_ids = [ident[0] for ident in conn.execute(db.select([tweets_t.c.tweetId]))]
retweet_ids = [ident[0] for ident in conn.execute(db.select([retweets_t.c.rt_tweetID]))]
tweet_users = [username[0] for username in conn.execute(db.select([tweets_t.c.user]))]
retweet_users_author = [username[0] for username in conn.execute(db.select([retweets_t.c.user_author]))]
retweet_users_retweeter = [user[0] for user in conn.execute(db.select([retweets_t.c.user_retweeted_by]))]
tweet_texts = [text[0] for text in conn.execute(db.select([tweets_t.c.text]))]
retweet_texts = [text[0] for text in conn.execute(db.select([retweets_t.c.rt_text]))]
tweet_times = [timest[0] for timest in conn.execute(db.select([tweets_t.c.time]))]
retweet_times = [timest[0] for timest in conn.execute(db.select([retweets_t.c.rt_time]))]
tweet_df = pd.DataFrame({
    #note the table name in db is tweetId not tweetID, different from retweet table
    "ID": [ident for ident in conn.execute(db.select([tweets_t.c.tweetId]))],
    "User": [username for username in conn.execute(db.select([tweets_t.c.user]))],
    "Text": [text for text in conn.execute(db.select([tweets_t.c.text]))],
    "Time": [timest for timest in conn.execute(db.select([tweets_t.c.time]))]
})
retweet_df = pd.DataFrame({
    "ID": [ident for ident in conn.execute(db.select([retweets_t.c.rt_tweetID]))],
    "User_Author": [username for username in conn.execute(db.select([retweets_t.c.user_author]))],
    "User_Who_Retweeted": [user for user in conn.execute(db.select([retweets_t.c.user_retweeted_by]))],
    "Text": [text for text in conn.execute(db.select([retweets_t.c.rt_text]))],
    "Time": [timest for timest in conn.execute(db.select([retweets_t.c.rt_time]))]
})


tweetlist = list(set(tweet_texts + retweet_texts))
def tweet_sort(tweet_list, topic_hash):
    return [(kvpair[0], tweet) for tweet in tweet_list for kvpair in topic_hash.items() for keyword in kvpair[1] if re.search(keyword, tweet)]

sorted_tweets = tweet_sort(tweetlist, topics_keywords)
topic_sorted_df = pd.DataFrame({
    "Topic": [tweet[0] for tweet in sorted_tweets],
    "Tweet": [tweet[1] for tweet in sorted_tweets]
})

#create Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1('Trailtracker'),
    html.H3('Select a candidate to view breakdown of tweets about that candidate by topic.'),
    dcc.Dropdown(
        id='candidate-selector',
        options = [{'label': cand_name, 'value': cand_name} for cand_name in candidate_fullnames],
        value = 'bernie sanders'
    ),
    dcc.Graph(id = 'topics-by-candidate-barchart'),
    # html.Div(
    #     #add viz using SpaCy for which word tokens appear most frequently among tweets about candidate
    #     #add viz for top 5 users by number of tweets in the category
    # )
])

@app.callback(
    Output(component_id='topics-by-candidate-barchart', component_property='figure'),
    [Input(component_id='candidate-selector', component_property='value')]
)
def update_chart(candidate_name): #candidate_name: str in format 'firstname lastname'
    try:
        name_re = re.split(r'\s', candidate_name)
    except Exception as e:
        candidate_name = 'bernie sanders'
        name_re = re.split(r'\s', candidate_name)
    fname = name_re[0]
    lname = name_re[1]
    #test below df further to see if it's matching the right strings
    chart_df = topic_sorted_df[topic_sorted_df['Tweet'].str.contains(re.compile(fname + r'|' + lname))]
    return {
        'data': [go.Bar(
            x = [val[1] for val in topic_list.items()],
            y = [chart_df[chart_df['Topic'].str.contains(val[1])].Tweet.count() for val in topic_list.items()]
        )]
    }

if __name__ == '__main__':
    app.run_server(debug=False)