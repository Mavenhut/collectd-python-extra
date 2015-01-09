#!/usr/bin/env python
import os
import requests


def merge(one, two):
    cp = one.copy()
    cp.udpate(two)
    return cp


def color_to_level(color):
    return {
        'green': 0,
        'yellow': 1,
        'red': 2
    }.get(color, 3)

gauge = {'type': 'gauge'}

health_metrics = {
    'active_primary_shards': gauge,
    'active_shards': gauge,
    'initializing_shards': gauge,
    'number_of_data_nodes': gauge,
    'number_of_nodes': gauge,
    'relocating_shards': gauge,
    'unassigned_shards': gauge,
    'timed_out': merge(gauge, {'transform': int}),
    'status': merge(gauge, {'transform': color_to_level}),
}

stats_gauges = [
    'breakers.fielddata.estimated_size_in_bytes',
    'breakers.fielddata.limit_size_in_bytes',
    'breakers.fielddata.tripped',
    'breakers.fielddata.overhead',
    'breakers.parent.estimated_size_in_bytes',
    'breakers.parent.limit_size_in_bytes',
    'breakers.parent.tripped',
    'breakers.parent.overhead',
    'breakers.request.estimated_size_in_bytes',
    'breakers.request.limit_size_in_bytes',
    'breakers.request.tripped',
    'breakers.request.overhead',

    'http.current_open',

    'indices.query_cache.evictions',
    'indices.query_cache.miss_count',
    'indices.query_cache.memory_size_in_bytes',
    'indices.query_cache.hit_count',
    'indices.docs.count',
    'indices.docs.deleted',
    'indices.search.open_contexts',
    'indices.search.fetch_current',
    'indices.search.query_current',
    'indices.translog.operations',
    'indices.translog.size_in_bytes',
    'indices.flush.total',
    'indices.segments.version_map_memory_in_bytes',
    'indices.segments.index_writer_memory_in_bytes',
    'indices.segments.fixed_bit_set_memory_in_bytes',
    'indices.segments.memory_in_bytes',
    'indices.segments.count',
    'indices.segments.index_writer_max_memory_in_bytes',
    'indices.suggest.current',
    'indices.id_cache.memory_size_in_bytes',
    'indices.fielddata.evictions',
    'indices.fielddata.memory_size_in_bytes',
    'indices.store.size_in_bytes',
    'indices.warmer.current',
    'indices.filter_cache.evictions',
    'indices.filter_cache.memory_size_in_bytes',
    'indices.get.current',
    'indices.completion.size_in_bytes',
    'indices.indexing.delete_current',
    'indices.indexing.is_throttled',
    'indices.indexing.index_current',
    'indices.merges.current_docs',
    'indices.merges.total_docs',
    'indices.merges.total_size_in_bytes',
    'indices.merges.current',
    'indices.merges.current_size_in_bytes',
    'indices.percolate.queries',
    'indices.percolate.memory_size_in_bytes',
    'indices.percolate.current',

    'process.mem.resident_in_bytes',
    'process.mem.share_in_bytes',
    'process.mem.total_virtual_in_bytes',
    'process.open_file_descriptors',
    'process.cpu.total_in_millis',
    'process.cpu.user_in_millis',
    'process.cpu.sys_in_millis',
    'process.cpu.percent',

    'transport.server_open',
]

stats_counters = [
    'http.total_opened',
    'transport.rx_count',
    'transport.rx_size_in_bytes',
    'transport.tx_count',
    'transport.tx_size_in_bytes',
    'indices.flush.total_time_in_millis',
    'indices.refresh.total_time_in_millis',
    'indices.warmer.total_time_in_millis',
    'indices.merges.total_time_in_millis',
    'indices.search.query_time_in_millis',
    'indices.search.fetch_time_in_millis',
    'indices.suggest.time_in_millis',
    'indices.store.throttle_time_in_millis',
    'indices.get.exists_time_in_millis',
    'indices.get.time_in_millis',
    'indices.get.missing_time_in_millis',
    'indices.indexing.delete_time_in_millis',
    'indices.indexing.throttle_time_in_millis',
    'indices.indexing.index_time_in_millis',
    'indices.percolate.time_in_millis',
    'indices.get.total',
    'indices.refresh.total',
    'indices.suggest.total',
    'indices.warmer.total',
    'indices.merges.total',
    'indices.percolate.total',
    'indices.search.query_total',
    'indices.search.fetch_total',
    'indices.get.exists_total',
    'indices.get.missing_total',
    'indices.indexing.delete_total',
    'indices.indexing.index_total',
    'indices.indexing.noop_update_total',
]


def lookup(data, selector):
    keys = selector.split('.')
    value = data
    while keys:
        value = value[keys.pop(0)]
    return value


class Metric:
    __slots__ = ('type', 'metric', 'name')

    def __init__(self, name, type="gauge", metric=0.0):
        self.type = type
        self.metric = metric
        self.name = name

    def __repr__(self):
        return "Metric(%s:%s => %f)" % (self.name, self.type, self.metric)


def check_es_cluster(instance="localhost", cluster='http://localhost:9200'):
    stats_url = ('{0}/_nodes/_local/stats/'
                 'http,indices,process,transport,breaker').format(cluster)
    health_url = '{0}/_cluster/health'.format(cluster)

    stats = requests.get(stats_url).json()
    health = requests.get(health_url).json()

    metrics = []

    for name, metric in health_metrics.items():
        datapoint = health[name]

        if 'transform' in metric:
            datapoint = metric['transform'](datapoint)

        metrics.append(Metric(name, type=metric['type'], metric=datapoint))

    for metric in stats_gauges:
        datapoint = lookup(stats, metric)
        metrics.append(Metric(metric, metric=datapoint))

    for metric in stats_counters:
        datapoint = lookup(stats, metric)
        metrics.append(Metric(metric, type='counter', metric=datapoint))

    return metrics


try:
    import collectd

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

    def read_callback():
        metrics = check_es_cluster(instance=ESConfig.instance,
                                   cluster=ESConfig.cluster)

        for metric in metrics:
            if metric.metric is None:
                continue

            val = collectd.Values(plugin='elasticsearch', type=metric.type)
            val.plugin_instance = ESConfig.instance
            val.values = [float(metric.metric)]
            val.type_instance = metric.name
            val.dispatch()

    collectd.register_read(read_callback)
    collectd.register_config(config_callback)
except ImportError:
    # we're not running inside collectd
    # it's ok
    pass

if __name__ == "__main__":
    cluster = os.getenv("ES_CLUSTER", 'http://localhost:9200')
    metrics = check_es_cluster(cluster=cluster)
