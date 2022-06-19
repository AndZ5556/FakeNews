import rdflib.util
from twython import Twython
import tweepy
from tqdm import tqdm
import os

from json_encoder import CompactJSONEncoder as json
from rdflib.namespace import DC, DCTERMS, DOAP, FOAF, SKOS, OWL, RDF, RDFS, VOID, XMLNS, XSD
from rdflib import Graph, URIRef, Literal, Namespace, term, RDF
from rdflib.namespace import RDFS, XSD
# import  rdflib

g = Graph()
FN = Namespace("http://fakenews.net/")

def process_users(path):
    data = json.loadFile(path)
    pbar = tqdm(total=len(data['users']))
    for user in data['users']:
        id = "user:{}".format(user['id'])
        g.add((FN[id], RDF.type, FN.User))
        if user['location'] is not None:
            g.add((FN[id], FN.location, FN["location:{}".format(user['location'])]))
        pbar.update()
    pbar = tqdm(total=len(data['locations']))
    for location in data['locations']:
        id = "location:{}".format(location['id'])
        g.add((FN[id], RDF.type, FN.Location))
        g.add((FN[id], FN.address, Literal(location['address'])))
        g.add((FN[id], FN.latitude, Literal(location['latitude'])))
        g.add((FN[id], FN.longitude, Literal(location['longitude'])))
        if 'city' in location:
            g.add((FN[id], FN.city, Literal(location['city'])))
        if 'country' in location:
            g.add((FN[id], FN.country, Literal(location['country'])))
        pbar.update()
    g.bind("fn", FN)
    open('rdf/users_2.ttl', "w", encoding="utf-8").write(g.serialize(format="turtle"))

def reverse_tweets():
    dict = {}
    g = Graph()
    data = json.loadFile('result/fake/tweets.json')
    count = 0
    pbar = tqdm(total=len(data))
    for tweet in data:
        tweet['retweeted_by'] = []
        dict[tweet['tweet_id']] = tweet
        pbar.update()
    pbar = tqdm(total=len(data))
    for tweet in data:
        if tweet['retweet_to'] is not None:
            dict[int(tweet['retweet_to'])]['retweeted_by'].append(tweet['tweet_id'])
        pbar.update()
    pbar = tqdm(total=len(data))
    for key in dict:
        pbar.update()
        process_tweet(dict[key], g)
    g.bind("fn", FN)
    open('rdf/reversed_tweets.ttl', "w", encoding="utf-8").write(g.serialize(format="turtle"))

def process_tweet(tweet, graph):
    id = "tweet:{}".format(tweet['tweet_id'])
    graph.add((FN[id], RDF.type, FN.Tweet))
    graph.add((FN[id], FN.author, FN["user:{}".format(tweet['user_id'])]))
    for tweet_id in tweet['retweeted_by']:
        graph.add((FN[id], FN.retweeted_by, FN["tweet:{}".format(tweet_id)]))
    graph.add((FN[id], FN.retweet_count, Literal(len(tweet['retweeted_by']))))

def process_tweets(paths):
    for path in paths:
        data = json.loadFile(path)
        pbar = tqdm(total=len(data))
        for tweet in data:
            process_tweet(tweet)
            pbar.update()
    g.bind("fn", FN)
    open('result.ttl', "w", encoding="utf-8").write(g.serialize(format="turtle"))

def join_tweets(paths):
    tweets = []
    dict = {}
    for path in paths:
        data = json.loadFile(path)
        pbar = tqdm(total=len(data))
        for tweet in data:
            if tweet['tweet_id'] not in dict:
                tweets.append(tweet)
                dict['tweet_id'] = True
            pbar.update()
    json(indent=2).dump(tweets, 'result/fake/tweets.json')

def process_news(type):
    dict = {}
    dump = json.loadFile('./news/news_dump_{}.json'.format(type))
    pbar = tqdm(total=len(dump))
    for element in dump:
        id = "article:{}".format(element['id'].split('-')[1])
        g.add((FN[id], RDF.type, FN.Article))
        for tweet in element['tweet_ids']:
            g.add((FN[id], FN.retweeted_by, FN["tweet:{}".format(tweet)]))
        if 'time' in element and element['time'] is not None:
            g.add((FN[id], FN.time, Literal(rdflib.util.date_time(element['time']))))
        g.add((FN[id], FN.article_type, Literal(type)))
        pbar.update()
    g.bind("fn", FN)
    open('rdf/result_news_real.ttl', "w", encoding="utf-8").write(g.serialize(format="turtle"))
# join_tweets(['./dumps/all_tweets.json', './dumps/all_retweets.json', './dumps/all_re_retweets.json',
#                 './dumps/all_re_retweets2.json', './dumps/all_re_retweets3.json', './dumps/all_re_retweets4.json',
#                 './dumps/all_re_retweets5.json', './dumps/all_re_retweets6.json', './dumps/all_re_retweets7.json'])

# process_users('./dumps/all_re_retweets7_users.json')


reverse_tweets()
