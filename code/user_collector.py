import os
from json_encoder import CompactJSONEncoder as json
import uuid
import json as true_json
from tqdm import tqdm
from geopy.geocoders import Nominatim
from utils import fix_location

def collect_users(dir, file):
    source_path = '{}/{}.json'.format(dir, file)
    users_collector = UsersCollector(dir, file)
    users_collector.restore()
    tweets = json.loadFile(source_path)
    users_collector.collect_data(tweets)

class UsersCollector():
    geolocator = None
    user_dict = {}
    locations_dict = {}
    result = { 'users': [], 'locations': []}
    target_path = ''
    user_count = 0
    init_count = 1000

    def __init__(self, dir, file):
        self.target_path = '{}/{}.json'.format(dir, file)
        self.geolocator = Nominatim(user_agent=str(uuid.uuid4()))
        # self.geolocator = OpenMapQuest(api_key='n2h9rP9fKVZV2jYlUjthxBgGDyE3Sh8Q', user_agent=str(uuid.uuid4()))

    def load_line(self, str):
        try:
            location = true_json.loads(str[:-2])
        except Exception as exception:
            location = true_json.loads(str)
        return location

    def restore_from_file(self, file_name):
        print('Restoring from {}'.format(file_name))
        if not os.path.isfile(file_name):
            print('Fail -> Target path does not exist')
            return
        file = open(file_name, 'r', encoding="utf8")
        str = file.readline()
        while str is not None:
            str = file.readline()
            if str.find('locations') != -1:
                break
            user = self.load_line(str)
            self.user_dict[user['id']] = user['location']
            self.result['users'].append(user)
        while str is not None:
            str = file.readline()
            if str.find('id') == -1:
                break
            s = str.split('"address": "')[1].split('",      "latitude"')[0]
            clear_s = s.replace('"', '')
            str = str.replace(s, clear_s)
            location = self.load_line(str)
            self.locations_dict[location['id']] = location
            self.result['locations'].append(location)
        self.user_count = len(self.result['users'])
        self.init_count = self.user_count + 100

    def restore(self):
        # self.result = json.loadFile(self.target_path)
        print('Try restore file:')
        self.restore_from_file(self.target_path)
        print('Finish restore file. Backup length -> {}'.format(self.user_count))

    def collect_data(self, tweets):
        print('Collecting users data')
        pbar = tqdm(total=len(tweets))
        for tweet in tweets:
            self.get_user_from_tweet(tweet)
            if self.user_count > self.init_count and self.user_count % 1001 == 0:
                self.dump()
            pbar.update()
        print('Finish collecting users data')
        self.dump()

    def collect_raw_data(self, raw_tweets):
        tweets = []
        for raw_tweet in raw_tweets:
            tweet = {
                'user_id': raw_tweet.id,
                'location': fix_location(raw_tweet.location)
            }
            tweets.append(tweet)
        self.collect_data(tweets)

    def dump(self):
        json(indent=2).dump(self.result, self.target_path)

    def get_user_from_tweet(self, tweet):
        user_dict = self.user_dict
        locations_dict = self.locations_dict
        geolocator = self.geolocator
        result = self.result
        if tweet['user_id'] not in user_dict:
            user = {}
            user['id'] = tweet['user_id']
            try:
                location = geolocator.geocode(tweet['location'])
                if location is not None:
                    location = geolocator.reverse(location.point, language='en')
                    user['location'] = location.raw['place_id']
                    loc = location.raw
                    if loc['place_id'] not in locations_dict:
                        location_serialized = {
                            'id': loc['place_id'],
                            'address': fix_location(location.address),
                            'latitude': location.latitude,
                            'longitude': location.longitude
                        }
                        if 'city' in loc['address']:
                            location_serialized['city'] = loc['address']['city']
                        if 'country' in loc['address']:
                            location_serialized['country'] = loc['address']['country']
                        result['locations'].append(location_serialized)
                        locations_dict[location.raw['place_id']] = location_serialized
                else:
                    user['location'] = None
            except Exception as exception:
                user['location'] = None
            result['users'].append(user)
            self.user_count += 1
            user_dict[tweet['user_id']] = tweet['location']

# http = urllib3.PoolManager(1, headers={'user-agent': 'my-test-app'})
#
# url = 'https://nominatim.openstreetmap.org/search?country=DE&city=Erlangen&postalcode=91052&street=N%C3%BCrnberger+Stra%C3%9Fe+7&format=json&limit=1'

# resp = http.request('GET', url)
# data = resp.data.decode()
# json.loads(esp.data.decode())
# geolocator = Nominatim(user_agent='myagent')
# location = geolocator.geocode('London')
# print(location)


# collector = UsersCollector('result/real', 'users')
# arr = ['all_tweets_users']
# for i in range(2, 8):
#     arr.append('all_retweets{}_users'.format(i))
# for file in arr:
#     collector.restore_from_file('./dumps/real/{}.json'.format(file))
# collector.dump()
# for file in arr:
#     print('Collecting {}'.format(file))
#     collect_users('dumps/real', file)