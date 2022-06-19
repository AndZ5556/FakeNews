import json
import re
from multiprocessing.pool import Pool
from tqdm import tqdm
from twitter_connector import TwythonConnector as twython_connector


class News:
    def __init__(self, info_dict, label, news_platform):
        self.news_id = info_dict["id"]
        self.news_url = info_dict["news_url"]
        self.news_title = info_dict["title"]
        self.tweet_ids = []

        try:
            tweets = [int(tweet_id) for tweet_id in info_dict["tweet_ids"].split("\t")]
            self.tweet_ids = tweets
        except:
            pass

        self.label = label
        self.platform = news_platform


def sort_tweets(tweet):
    if 'retweet_count' in tweet:
        return -tweet['retweet_count']
    return 0

def multiprocess_data_collection(function_reference, data_list):
    pool = Pool(4)

    pbar = tqdm(total=len(data_list))

    def update(arg):
        pbar.update()

    for i in range(pbar.total):
        pool.apply_async(function_reference, args=(data_list[i], ), callback=update)

    pool.close()
    pool.join()

def equal_chunks(list, chunk_size):
    chunks = []
    for i in range(0, len(list), chunk_size):
        chunks.append(list[i:i + chunk_size])

    return chunks


def fix_location(location):
    if not isinstance(location, str):
        return location
    clear_location = location.replace('"', '')
    clear_location = clear_location.replace('\\', '')
    try:
        json.loads('{ "location": "' + clear_location + '" }')
    except Exception:
        clear_location = re.sub('[^A-Za-z0-9 ,.:-]+', '', clear_location)
        try:
            json.loads('{ "location": "' + clear_location + '" }')
        except Exception:
            clear_location = 'null'
    return clear_location
