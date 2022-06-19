import json
import logging
import time
import requests
import tweepy

class TwythonConnector:
    def __init__(self, keys_server_url, key_file):
        self.streams = []
        self.init_twython_objects(key_file)
        self.url = "http://" + keys_server_url + "/get-keys?resource_type="
        self.max_fail_count = 3

    def init_twython_objects(self, keys_file):
        keys = json.load(open(keys_file, 'r'))
        for key in keys:
            self.streams.append(self.get_twitter_connection(connection_mode=0, app_key=key['app_key'],
                                                             app_secret=key['app_secret'],
                                                             oauth_token=key['oauth_token'],
                                                             oauth_token_secret=key['oauth_token_secret']))

    @staticmethod
    def get_twitter_connection(connection_mode=0, app_key=None, app_secret=None, oauth_token=None,
                                oauth_token_secret=None):
        ACCESS_TOKEN = 'AAAAAAAAAAAAAAAAAAAAAD6KbwEAAAAAqVBRWzvSy7lCf1SI%2FUaqKdMtBVA%3DZ0ClGf77aYvRlao8iWijktBmSltQ5X8b3vQMyBXcffWRCDC7oi'
        client = tweepy.Client(ACCESS_TOKEN, wait_on_rate_limit=True)
        return client

    def get_twython_connection(self, resource_type):
        resource_index = self.get_resource_index(resource_type)
        return self.streams[resource_index]

    def get_resource_index(self, resource_type):
        while True:
            response = requests.get(self.url + resource_type)
            if response.status_code == 200:
                response = json.loads(response.text)
                if response["status"] == 200:
                    print("resource id : {}".format(response["id"]))
                    return response["id"]
                else:
                    print("sleeping for {} seconds".format(response["wait_time"]))
                    logging.info("sleeping for {} seconds".format(response["wait_time"]))
                    time.sleep(response["wait_time"])
