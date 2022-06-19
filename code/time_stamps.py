from utils import multiprocess_data_collection, equal_chunks
from twitter_connector import TwythonConnector as twython_connector
from json_encoder import CompactJSONEncoder as json
import json as true_json
from multiprocessing.pool import Pool
from tqdm import tqdm

def dump_tweet_information(tweet_chunk: list, client):
    """Collect info and dump info of tweet chunk containing atmost 100 tweets"""

    tweet_list = []
    for tweet in tweet_chunk:
        tweet_list.append(tweet['tweet_id'])

    try:
        tweet_objects_map = client.get_tweets(ids=tweet_list,
                                                                                                     tweet_fields='created_at',
                                                                                                     expansions='author_id,geo.place_id',
                                                                                                 user_fields='location')
        object_array = []
        for tweet in tweet_chunk:
            for tweet_data in tweet_objects_map.data:
                if tweet['tweet_id'] == tweet_data.id:
                    tweet_object = {}
                    tweet_object['tweet_id'] = tweet_data.id
                    tweet_object['time'] = str(tweet_data.created_at)
                    object_array.append(tweet_object)
        true_json.dump(object_array, open("time/{}.json".format(tweet_chunk[0]['tweet_id']), "w"))


    except Exception as e:
        print(e)

    return None

def load_time():
    data = json.loadFile('result/fake/tweets.json')
    array = []
    dict = {}
    for tweet in data:
        if 'tweet_id' not in dict:
            dict[tweet['tweet_id']] = tweet
            array.append(tweet)
    print('Collected')
    tweet_chunks = equal_chunks(array, 100)
    pool = Pool(processes=4)

    pbar = tqdm(total=len(tweet_chunks))
    connection = twython_connector.get_twitter_connection()
    def update(arg):
        pbar.update()

    for i in range(pbar.total):
        pool.apply_async(dump_tweet_information, args=(tweet_chunks[i], connection), callback=update)

    pool.close()
    pool.join()
