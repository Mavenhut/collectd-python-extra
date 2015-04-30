#!/usr/bin/python

# collectd-cloudstack - asynjosbsstats.py
#
# Author : Loic Lambiel @ exoscale
# Description : This is a collectd python module to gather the async jobs in cloudstack (from database)


import MySQLdb
import sys
import time

SLEEPTIME = 58


def get_asyncjobs(dbhost, user, pwd, database):
    if not (dbhost and user and pwd and database):
        logger('error', "empty parameter, dbhost: %s , user: %s , pwd: %s , database: %s" % (dbhost, user, pwd, database))
        sys.exit(1)
    try:
        CSStats = {}
        con = MySQLdb.connect(dbhost, user, pwd, database)
        # Query running jobs
        QUERYRUNNINGASYNCJOBS = "SELECT id FROM cloud.async_job WHERE job_status = 0 and instance_type not like 'Thread';"
        QUERYALLJOBS = "SELECT id FROM cloud.async_job;"
        cursor = con.cursor()
        cursor.execute(QUERYRUNNINGASYNCJOBS)
        querycount = cursor.rowcount
        CSStats['nbasyncjobsrunning'] = querycount
        # Query failed jobs
        QUERYFAILEDJOBS = "SELECT id FROM cloud.async_job WHERE job_status = 2;"
        cursor = con.cursor()
        cursor.execute(QUERYFAILEDJOBS)
        querycount = cursor.rowcount
        CSStats['nbasyncjobsfailed'] = querycount
        # Query all jobs
        QUERYALLJOBS = "SELECT id FROM cloud.async_job;"
        cursor = con.cursor()
        cursor.execute(QUERYALLJOBS)
        querycount = cursor.rowcount
        CSStats['nbasyncjobsall'] = querycount
        return CSStats

    except ValueError as e:
        logger('error', "Error during mysql query: %s" % e)
        sys.exit(1)

    finally:
        if con:
            con.close()
            time.sleep(SLEEPTIME)


try:
    import collectd

    NAME = "cloudstack"
    VERBOSE_LOGGING = False

    dbhost = ""
    user = ""
    pwd = ""
    database = ""

    def config_callback(conf):
        global dbhost, user, pwd, database, VERBOSE_LOGGING
        for node in conf.children:
            logger('verb', "Node key: %s and value %s" % (node.key, node.values[0]))
            if node.key == "DbHost":
                dbhost = node.values[0]
            elif node.key == "User":
                user = node.values[0]
            elif node.key == "Pwd":
                pwd = node.values[0]
            elif node.key == "Database":
                database = node.values[0]
            elif node.key == "Verbose":
                VERBOSE_LOGGING = bool(node.values[0])
            else:
                logger('warn', "unknown config key in puppet module: %s" % node.key)

    def read_callback():
        cs_stats = get_asyncjobs(dbhost, user, pwd, database)
        # running jobs
        val = collectd.Values(plugin=NAME, type="gauge")
        val.values = [cs_stats['nbasyncjobsrunning']]
        logger('verb', "Nb of running async jobs: %s" % cs_stats['nbasyncjobsrunning'])
        val.type_instance = "async-jobs-running"
        val.type = "gauge"
        val.dispatch()
        # failed jobs
        val = collectd.Values(plugin=NAME, type="gauge")
        val.values = [cs_stats['nbasyncjobsfailed']]
        logger('verb', "Nb of failed async jobs: %s" % cs_stats['nbasyncjobsfailed'])
        val.type_instance = "async-jobs-failed"
        val.type = "gauge"
        val.dispatch()
        # all jobs
        val = collectd.Values(plugin=NAME, type="gauge")
        val.values = [cs_stats['nbasyncjobsall']]
        logger('verb', "Nb of all async jobs: %s" % cs_stats['nbasyncjobsall'])
        val.type_instance = "async-jobs-all"
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
    # we're not running inside collectd
    # it's ok
    pass

    if __name__ == "__main__":
        dbhost = sys.argv[1]
        user = sys.argv[2]
        pwd = sys.argv[3]
        database = sys.argv[4]
        cs_stats = get_asyncjobs(dbhost, user, pwd, database)

        print "The number of running async jobs is %s" % (cs_stats['nbasyncjobsrunning'])
        print "The number of failed async jobs is %s" % (cs_stats['nbasyncjobsfailed'])
        print "The number of all async jobs is %s" % (cs_stats['nbasyncjobsall'])
