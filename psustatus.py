#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Loic Lambiel, exoscale
# This is a collectd python script to get the PSU status using ipmi-sensors (freeipmi-tools package)


import collectd
from subprocess import PIPE, Popen

VERBOSE_LOGGING = False
NAME = "ipmi.psu"
SKIP = 10
RUN = 0


def get_psustatus():
    psuStatus = {}
    logger('verb', "Performing ipmi-sensors query to get psu status")

    try:
        p = Popen(["ipmi-sensors", "-t", "Power_Supply", "--no-header-output"], stdin=PIPE, stdout=PIPE, bufsize=1)
        logger('verb', "ipmitool query done")
    except Exception:
        logger('err', "Failed to query ipmi-sensors. Please ensure it is installed")
        raise

    i = 0
    for lines in p.stdout:
        if "Status" in lines:
            i = i + 1
            matchedline = lines.split("|")
            psuItem = "ps%s_status" % i
            psustatus = matchedline[5].lower()
            if "failure" in psustatus:
                psuState = 1
            elif "lost" in psustatus:
                psuState = 1
            elif "out-of-range" in psustatus:
                psuState = 1
            elif "error" in psustatus:
                psuState = 1
            else:
                psuState = 0

            psuStatus[str(psuItem)] = psuState

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
    global RUN, SKIP
    RUN += 1
    if RUN % SKIP != 1:
        return
    psu_status = get_psustatus()
    val = collectd.Values(plugin=NAME, type="gauge")
    if psu_status:
        for key, value in psu_status.items():
            val.values = [value]
            logger('verb', "psu %s status is: %s" % (key, value))
            val.type_instance = key
            val.type = "gauge"
            val.dispatch()
    else:
        logger('verb', "no psu found")


collectd.register_read(read_callback)
