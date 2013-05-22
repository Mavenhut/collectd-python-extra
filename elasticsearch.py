#!/usr/bin/env python
import sys
import os
import json
import requests
import pprint

def color_to_level(color):
  if color == 'green':
    return 0
  elif color == 'yellow':
    return 1
  elif color == 'red':
    return 2
  else:
    return 3

HEALTH_METRICS = {
  'active_primary_shards': {'type': 'gauge'},
  'active_shards': {'type': 'gauge'},
  'initializing_shards': {'type': 'gauge'},
  'number_of_data_nodes': {'type': 'gauge'},
  'number_of_nodes': {'type': 'gauge'},
  'relocating_shards': {'type': 'gauge'},
  'unassigned_shards': {'type': 'gauge'},
  'timed_out': {'type': 'gauge' },
  'status': { 'type': 'gauge', 'transform': color_to_level }
}

def deep_lookup(struct, path):

  first_key = path[0]
  new_path = path[1:]

  if first_key == '__FIRST__':
    first_key = struct.keys()[0]

  try:
    new_struct = struct[first_key]
  except KeyError:
    return None

  if len(new_path) == 0:
    return new_struct
  else:
    return deep_lookup(new_struct, new_path)

def name_from_path(path):
  new_path = []
  
  for elem in path:
    if elem != '__FIRST__':
      new_path.append(elem)

  return "_".join(new_path)

STATS_METRICS = [
  {'path': [ 'nodes', '__FIRST__', 'http', 'current_open' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'http', 'total_opened' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'cache', 'bloom_size_in_bytes' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'cache', 'field_evictions' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'cache', 'field_size_in_bytes' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'cache', 'filter_count' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'cache', 'filter_evictions' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'cache', 'filter_size_in_bytes' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'cache', 'id_cache_size_in_bytes' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'docs', 'count' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'docs', 'deleted' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'flush', 'total' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'flush', 'total_time_in_millis' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'get', 'current' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'get', 'exists_time_in_millis' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'get', 'exists_total' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'get', 'missing_time_in_millis' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'get', 'missing_total' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'get', 'time_in_millis' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'get', 'total' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'indexing', 'delete_current' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'indexing', 'delete_time_in_millis' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'indexing', 'delete_total' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'indexing', 'index_current' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'indexing', 'index_time_in_millis' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'indexing', 'index_time_in_millis' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'merges', 'current' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'merges', 'current_docs' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'merges', 'current_size_in_bytes' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'merges', 'total' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'merges', 'total_docs' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'merges', 'total_size_in_bytes' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'merges', 'total_time_in_millis' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'refresh', 'total' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'refresh', 'total_time_in_millis' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'search', 'fetch_current' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'search', 'fetch_time_in_millis' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'search', 'fetch_total' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'search', 'query_current' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'search', 'query_time_in_millis' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'search', 'query_total' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'store', 'size_in_bytes' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'indices', 'store', 'throttle_time_in_millis' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'process', 'mem', 'resident_in_bytes' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'process', 'mem', 'share_in_bytes' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'process', 'mem', 'total_virtual_in_bytes' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'process', 'open_file_descriptors' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'transport', 'rx_count' ], 'type': 'counter'},
  {'path': [ 'nodes', '__FIRST__', 'transport', 'rx_size_in_bytes' ], 'type': 'counter'},
  {'path': [ 'nodes', '__FIRST__', 'transport', 'server_open' ], 'type': 'gauge'},
  {'path': [ 'nodes', '__FIRST__', 'transport', 'tx_count' ], 'type': 'counter'},
  {'path': [ 'nodes', '__FIRST__', 'transport', 'tx_size_in_bytes' ], 'type': 'counter'},
]

class Metric:
  def __init__(self, name, type="gauge", metric=0.0):
    self.type = type
    self.metric = metric
    self.name = name

  def __repr__(self):
    return "Metric(%s:%s => %f)" % (self.name, self.type, self.metric)

def check_es_cluster(instance="localhost", cluster='http://localhost:9200'):

  url_stats = "%s/_cluster/nodes/_local/stats?http=true&jvm=true&process=true&transport=true" % cluster
  url_health = "%s/_cluster/health" % cluster

  stats = requests.get(url_stats).json()
  health = requests.get(url_health).json()


  metric_tab = []

  for name, metric_hints in HEALTH_METRICS.items():

    datapoint = health[name]

    if 'transform' in metric_hints:
      transform_function = metric_hints['transform']
      datapoint = transform_function(datapoint)

    metric = Metric(name, type=metric_hints['type'], metric=datapoint)
    metric_tab.append(metric)


  for metric_hints in STATS_METRICS:
    name = name_from_path(metric_hints['path'])
    datapoint = deep_lookup(stats, metric_hints['path'])

    if 'transform' in metric_hints:
      transform_function = metric_hints['transform']
      datapoint = transform_function(datapoint)

    metric = Metric(name, type=metric_hints['type'], metric=datapoint)
    metric_tab.append(metric)

#  pp = pprint.PrettyPrinter()
#  pp.pprint(stats)
#  pp.pprint(health)
#  pp.pprint(metric_tab)

  return metric_tab
  

try:
  import collectd

  NAME = "elasticsearch"

  class ESConfig:
    cluster = "http://localhost:9200"
    instance = "localhost"

  def config_callback(conf):
    for node in conf.children:
      if node.key == 'Instance':
        ESConfig.instance = node.values[0]
      elif node.key == 'Cluster':
        ESConfig.cluster = node.values[0]
      else:
        logger('verb', "unknown config key in elasticsearch module: %s" % node.key)


  def metric_to_val(m):

    if m.metric == None:
      return None

    val = collectd.Values(plugin=NAME, type=m.type)
    val.plugin_instance = ESConfig.instance
    val.values = [ float(m.metric) ]
    val.type_instance = m.name
    return val
    
  def read_callback():

    metrics = check_es_cluster(instance=ESConfig.instance,
                               cluster=ESConfig.cluster)

    for metric in metrics:
      val = metric_to_val(metric)
      if val:
        val.dispatch()

  collectd.register_read(read_callback)
  collectd.register_config(config_callback)

except ImportError:
  ## we're not running inside collectd
  ## it's ok
  pass

if __name__ == "__main__":
  cluster = os.getenv("ES_CLUSTER", 'http://localhost:9200')

  metrics = check_es_cluster(cluster=cluster)
