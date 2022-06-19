import urllib.parse
import re
import urllib.request
from tqdm import tqdm



sparql = '''
PREFIX fn: <http://fakenews.net/>
SELECT ?s ?p ?o
WHERE \{
	fn:{} fn:retweeted_by ?o .
\}
'''

# 'http://localhost:7200/sparql?name=SPARQL%20Select%20template&infer=true&sameAs=true&query=PREFIX%20fn%3A%20%3Chttp%3A%2F%2Ffakenews.net%2F%3E%0ASELECT%20%3Fs%20%3Fp%20%3Fo%0AWHERE%20%7B%0A%09fn%3Aarticle%3A2734628654%20fn%3Aretweeted_by%20%3Fo%20.%0A%7D%20LIMIT%20100'

class GraphHelper:
    def get_select_sparql(id):
        return '''
            PREFIX fn: <http://fakenews.net/>
            SELECT ?s ?p ?o
            WHERE {
                fn:''' + id + ''' fn:retweeted_by ?o .
            }
            '''

    def get_tweets(self):
        url = 'http://SPB10-NB-W10:7200/repositories/fakenews?query='
        query = url + urllib.parse.quote(self.get_select_sparql(article))
        # print (urllib.request.urlretrieve(url + urllib.parse.quote(sparql)))
        all_tweets = []
        dict = {}
        deep = 1
        with urllib.request.urlopen(query) as response:
            s = str(response.read())
            subs = re.findall(r'tweet:[0-9]*', s)
            all_tweets.extend(subs)
            while len(subs) > 0:
                print('Deep ->' + str(deep))
                print('Tweet Count ->' + str(len(all_tweets)))
                pbar = tqdm(total=len(subs))
                re_tweets = []
                for tweet in subs:
                    pbar.update()
                    if tweet not in dict:
                        dict[tweet] = True
                        query = url + urllib.parse.quote(get_select_sparql(tweet))
                        with urllib.request.urlopen(query) as response:
                            s = str(response.read())
                            re_tweets.extend(re.findall(r'tweet:[0-9]*', s))
                subs = re_tweets
                all_tweets.extend(subs)
                deep += 1

        print('Deep ->' + str(deep))
        print('Tweet Count ->' + str(len(all_tweets)))

    def get_retweets(self):
        url = 'http://SPB10-NB-W10:7200/repositories/fakenews?query='
        query = url + urllib.parse.quote(self.get_select_sparql(article))
        # print (urllib.request.urlretrieve(url + urllib.parse.quote(sparql)))
        all_tweets = []
        dict = {}
        deep = 1
        with urllib.request.urlopen(query) as response:
            s = str(response.read())
            subs = re.findall(r'tweet:[0-9]*', s)
            all_tweets.extend(subs)
            while len(subs) > 0:
                print('Deep ->' + str(deep))
                print('Tweet Count ->' + str(len(all_tweets)))
                pbar = tqdm(total=len(subs))
                re_tweets = []
                for tweet in subs:
                    pbar.update()
                    if tweet not in dict:
                        dict[tweet] = True
                        query = url + urllib.parse.quote(self.get_select_sparql(tweet))
                        with urllib.request.urlopen(query) as response:
                            s = str(response.read())
                            re_tweets.extend(re.findall(r'tweet:[0-9]*', s))
                subs = re_tweets
                all_tweets.extend(subs)
                deep += 1
