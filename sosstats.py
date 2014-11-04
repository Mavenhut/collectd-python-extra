#!/usr/bin/python

# collectd-pithoscassandra - sosstats.py
#
# Author : Loic Lambiel @ exoscale
# Description : This is a collectd python module to gather some metrics from pithos - cassandra (exoscale SOS)


from __future__ import division
from cassandra.cluster import Cluster
import sys
import collectd
import time

SLEEPTIME = 300

def get_stats(nodes):
    if not (nodes):
        logger('error', "empty parameter, nodes: %s" % (nodes))
        sys.exit(1)
    try:
        logger('verb', "Connecting to cluster")
        cluster = Cluster([nodes])

        session = cluster.connect('storage')

        totalobjectsize = 0
        nbobjects = 0
        nbbuckets = 0
        logger('verb', "Querying nb of buckets")

        query = session.execute('SELECT COUNT (*)  FROM bucketstore.bucket')

        for i in query:
            nbbuckets = i.count

        logger('verb', "Querying objects + count")

        query = session.execute('SELECT size FROM metastore.object')

        for i in query:
            totalobjectsize = totalobjectsize + i.size
            nbobjects = nbobjects + 1
        
        totalobjectsize = totalobjectsize / 1073741824
        stats = {}
        stats['totalobjectsize'] = totalobjectsize
        stats['nbobjects'] = nbobjects
        stats['nbbuckets'] = nbbuckets
        return stats


    except ValueError as e:
        logger('error', "Error during cassandra query: %s" % e)
        sys.exit(1)

    finally:
        time.sleep(SLEEPTIME)




NAME = "pithos-sos"
VERBOSE_LOGGING = True

nodes = ""

def config_callback(conf):
    global  nodes, VERBOSE_LOGGING
    for node in conf.children:
        logger('verb', "Node key: %s and value %s" % (node.key, node.values[0]))
        if node.key == "nodes":
            nodes = node.values[0]
        elif node.key == "Verbose":
            VERBOSE_LOGGING = bool(node.values[0])
        else:
            logger('warn', "unknown config key in puppet module: %s" % node.key)

def read_callback():
    sos_stats = get_stats(nodes)
    val = collectd.Values(plugin=NAME, type="gauge")
    val.values = [sos_stats['totalobjectsize'] ]
    logger('verb', "Total objects size %s" % sos_stats['totalobjectsize'])
    val.type_instance = "total-objects-sizeGB"
    val.type = "gauge"
    val.dispatch()

    val = collectd.Values(plugin=NAME, type="gauge")
    val.values = [sos_stats['nbobjects'] ]
    logger('verb', "Total nb objects %s" % sos_stats['nbobjects'])
    val.type_instance = "total-objects-nb"
    val.type = "gauge"
    val.dispatch()

    val = collectd.Values(plugin=NAME, type="gauge")
    val.values = [sos_stats['nbbuckets'] ]
    logger('verb', "Total nb Buckets %s" % sos_stats['nbbuckets'])
    val.type_instance = "total-buckets-nb"
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

