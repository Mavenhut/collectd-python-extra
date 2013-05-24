#!/usr/bin/env python
import tweepy
import sys
import os

def check_twitter_stats(consumer_key,consumer_secret,access_token,access_token_secret):
  auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_token_secret)

  api = tweepy.API(auth)
  twitterStats = {} 
  twitterStats['name'] = api.me().name
  twitterStats['followers'] = api.me().followers_count
  return twitterStats

try:
  import collectd

  NAME = "twitterstats"

  class TwitterStatsConfig:
    TwitterStatsConfig.consumer_key = "key"
    TwitterStatsConfig.consumer_secret = "secret"
    TwitterStatsConfig.access_token = "token"
    TwitterStatsConfig.consumer_key = "token secret"

  def config_callback(conf):
    for node in conf.children:
      if node.key == 'ConsumerKey':
        TwitterStatsConfig.consumer_key = node.values[0]
      elif node.key == 'ConsumerSecret':
        TwitterStatsConfig.consumer_secret = node.values[0]
      elif node.key == 'AccessToken':
        TwitterStatsConfig.access_token = node.values[0]
      elif node.key == 'AccessTokenSecret':
        TwitterStatsConfig.access_token_secret = node.values[0]
      else:
        logger('verb', "unknown config key in puppet module: %s" % node.key)

  def read_callback():

    twitter_stats = check_twitter_stats(consumer_key=TwitterStatsConfig.consumer_key,
                                   consumer_secret=TwitterStatsConfig.consumer_secret,
                                   access_token=TwitterStatsConfig.access_token,
                                   access_token_secret=TwitterStatsConfig.access_token_secret)
    val = collectd.Values(plugin=NAME, type="counter")
    val.plugin_instance = twitter_stats['name']
    val.values = [twitter_stats['followers'] ]
    val.type = "counter"
    val.dispatch()

  collectd.register_read(read_callback)
  collectd.register_config(config_callback)
    

except ImportError:
  ## we're not running inside collectd
  ## it's ok
  pass

if __name__ == "__main__":
  consumer_key = sys.argv[1]
  consumer_secret = sys.argv[2]
  access_token = sys.argv[3]
  access_token_secret= sys.argv[4]
  stats = check_twitter_stats(consumer_key, consumer_secret, access_token, access_token_secret)

  print "Twitter followers count of %s: %s" % (stats['name'], stats['followers'])
