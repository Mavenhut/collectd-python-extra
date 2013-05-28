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
  global  consumer_key, consumer_secret, access_token, access_token_secret, VERBOSE_LOGGING
  
  NAME = "twitterstats"
  VERBOSE_LOGGING = False
  
  consumer_key = ""
  consumer_secret = ""
  access_token = ""
  access_token_secret = ""

  def config_callback(conf):
    logger('verb', "Node key: %s and value %s" % (node.key, node.values[0]))
    for node in conf.children:
      if node.key == 'ConsumerKey':
        consumer_key = node.values[0]
      elif node.key == 'ConsumerSecret':
        consumer_secret = node.values[0]
      elif node.key == 'AccessToken':
        access_token = node.values[0]
      elif node.key == 'AccessTokenSecret':
        access_token_secret = node.values[0]
      elif node.key == "Verbose":
        VERBOSE_LOGGING = bool(node.values[0])
      else:
        logger('warn', "unknown config key in puppet module: %s" % node.key)
  
  def read_callback():
    logger('verb', "consumer_key: %s" % consumer_key)
    twitter_stats = check_twitter_stats(consumer_key,
                                   consumer_secret,
                                   access_token,
                                   access_token_secret
                                   )
    val = collectd.Values(plugin=NAME, type="gauge")
    val.plugin_instance = twitter_stats['name']
    val.values = [twitter_stats['followers'] ]
    val.type_instance = "followers"
    val.type = "gauge"
    val.dispatch()

  # logging function
  def logger(t, msg):
    if t == 'err':
        collectd.error('%s: %s' % (NAME, msg))
    elif t == 'warn':
        collectd.warning('%s: %s' % (NAME, msg))
    elif t == 'verb':
        if VERBOSE_LOGGING:
            collectd.info('%s: %s' % (NAME, msg))
    else:
        collectd.notice('%s: %s' % (NAME, msg))

  collectd.register_config(config_callback)
  collectd.register_read(read_callback)
    

except ImportError:
  ## we're not running inside collectd
  ## it's ok
  pass

if __name__ == "__main__":
  consumer_Key = sys.argv[1]
  consumer_Secret = sys.argv[2]
  access_Token = sys.argv[3]
  access_Token_Secret= sys.argv[4]
  stats = check_twitter_stats(consumer_Key, consumer_Secret, access_Token, access_Token_Secret)

  print "Twitter followers count of %s: %s" % (stats['name'], stats['followers'])
