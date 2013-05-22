#!/usr/bin/env python
import redis
import sys
import os

def check_redis_length(queue_name, port=6379):
  redis_client = redis.Redis(port=port)
  return redis_client.llen(queue_name)

try:
  import collectd

  NAME = "redislen"

  class RedisLengthConfig:
    queue_name = "logstash"
    port = 6379

  def config_callback(conf):
    for node in conf.children:
      if node.key == 'QueueName':
        RedisLengthConfig.queue_name = node.values[0]
      elif node.key == 'Port':
        RedisLengthConfig.port = int(node.values[0])
      else:
        logger('verb', "unknown config key in puppet module: %s" % node.key)

  def read_callback():

    queue_len = check_redis_length(RedisLengthConfig.queue_name,
                                   port=RedisLengthConfig.port)
    val = collectd.Values(plugin=NAME, type="gauge")
    val.plugin_instance = RedisLengthConfig.queue_name
    val.values = [ float(queue_len) ]
    val.type = "gauge"
    val.dispatch()

  collectd.register_read(read_callback)
  collectd.register_config(config_callback)
    

except ImportError:
  ## we're not running inside collectd
  ## it's ok
  pass

if __name__ == "__main__":
  port = int(os.getenv("REDIS_PORT", 6379))
  queue_name = sys.argv[1]
  queue_len = check_redis_length(queue_name, port=port)

  print "length of %s: %d" % (queue_name, queue_len)
