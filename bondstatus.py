#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Loic Lambiel, exoscale
#This is a collectd python script to detect bondings status. any MII state other than "up" will be reported as failed


global NAME = "Bondstatus"

def check_bond_status(intBondID):
    try:
        Bondstatus = {}
        strBondPath = "/proc/net/bonding/bond%d" % intBondID
        for line in open(strBondPath).readlines():
            if "MII Status" in line:
                strState = line.split(":")
                strState = strState[1].strip()
                if strState != "up":
                    #bond nok
                    intState = 1
                    str(Bondstatus['intState')] = intState
                    str(Bondstatus['strState']) = strState
                    return Bondstatus
                else:
                #bond ok
                    intState = 0
                    str(Bondstatus['intState']) = intState
                    str(Bondstatus['strState']) = strState
        return Bondstatus
    except:
        return

try:
    import collectd

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
            bond_status = check_bond_status(i)
            val = collectd.Values(plugin=NAME, type="gauge")
            #val.plugin_instance = bond_status['name']
            val.values = [bond_status['intState'] ]
            logger('verb', "Bond%s status is: %s" % (i,bond_status['intState']))
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
            bond_status = check_bond_status(i)
            if bond_status['intState'] == 0:
                print "bond%d is up" % i
            else:
                print "bond%d error:%s" % (i,bond_status['strState'])
        except:
            continue
