#!/usr/bin/env python
import redis
import sys
import os

def check_redis_length(queue_name, port=6379):
  redis_client = redis.Redis(port=port)
  return redis_client.llen(queue_name)

class RedisLengthConfig:
  def __init__(self):
    self.queues = []
    self.port = 6379

config = RedisLengthConfig()

try:
  import collectd


  def logger(t, msg):
    if t == 'err':
      collectd.error('%s: %s' % (NAME, msg))
    elif t == 'warn':
      collectd.warning('%s: %s' % (NAME, msg))
    elif t == 'info':
      collectd.info('%s: %s' % (NAME, msg))
    else:
      collectd.notice('%s: %s' % (NAME, msg))

  NAME = "redislen"


  def config_callback(conf):
    for node in conf.children:
      if node.key == 'QueueName':
        for v in node.values:
          config.queues.append(v)
      elif node.key == 'Port':
        config.port = int(node.values[0])
      else:
        logger('info', "unknown config key in puppet module: %s" % node.key)

  def read_callback():
    for v in config.queues:
      queue_len = check_redis_length(v,port=config.port)

      val = collectd.Values(plugin=NAME, type="gauge")
      val.plugin_instance = v
      val.values = [ float(queue_len) ]
      val.type = "gauge"
      val.dispatch()

  collectd.register_config(config_callback)
  collectd.register_read(read_callback)

except ImportError:
  ## we're not running inside collectd
  ## it's ok
  pass

if __name__ == "__main__":
  port = int(os.getenv("REDIS_PORT", 6379))
  queue_name = sys.argv[1]
  queue_len = check_redis_length(queue_name, port=port)

  print "length of %s: %d" % (queue_name, queue_len)
