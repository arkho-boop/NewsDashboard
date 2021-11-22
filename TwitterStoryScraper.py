import pandas as pd
import requests
import json
import datetime
import time

payload = {}
headers = {
    'Authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAAOvIAwEAAAAA92pfv6fozc8zSytQdYOAuZpENzo'
                     '%3DCTd1XNRzobC3UgjO4pON7rlsouAZjVzoHo8iYEJ9bfTaahFaYU',
    'Cookie': 'guest_id=v1%3A163166982787359803; personalization_id="v1_mkR8sgr+WUzTngI9VU8+PA=="'
}


def scrape_tweet(tweet_id):
    url = "https://api.twitter.com/2/tweets/" + str(tweet_id) + "?tweet.fields=author_id"
    response = requests.request("GET", url, headers=headers, data=payload)
    return json.loads(response.text)


def scrape_user_likes(twitter_id):
    url = "https://api.twitter.com/2/users/" + str(twitter_id) + "/liked_tweets"
    response = requests.request("GET", url, headers=headers, data=payload)
    return json.loads(response.text)


def scrape_user_tweets(twitter_id, start_time):
    url = "https://api.twitter.com/2/users/" + str(twitter_id) + "/tweets?expansions=referenced_tweets.id&max_results" \
                                                                 "=100&tweet.fields=entities&start_time=" \
          + str(start_time)
    response = requests.request("GET", url, headers=headers, data=payload)
    return json.loads(response.text)


# which tweets got the most likes?
def scrape_top_most_liked(twitter_id_list):
    time_start = datetime.datetime.now()
    ticker = 0
    output = []
    for twitter_id in twitter_id_list:
        ticker += 1
        time_change = datetime.datetime.now() - time_start

        if (ticker == 74) & (time_change < datetime.timedelta(minutes=15)):
            time.sleep((datetime.timedelta(minutes=15) - time_change).total_seconds())
            ticker = 0
            time_start = datetime.datetime.now()

        temp = scrape_user_likes(twitter_id)
        temp['twitter_id'] = twitter_id
        output.append(temp)
    return output


# scrape tweets in list
def scrape_all_tweets(twitter_id_list, start_time):
    tweets = []
    for twitter_id in twitter_id_list:
        temp = scrape_user_tweets(twitter_id, start_time)
        temp['twitter_id'] = twitter_id
        tweets.append(temp)
    return tweets


# with the list, figure out what got the most retweets in the last n hours
def most_interactions_except_likes(tweets_data):
    tweets = []
    for user in tweets_data:
        if 'data' in user:
            for tweet in user['data']:
                if 'referenced_tweets' in tweet:
                    for referenced_tweet in tweet['referenced_tweets']:
                        temp = referenced_tweet
                        temp['root_user'] = user['twitter_id']
                        tweets.append(temp)
    df = pd.DataFrame(tweets)
    top = df['id'].value_counts().index.values[0:9]
    output = []
    for tweet_id in top:
        temp = df[df['id'] == tweet_id]
        tweet_info = scrape_tweet(tweet_id)
        output_temp = {
            'tweet_id': tweet_id,
            'tweet_root_user': tweet_info['data']['author_id'],
            'retweeted': 0,
            'quoted': 0,
            'replied_to': 0,
            'total_interactions': len(temp),
            'link': "twitter.com/any_user/status/" + tweet_id
        }
        if 'replied_to' in temp['type'].value_counts():
            output_temp['replied_to'] = temp['type'].value_counts()['replied_to']
        if 'retweeted' in temp['type'].value_counts():
            output_temp['retweeted'] = temp['type'].value_counts()['retweeted']
        if 'quoted' in temp['type'].value_counts():
            output_temp['quoted'] = temp['type'].value_counts()['quoted']
        output.append(output_temp)
    return output


def most_linked_url(tweets_data):
    urls = []
    for user in tweets_data:
        if 'data' in user:
            for tweet in user['data']:
                if 'entities' in tweet:
                    if 'urls' in tweet['entities']:
                        for url in tweet['entities']['urls']:
                            urls.append(url['expanded_url'])
    urls = [i for i in urls if not ('twitter.com' in i)]
    urls_cleaned = []
    for url in urls:
        if ('://amp.' in url) or (('?' in url) and ('tube.com' not in url)):
            if '://amp' in url:
                urls_cleaned.append(url.replace('://amp.', '://'))
            else:
                urls_cleaned.append(url.split('?', 1)[0])
        else:
            urls_cleaned.append(url)
    urls = urls_cleaned
    df = pd.DataFrame(urls)
    urls = df[0].value_counts().index.values[0:9]
    output = []
    for url in urls:
        temp = df[df[0] == url]
        output_temp = {
            'url': url,
            'total_tweets': len(temp)
        }
        output.append(output_temp)
    return output
