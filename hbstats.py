#!/usr/bin/python

# collectd-hostbill - hbstats.py
#
# Author : Loic Lambiel @ exoscale
# Description : This is a collectd python module to gather stats from hostbill


import MySQLdb
import sys
from datetime import date, timedelta



def check_hosbill_status(dbhost,user,pwd,database):
  if not (dbhost and user and pwd and database):
    logger('error', "empty parameter, dbhost: %s , user: %s , pwd: %s , database: %s" % (dbhost,user,pwd,database))
    sys.exit(1)
  try:
    #date tommorrow and yesterday range
    d1=date.today()+timedelta(days=1)
    d2=date.today()-timedelta(days=1)
    QUERYFAILEDEMAIL="SELECT * FROM hostbill.hb_email_log where status ='0' and date BETWEEN '%s' AND '%s'" % (d2,d1)
    con = MySQLdb.connect(dbhost, user, pwd, database)
    cursor = con.cursor()
    cursor.execute(QUERYFAILEDEMAIL)
    querycount = cursor.rowcount
    HbStats = {}
    HbStats['name'] = 'exoscale'
    HbStats['nbfailedsentmails'] = querycount
    return HbStats


  except ValueError as e:
    logger('error', "Error during mysql query: %s" % e)
    sys.exit(1)

  finally:
    if con:
      con.close()


try:
  import collectd

  NAME = "hbstats"
  VERBOSE_LOGGING = False

  dbhost = ""
  user = ""
  pwd = ""
  database = ""

  def config_callback(conf):
    global  dbhost, user, pwd, database, VERBOSE_LOGGING
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
    hostbill_stats = check_hosbill_status(dbhost,user,pwd,database)
    val = collectd.Values(plugin=NAME, type="gauge")
    val.plugin_instance = hostbill_stats['name']
    val.values = [hostbill_stats['nbfailedsentmails'] ]
    logger('verb', "Nb of failed sent emails: %s" % hostbill_stats['nbfailedsentmails'])
    val.type_instance = "nb-failed-sent-emails"
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
  ## we're not running inside collectd
  ## it's ok
  pass

if __name__ == "__main__":
  dbhost = sys.argv[1]
  user = sys.argv[2]
  pwd = sys.argv[3]
  database= sys.argv[4]
  hostbill_stats = check_hosbill_status(dbhost,user,pwd,database)

  print "The number of failed sent emails is %s" % (hostbill_stats['nbfailedsentmails'])

