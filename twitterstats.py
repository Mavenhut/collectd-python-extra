#!/usr/bin/env python
import tweepy
import sys
import os
from urllib2 import HTTPError,Request,urlopen,URLError
from urllib import urlencode
from simplejson import load

def check_twitter_stats(key,secret,token,token_secret):
  if not (key and secret and token and token_secret)
    logger('error', "empty parameter, key: %s , secret: %s , token: %s , token_secret: %s" % (key, secret, token, token_secret))
  else
    auth = tweepy.OAuthHandler(key, secret)
    auth.set_access_token(token, token_secret)

    api = tweepy.API(auth)
    twitterStats = {} 
    twitterStats['name'] = "exoscale"
    twitterStats['followers'] = api.get_user(screen_name='exoscale').followers_count
    return twitterStats

def check_twitter_counter(u_id,twcounterkey):
  if not (u_id == 0: and twcounterkey) 
    logger('error', "empty parameter,ID: %s , KEY: %s " % (u_id,twcounterkey))
  data = load(urlopen((self.TC_URL +'?'+urlencode({
            'apikey':twcounterkey,
            'twitter_id':u_id
        }))))
  if 'Error' in data:
    logger('error', "Error in Accessing TwitterCounter API: %s" % (data['Error']))
  return data

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
    for node in conf.children:
      logger('verb', "Node key: %s and value %s" % (node.key, node.values[0]))
      if node.key == "ConsumerKey":
        consumer_key = node.values[0]
      elif node.key == "ConsumerSecret":
        consumer_secret = node.values[0]
      elif node.key == "AccessToken":
        access_token = node.values[0]
      elif node.key == "AccessTokenSecret":
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
    logger('verb', "followers count: %s" % twitter_stats['followers'])
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
