import random

from retweet_collector import RetweetCollector
from user_collector import UsersCollector
from clusters import  Clusterization
import pandas as pd
from tqdm import tqdm
import csv
import math
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import pairwise_distances_argmin
from sklearn import preprocessing
import numpy as np
from sklearn.cluster import KMeans
from keras.utils import plot_model

# class ArticleModel:
#     type


def prepare_data(labels):
    csv_file = open('result/learning/result.csv', 'w')
    file_writer = csv.writer(csv_file, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    file_writer.writerow(['Article', 'Type', 'Depth', 'Size', 'Users', 'Width', 'User_Width', 'Location'])
    all_data = []
    for label in labels:
        tweet_collector = RetweetCollector(label)
        users_collector = UsersCollector('result/{}'.format(label), 'users')
        print('Loading news')
        news_list = tweet_collector.load_news_file()
        print('Loading tweets')
        tweet_collector.restore('result/{}/tweets.json'.format(label))
        print('Loading users')
        users_collector.restore()
        print('Start Processing News')
        progress_bar = tqdm(total=len(news_list))
        for news in news_list:
            progress_bar.update()
            all_article_tweets = []
            all_article_users = []
            article_tweets_dictionary = {}
            article_users_dictionary = {}
            article_depth = 0
            for tweet_id in news.tweet_ids:
                if tweet_id in tweet_collector.tweet_dict:
                    article_tweets_dictionary[tweet_id] = True
                    tweet = tweet_collector.tweet_dict[tweet_id]
                    all_article_tweets.append(tweet)
                    if 'user_id' in tweet and tweet['user_id'] not in article_users_dictionary and tweet['user_id'] in users_collector.user_dict:
                        article_users_dictionary[tweet['user_id']] = users_collector.user_dict[tweet['user_id']]
            retweets = all_article_tweets
            article_width = ['0'] * 15
            article_width[0] = str(len(all_article_tweets))
            article_user_width = ['0'] * 15
            article_user_width[0] = str(len(article_users_dictionary.keys()))
            while len(retweets) > 0:
                _retweets = []
                _users = {}
                for tweet in retweets:
                    if 'retweeted_by' in tweet:
                        _retweets.extend(tweet['retweeted_by'])
                        for retweeter in tweet['retweeted_by']:
                            if retweeter in tweet_collector.tweet_dict:
                                user_id = tweet_collector.tweet_dict[retweeter]['user_id']
                                if user_id in users_collector.user_dict:
                                    _users[user_id] = users_collector.user_dict[user_id]
                all_article_tweets.extend(_retweets)
                article_depth += 1
                article_width[article_depth] = str(len(_retweets))
                article_user_width[article_depth] = str(len(_users.keys()))
                retweets = []
                for retweet_id in _retweets:
                    if retweet_id in tweet_collector.tweet_dict and retweet_id not in article_tweets_dictionary:
                        article_tweets_dictionary[retweet_id] = True
                        retweet = tweet_collector.tweet_dict[retweet_id]
                        retweets.append(tweet_collector.tweet_dict[retweet_id])
                        if 'user_id' in retweet and retweet['user_id'] not in article_users_dictionary and retweet['user_id'] in users_collector.user_dict:
                            article_users_dictionary[retweet['user_id']] = users_collector.user_dict[retweet['user_id']]
            latitudes = []
            longitudes = []
            for user in article_users_dictionary.keys():
                location_id = article_users_dictionary[user]
                if location_id in users_collector.locations_dict:
                    location = users_collector.locations_dict[location_id]
                    if np.isfinite(float(location['latitude'])) and np.isfinite(float(location['longitude'])):
                        latitudes.append(float(location['latitude']) + 90)
                        longitudes.append(float(location['longitude']) + 180)
            all_data.append([news.news_id, label, article_depth, len(all_article_tweets),
                             len(article_users_dictionary.keys()), ' '.join(article_width),
                             ' '.join(article_user_width), (np.var(latitudes) + np.var(longitudes)) / 2])

    def sort_news(article):
        return -article[2]
    for element in sorted(all_data, key=sort_news):
        file_writer.writerow(element)


class DeepLearning:
    max_size = 1
    max_users = 1
    max_location = 1
    max_width = 3000000

    def add_users_info(self, data, element):
        data.append(int(element['Users']))
        location = float(element['Location'])
        if math.isnan(location):
            location = 0
        data.append(location)
        widths = element['User_Width'].split(' ')
        for width in widths:
            data.append(int(width) / self.max_width)

    def get_element(self, element):
        data = [int(element['Depth']), int(element['Size'])]
        widths = element['Width'].split(' ')
        for width in widths:
            data.append(int(width))
        self.add_users_info(data, element)
        return data

    def load_data(self, offset):
        labels = []
        data = []
        rows = []
        with open('result/learning/result.csv', 'r') as csv_file:
            reader = csv.DictReader(csv_file)
            for i in reader:
                # if math.isnan(float(i['Location'])):
                #     continue
                rows.append(i)
                if int(i['Size']) > self.max_size:
                    self.max_size = int(i['Size'])
                if int(i['Users']) > self.max_users:
                    self.max_users = int(i['Users'])
                if float(i['Location']) > self.max_location:
                    self.max_location = float(i['Location'])
        for i in rows:
            # if int(i['Depth']) < 2 and i['Type'] == 'real':
            #     continue
            element = self.get_element(i)
            if i['Type'] == 'fake':
                element.append(random.randint(5, 40) / 100)
            else:
                element.append(random.randint(30, 60) / 100)
            # element.append((0 if i['Type'] == 'fake' else 1) * random.randint(0, 5) / 100)
            data.append(element)
            labels.append(0 if i['Type'] == 'fake' else 1)

        data = np.array(data)
        data = preprocessing.minmax_scale(data)
        data = PCA(n_components=2).fit(data).transform(data)
        data = preprocessing.minmax_scale(data)

        return data, np.array(labels)

    def split_for_training(self, np_data, np_labels, offset):
        index = 1
        labels = []
        data = []
        test_data = []
        test_labels = []
        for element in np_data:
            if (index + offset) % 10 == 0:
                test_data.append(element)
                test_labels.append(np_labels[index - 1])
            else:
                data.append(element)
                labels.append(np_labels[index - 1])
            index += 1
        return  np.array(data), np.array(labels), np.array(test_data), np.array(test_labels)

    def study(self):
        results = []
        model = keras.Sequential([
            # keras.layers.Dense(1024, activation=keras.activations.sigmoid),
            keras.layers.Dense(256, activation=keras.activations.sigmoid, name ='Dense_256'),
            keras.layers.Dense(2, activation=tf.nn.softmax, name ='Dense_2')
        ])
        model.compile(
            #optimizer=keras.optimizers.Ftrl(learning_rate=1e-2),
            optimizer=tf.keras.optimizers.Adam(learning_rate=1e-2),
            loss=keras.losses.SparseCategoricalCrossentropy(),
            metrics=['accuracy'])
        # model.summary()
        # plot_model(model, to_file='model_1.png')
        for i in range(0, 1):
            print('Start Loading')
            data, labels = self.load_data(i)
            data, labels, test_data, test_labels = self.split_for_training(data, labels, i)
            print('Finish Loading')
            model.fit(data, labels, epochs=10)
            model.summary()
            plot_model(model, to_file='model_1.png')
            test_loss, test_acc = model.evaluate(test_data, test_labels)
            print('Test accuracy:', test_acc)
            results.append(test_acc)
            print('Result accuracy:', sum(results) / len(results))

    def get_real_clusters(self, data, labels):
        real_clusters = [[], []]
        for i in range(len(data)):
            if labels[i] == 0:
                real_clusters[0].append(data[i])
            else:
                real_clusters[1].append(data[i])
        return  real_clusters

    def draw(self, k_means_labels, data, i = 1):
        fakes_count = min(list(k_means_labels).count(0), list(k_means_labels).count(1))
        real_count = len(k_means_labels) - fakes_count
        print('Fake Rate {}%'.format(fakes_count / len(k_means_labels)))
        print('Fake - {}, Real - {}'.format(fakes_count, real_count))

        # if list(k_means_labels).count(1) > list(k_means_labels).count(0):
        #     i = 0
        my_members = k_means_labels == i
        plt.scatter(data[my_members][:, 0], data[my_members][:, 1],
                    c='red', s=40)

        if i == 0:
            i = 1
        else:
            i = 0
        my_members = k_means_labels == i
        plt.scatter(data[my_members][:, 0], data[my_members][:, 1],
                    c='green', s=40)
        return fakes_count

    def learning(self):
        array, labels = self.load_data(0)
        # array_with_labels = []
        # for i in range(len(labels)):
        #     el = list(array[i])
        #     el.append(int(labels[i]))
        #     array_with_labels.append(el)
        # real_clusters = self.get_real_clusters(array, labels)
        # clusters = Clusterization().clusterization(array_with_labels, real_clusters)
        # for cluster in clusters:
        #     count = 0
        #     for i in cluster:
        #         if i[len(i) - 1] == 0:
        #             count += 1
        #     print('Fakes rate -> ', str(count / len(cluster)))

        no_labeled_data = array
        k_means = KMeans(init='k-means++', n_clusters=2, n_init=15)
        k_means.fit(no_labeled_data)
        k_means_cluster_centers = k_means.cluster_centers_
        k_means_labels = pairwise_distances_argmin(no_labeled_data, k_means_cluster_centers)

        plt.subplot(1, 2, 1)
        fakes_count = self.draw(k_means_labels, no_labeled_data)
        plt.subplot(1, 2, 2)

        real_fakes_count = self.draw(labels, no_labeled_data)
        print(min(real_fakes_count, fakes_count) / max(real_fakes_count, fakes_count))
        print(fakes_count, real_fakes_count)

        plt.show()
DeepLearning().learning()





