#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Loic Lambiel, exoscale
#This is a collectd python script to get the PSU status using ipmitool



def get_psustatus():
    psuStatus = {}
    try:
        logger('verb', "Performing ipmitool query to get psu status")
    except:
        pass
    try:
        p = Popen(["ipmitool", "sensor"], stdin=PIPE, stdout=PIPE, bufsize=1)
        try:
            logger('verb', "ipmitool query done")
        except:
            pass
    except:
        try:
            logger('err', "Failed to query ipmitool. Please ensure it is installed")
        except:
            pass

        raise

    for lines in p.stdout:
        if "PS" in lines:
            matchedline = lines.split("|")
            psuItem = matchedline[0].lower()
            psuItem = psuItem.replace(" ", "_")
            while psuItem.endswith('_'):
                psuItem = psuitem[:-1]
            psuState = matchedline[1].split("x")[1]
 
            psuStatus['psuItem'] = psuItem
            psuStatus['psuState'] = psuState

    time.sleep(SLEEPTIME)        
    return psuStatus

try:
    import collectd
    import time
    from subprocess import PIPE, Popen
    global SLEEPTIME
    
    SLEEPTIME = 300
    VERBOSE_LOGGING = False

    NAME = "ipmi"

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
        psu_status = get_psustatus()
        val = collectd.Values(plugin=NAME, type="gauge")
        if psu_status:
            for key, value in psu_status.items():
                val.values = [value]
                logger('verb', "psu %s status is: %s" % (key, value))
                val.type_instance =  key
                val.type = "gauge"
                val.dispatch()
        else:
            logger('verb', "no psu found")

    collectd.register_read(read_callback) 


except ImportError:
    ## we're not running inside collectd
    ## it's ok

    psu_status = get_psustatus()
    if psu_status:
        for key, value in psu_status.items():
            print "%s status is %s" % (key, value)
    else:
        print "no psu found"
