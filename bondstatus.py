#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Loic Lambiel, exoscale
#This is a collectd python script to detect bondings status. any MII state other than "up" will be reported as failed


def bond_status(intBondID):
    try:
        strBondPath = "/proc/net/bonding/bond%d" % intBondID
        for line in open(strBondPath).readlines():
            if "MII Status" in line:
                strStatus = line.split(":")
                strStatus = strStatus[1].strip()
                if strStatus != "up":
                    #bond nok
                    intStatus = 1
                    return intStatus,strStatus
                else:
                #bond ok
                    intStatus = 0
        return intStatus,strStatus
    except:
        return

try:
    import collectd

    NAME = "Bonding"
    VERBOSE_LOGGING = True

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
   

    def read_callback():
        i = 0
        for i in range(0, 10):
            intStatus = bond_status(i)
            val = collectd.Values(plugin=NAME, type="gauge")
            #val.plugin_instance = hostbill_stats['name']
            val.values = intStatus
            logger('verb', "Bond%s status is: %d" % i,intStatus)
            val.type_instance = "Bond%s" % i
            val.type = "gauge"
            val.dispatch()

    collectd.register_read(read_callback) 


except ImportError:
    ## we're not running inside collectd
    ## it's ok

    i = 0
    for i in range(0, 10):
        try:
            intStatus,strStatus = bond_status(i)
            if intStatus == 0:
                print "bond%d is up" % i
            else:
                print "bond%d error:%s" % i,strStatus
        except:
            continue
