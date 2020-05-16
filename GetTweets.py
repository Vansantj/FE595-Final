# -*- coding: utf-8 -*-
"""
Created on Wed May 13 21:01:31 2020

@author: jvan1
"""
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
def extractTweet(tweet):
    tweet = tweet.split('replies')[0].split('reply')[0]
    find_last_n = tweet[::-1].find('\n')
    tweet = tweet[::-1][find_last_n:][::-1]
    tweet=tweet.replace('\n',' ')
    if 'pic.twitter.com' in tweet:
        tweet = tweet.split('pic.twitter.com')[0]
    elif 'twitter.com' in tweet:
        tweet = tweet.split('twitter.com')[0]
    if 'http' in tweet:
        tweet = tweet.split('http')[0]
    if 'Embed Tweet' in tweet:
        tweet = tweet.split('Embed Tweet')[-1]
    tweet = tweet.lstrip('\n').rstrip('\n').lstrip(' ').rstrip(' ')
    re.sub(r'[^a-zA-Z0-9 ]','',tweet.replace('-',' '))
    if 'Follow' in tweet or 'Unfollow' in tweet:
        return ''
    return tweet
def extractAccount(tweet):
    tweet = tweet.split('@')[1].strip(' ')
    first_n = tweet.find('\n')
    tweet = tweet[0:first_n]
#    tweet=tweet.replace('\n','')
#    if 'pic.twitter.com' in tweet:
#        tweet = tweet.split('pic.twitter.com')[0]
#    elif 'twitter.com' in tweet:
#        tweet = tweet.split('twitter.com')[0]
#    if 'http' in tweet:
#        tweet = tweet.split('http')[0]
    return tweet
def extractReply(tweet):
    output_accounts = []
    if len(tweet.split('@'))>2:
        accounts_to_get = tweet.split('@')[2:]
        for tweet in accounts_to_get:
            tweet = tweet.strip(' ')
        
            first_n = tweet.find('\n')
            if first_n==-1:
                first_n = len(tweet)
            tweet = tweet[0:first_n]
            tweet = tweet.split(' ')[0]
            if 'pic.twitter.com' in tweet:
                tweet = tweet.split('pic.twitter.com')[0]
            elif 'twitter.com' in tweet:
                tweet = tweet.split('twitter.com')[0]
            if 'http' in tweet:
                tweet = tweet.split('http')[0]
            tweet = re.sub(r'[^a-zA-Z0-9 ]','',tweet.replace('-',' '))
    #    tweet=tweet.replace('\n','')
    #    if 'pic.twitter.com' in tweet:
    #        tweet = tweet.split('pic.twitter.com')[0]
    #    elif 'twitter.com' in tweet:
    #        tweet = tweet.split('twitter.com')[0]
    #    if 'http' in tweet:
    #        tweet = tweet.split('http')[0]
            output_accounts.append(tweet)
        return output_accounts
    else:
        tweet = tweet.split('@')[1].strip(' ')
        first_n = tweet.find('\n')
        tweet = tweet[0:first_n]
        output_accounts.append(tweet)
    #    tweet=tweet.replace('\n','')
    #    if 'pic.twitter.com' in tweet:
    #        tweet = tweet.split('pic.twitter.com')[0]
    #    elif 'twitter.com' in tweet:
    #        tweet = tweet.split('twitter.com')[0]
    #    if 'http' in tweet:
    #        tweet = tweet.split('http')[0]
        return output_accounts
def searchAccounts(account_list,tweet_list,account_set):
    new_accounts = []
    for i in range(0,len(account_list)):
        print(account_list[i])
        response = requests.get('https://twitter.com/'+account_list[i])
        soup = BeautifulSoup(response.text,'lxml')
        tweets = soup.findAll('li',{"class":'js-stream-item'})
        
        for tweet in tweets:
            tweet_list.append(extractTweet(tweet.text))
            new_accounts.append(extractAccount(tweet.text))
        response = requests.get('https://twitter.com/'+account_list[i]+'/with_replies')
        tweets = soup.findAll('li',{"class":'js-stream-item'})
        for tweet in tweets:
            tweet_list.append(extractTweet(tweet.text))
            new_accounts = new_accounts+extractReply(tweet.text)
        if i%100==0:
            print('Saving Tweets')
            pd.DataFrame({'Tweets':tweet_list}).drop_duplicates().to_csv('Tweets.csv')
    new_accounts = list(set([x for x in new_accounts if x not in account_set]))
    if len(new_accounts)>0:
        account_set = list(set(account_set+new_accounts))
        print('Saving Accounts + Tweets')
        pd.DataFrame({'Accounts':account_set}).to_csv('Account List.csv')
        pd.DataFrame({'Tweets':tweet_list}).drop_duplicates().to_csv('Tweets.csv')
        tweet_list, account_set = searchAccounts(new_accounts,tweet_list,account_set)
          
    return tweet_list, account_set
def getNewTweets():
    new_accounts = []
    try:
        tweet_list_df = pd.read_csv('Tweets.csv') 
        tweet_list = list(tweet_list_df['Tweets'].values)
    except:
        tweet_list = []
    try:
        account_set_df = pd.read_csv('Account List.csv')
        account_set = list(account_set_df['Accounts'].values)
        account_set = [x for x in account_set if not pd.isna(x)]
        account_set.reverse()
    except:
        account_set = ['realDonaldTrump']
    
    tweet_list, account_set = searchAccounts(account_set,tweet_list,account_set)
    pd.DataFrame({'Tweets':list(tweet_list_df['Tweets'].values)+tweet_list}).drop_duplicates().to_csv('Tweets.csv')

if __name__=='__main__':
    getNewTweets()