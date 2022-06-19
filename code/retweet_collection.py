import json
import shutil
import os
from tqdm import tqdm
import tweepy

from json_encoder import CompactJSONEncoder
from retweet_collector import RetweetCollector
from utils import fix_location, sort_tweets

# def get_retweets_count(tweet: Tweet):
#     path = "{}/{}/{}/{}/tweets/{}.json".format(config.dump_location, tweet.news_source, tweet.label, tweet.news_id, tweet.tweet_id)
#     try:
#         existed_tweet = json.load(open(path))
#         if existed_tweet['retweet_count'] and existed_tweet['retweet_count'] > 0:
#             return existed_tweet['retweet_count'] or 0
#     except Exception:
#         return 0


class RetweetCollection:
    news_type = 'fake'
    directory = ''
    save_path = ''
    iteration = 1

    def __init__(self, news_type):
        self.news_type = news_type
        self.directory = './dumps/{}'.format(news_type)
        self.save_path = '{}/saved'.format(self.directory)

    def dump_retweets_job(self, tweet_id, connection: tweepy.Client, retweet_count):
        retweeters = []
        retweets = []
        dump_target = "{}/dump_{}_{}.json".format(self.save_path, retweet_count, tweet_id)

        if os.path.isfile(dump_target):
            return

        pbar = tqdm(total=retweet_count)
        try:
            pooled_tweets = connection.get_retweeters(id=tweet_id, user_auth=False,
                                                      expansions="pinned_tweet_id",
                                                      tweet_fields="public_metrics,created_at",
                                                      user_fields="location")
            while pooled_tweets.data and len(pooled_tweets.data) > 0 and pooled_tweets.meta['next_token']:
                pbar.update(len(pooled_tweets.data))
                retweeters.extend(pooled_tweets.data)
                if pooled_tweets.includes and pooled_tweets.includes['tweets']:
                    retweets.extend(pooled_tweets.includes['tweets'])
                pooled_tweets = connection.get_retweeters(id=tweet_id, user_auth=False, user_fields="location",
                                                          expansions="pinned_tweet_id",
                                                          tweet_fields="public_metrics,created_at",
                                                          pagination_token=pooled_tweets.meta['next_token'])
        except Exception as e:
            print(e)

        if len(retweeters) > 0:
            retweets_array = []
            for retweeter in retweeters:
                retweet_data = {}
                retweet_data['user_id'] = retweeter.id
                retweet_data['location'] = fix_location(retweeter.location)
                if retweeter.pinned_tweet_id:
                    retweet_data['pinned_tweet_id'] = retweeter.pinned_tweet_id
                    for retweet in retweets:
                        if retweet.id == retweeter.pinned_tweet_id and retweet.public_metrics is not None:
                            retweet_data['retweet_count'] = retweet.public_metrics['retweet_count']
                            retweet_data['time'] = str(retweet.created_at)
                        else:
                            retweet_data['retweet_count'] = 0
                else:
                    retweet_data['pinned_tweet_id'] = None
                    retweet_data['retweet_count'] = 0
                retweets_array.append(retweet_data)
            CompactJSONEncoder(indent=2).dump(sorted(retweets_array, key=sort_tweets), dump_target)

    @staticmethod
    def get_existed_info(collected_path):
        result = {}
        if os.path.isfile(collected_path):
            data = CompactJSONEncoder.loadFile(collected_path)
            for tweet in data:
                result[tweet['retweet_to']] = True
        return result

    def clean_save(self):
        for filename in os.listdir(self.save_path):
            file_path = os.path.join(self.save_path, filename)
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)

    def upload_retweets(self):
        collected_path = "{}/all_retweets{}_small.json".format(self.directory, self.iteration)

        if self.iteration == 1:
            collected_path = "{}/all_tweets.json".format(self.directory)

        existed_info = self.get_existed_info("{}/all_retweets{}.json".format(self.directory, self.iteration + 1))
        if not os.path.isfile(collected_path):
            RetweetCollector(self.news_type).collect_retweets(self.save_path, collected_path)
            if os.path.isfile(collected_path):
                self.clean_save()

        client = tweepy.Client(
            # "AAAAAAAAAAAAAAAAAAAAAPQjcAEAAAAAVjF8EazqGBU8J0ZjFKR6e0xrc74%3DqTeMWyML3BGmBBDbLc19bgZMMNM4wL6KzM1A9qEpLNUjg1wmfg",
            "AAAAAAAAAAAAAAAAAAAAAD6KbwEAAAAAqVBRWzvSy7lCf1SI%2FUaqKdMtBVA%3DZ0ClGf77aYvRlao8iWijktBmSltQ5X8b3vQMyBXcffWRCDC7oi",
            wait_on_rate_limit=True)
        json_object = json.loads(open(collected_path, 'r', encoding="utf-8").read().replace("\\", "\\\\"))
        for object in json_object:
            if object['tweet_id'] not in existed_info and 'retweet_count' in object and object['retweet_count'] <= 100 and object['retweet_count'] > 10:
                self.dump_retweets_job(object['tweet_id'], client, object['retweet_count'])
        self.iteration += 1
        self.upload_retweets()
