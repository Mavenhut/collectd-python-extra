#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Author: Loic Lambiel, exoscale
#This is a collectd python script to get the PSU status using ipmi-sensors (freeipmi-tools package)



import collectd
import time
from subprocess import PIPE, Popen
global SLEEPTIME

SLEEPTIME = 120
VERBOSE_LOGGING = False
NAME = "ipmi.psu"

def get_psustatus():
    psuStatus = {}
    logger('verb', "Performing ipmi-sensors query to get psu status")
    
    try:
        p = Popen(["ipmi-sensors", "-t", "Power_Supply", "--no-header-output"], stdin=PIPE, stdout=PIPE, bufsize=1)
        logger('verb', "ipmitool query done")
    except:
        logger('err', "Failed to query ipmi-sensors. Please ensure it is installed")
        raise

    for lines in p.stdout:
        if "Status" in lines:
            matchedline = lines.split("|")
            psuitem = matchedline[1].lower()
            psuitem = psuitem.replace(" ", "_")
            psuitem = psuitem[1:]
            while psuitem.endswith('_'):
                psuitem = psuitem[:-1]
            psustatus = matchedline[5]
            if "Presence detected" in psustatus:
                psustatus = 0
            else:
                psustatus = 1

    time.sleep(SLEEPTIME)        
    return psuStatus



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


