import os.path

from tqdm import tqdm
from os import walk
import csv
import sys

from json_encoder import CompactJSONEncoder as json
from utils import sort_tweets, News


class RetweetCollector:
    dir_path = './fakenewsnet_dataset/gossipcop/fake'
    type = 'fake'
    tweet_dict = {}

    def __init__(self, type):
        self.type = type
        self.dir_path = './fakenewsnet_dataset/gossipcop/{}'.format(type)

    def generate_serializable_tweet(self, news_id, tweet_id):
        try:
            path = "{}/{}/tweets/{}.json".format(self.dir_path, news_id, tweet_id)
            existed_tweet = json.loadFile(path)
            if 'retweet_count' not in existed_tweet:
                existed_tweet['retweet_count'] = 0
            if 'retweet_to' not in existed_tweet:
                existed_tweet['retweet_to'] = None
            return existed_tweet
        except Exception:
            return None

    def load_result_files(self):
        target_path = './result/{}/tweets.json'.format(self.type)
        dictionary = {}
        result = []
        if os.path.isfile(target_path):
            result = json.loadFile(target_path)
            for element in result:
                dictionary[element['tweet_id']] = True
        files = ["./dumps/{}/all_tweets.json".format(self.type)]
        for i in range(2, 8):
            files.append('./dumps/{}/all_retweets{}_small.json'.format(self.type, i))
        for file in files:
            print('Loading from {}'.format(file))
            data = json.loadFile(file)
            for tweet in data:
                if tweet['tweet_id'] not in dictionary:
                    dictionary['tweet_id'] = True
                    result.append(tweet)
        json(indent=2).dump(sorted(result, key=sort_tweets), target_path)

    def restore(self, source_file):
        dictionary = {}
        data = json.loadFile(source_file)
        pbar = tqdm(total=len(data))
        for tweet in data:
            tweet['retweeted_by'] = []
            dictionary[tweet['tweet_id']] = tweet
            pbar.update()
        pbar = tqdm(total=len(data))
        for tweet in data:
            if tweet['retweet_to'] is not None:
                dictionary[int(tweet['retweet_to'])]['retweeted_by'].append(tweet['tweet_id'])
            pbar.update()
        self.tweet_dict = dictionary

    def process_collected_tweets(self):
        news_list = self.load_news_file()
        tweet_id_list = []
        pbar = tqdm(total=len(news_list))
        print('Collecting tweets')
        for news in news_list:
            pbar.update()
            for tweet_id in news.tweet_ids:
                tweet = self.generate_serializable_tweet(news.news_id, tweet_id)
                if tweet is not None:
                    tweet_id_list.append(tweet)
        json(indent=2).dump(sorted(tweet_id_list, key=sort_tweets), "./dumps/{}/all_tweets.json".format(self.type))
        print('Finish collecting tweets')

    def load_news_file(self):
        max_int = sys.maxsize
        while True:
            try:
                csv.field_size_limit(max_int)
                break
            except OverflowError:
                max_int = int(max_int / 10)

        news_list = []
        with open('./data/gossipcop_{}.csv'.format(self.type), encoding="UTF-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for news in reader:
                news_list.append(News(news, self.type, 'gossipcop'))
        return news_list

    def collect_retweets(self, load_path, target_path):
        f = []
        lenght = 0
        all_retweets = []
        print('Collecting retweets')
        for (dirpath, dirnames, filenames) in walk(load_path):
            f.extend(filenames)
            break
        for file in f:
            print('Collecting in file -> ' + file)
            tweets = json.loadFile("{}/{}".format(load_path, file))
            pbar = tqdm(total=len(tweets))
            for tweet in tweets:
                tweet['retweet_to'] = file.split('.')[0].split('_')[2]
                if 'pinned_tweet_id' in tweet:
                    tweet['tweet_id'] = tweet['pinned_tweet_id']
                    del tweet['pinned_tweet_id']
                pbar.update()
            all_retweets.extend(tweets)
            lenght += len(tweets)
        all_retweets = sorted(all_retweets, key=sort_tweets)
        print('Finish collecting retweets')
        json(indent=2).dump(all_retweets, target_path)

