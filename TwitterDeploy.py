import TwitterStoryScraper
import json
import datetime
import pandas as pd


f = open('TwitterJournalistsList.json',)
accounts_list = json.load(f)['data']


all_tweets = TwitterStoryScraper.scrape_all_tweets(pd.DataFrame(accounts_list)['id'].to_list(), (datetime.datetime.now() - datetime.timedelta(hours=35)).isoformat()[:-7] + "Z")
most_interactions = TwitterStoryScraper.most_interactions_except_likes(all_tweets)
most_urls = TwitterStoryScraper.most_linked_url(all_tweets)

for tweet in most_interactions:
    for val in tweet:
        tweet[val] = str(tweet[val])

f = open('most_interactions.json', 'w')
json.dump(most_interactions, f)
f.close()
f = open('most_urls.json', 'w')
json.dump(most_urls, f)
f.close()
