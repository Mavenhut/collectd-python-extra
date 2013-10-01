# collectd-cloudstack - cloudstack.py
#
# Author : Antoine Coetsier @ exoscale
# Description : This is a collectd python module to gather stats from cloudstack
# inspired by collectd-haproxy from Michael Leinartas - https://github.com/mleinart/collectd-haproxy

import collectd
import urllib2
import urllib
import json
import hmac
import base64
import hashlib
import re

class BaseClient(object):
    def __init__(self, api, apikey, secret):
        self.api = api
        self.apikey = apikey
        self.secret = secret

    def request(self, command, args):
        args['apikey']   = self.apikey
        args['command']  = command
        args['response'] = 'json'
        
        params=[]
        
        keys = sorted(args.keys())

        for k in keys:
            params.append(k + '=' + urllib.quote_plus(args[k]).replace("+", "%20"))
       
        query = '&'.join(params)

        signature = base64.b64encode(hmac.new(
            self.secret, 
            msg=query.lower(), 
            digestmod=hashlib.sha1
        ).digest())

        query += '&signature=' + urllib.quote_plus(signature)

        response = urllib2.urlopen(self.api + '?' + query)
        decoded = json.loads(response.read())
       
        propertyResponse = command.lower() + 'response'
        if not propertyResponse in decoded:
            if 'errorresponse' in decoded:
                raise RuntimeError("ERROR: " + decoded['errorresponse']['errortext'])
            else:
                raise RuntimeError("ERROR: Unable to parse the response")

        response = decoded[propertyResponse]
        result = re.compile(r"^list(\w+)s").match(command.lower())

        if not result is None:
            type = result.group(1)

            if type in response:
                return response[type]
            else:
                # sometimes, the 's' is kept, as in :
                # { "listasyncjobsresponse" : { "asyncjobs" : [ ... ] } }
                type += 's'
                if type in response:
                    return response[type]

        return response

class Client(BaseClient):
	def listHosts(self, args={}):
		return self.request('listHosts', args)
        
        def listCapabilities(self, args={}):
        	return self.request('listCapabilities', args)
        
        def listCapacity(self, args={}):
        	return self.request('listCapacity', args)
        
        def listSystemVms(self, args={}):
        	return self.request('listSystemVms', args)
        
        def listZones(self, args={}):
        	return self.request('listZones', args)

        def listVirtualMachines(self, args={}):
                return self.request('listVirtualMachines', args)

        def listAccounts(self, args={}):
                            return self.request('listAccounts', args)
        
        
NAME = 'cloudstack'

DEFAULT_API = 'http://localhost:8096/client/api'
DEFAULT_AUTH = False
DEFAULT_APIKEY = ''
DEFAULT_SECRET = ''
VERBOSE_LOGGING = False

METRIC_TYPES = {
  'memoryused': ('h_memory_used', 'memory'),
  'memorytotal': ('h_memory_total', 'memory'),
  'memoryallocated': ('h_memory_allocated', 'memory'),
  'cpuallocated': ('h_cpu_allocated', 'percent'),
  'activeviewersessions': ('console_active_sessions', 'current'),
  'hostscount': ('hosts_count', 'current'),
  'zonescount': ('zones_count', 'current'),
  'zonepublicipallocated': ('z_public_ip_allocated', 'current'),
  'zonepubliciptotal': ('z_public_ip_total', 'current'),
  'zonepublicippercent': ('z_public_ip_percent', 'percent'),
  'zonevmtotal': ('z_vm_total', 'current'),
  'zonevmtotalrunning': ('z_vm_total_running', 'current'),
  'zonevmtotalstopped': ('z_vm_total_stopped', 'current'),
  'zonevmtotalstarting': ('z_vm_total_starting', 'current'),
  'zonevmtotalstopping': ('z_vm_total_stopping', 'current'),
  'disksizetotal': ('h_disk_total', 'bytes'),
  'accountscount': ('g_accounts_total', 'current'),
  'accountenabled': ('g_accounts_total_enabled', 'current'),
  'accountdisabled': ('g_accounts_total_disabled', 'current')
 
}

METRIC_DELIM = '.'

hypervisors = []

def get_stats():
  stats = dict()
  
  logger('verb', "get_stats calls API %s KEY %s SECRET %s" % (API_MONITORS, APIKEY_MONITORS, SECRET_MONITORS))
  cloudstack = Client(API_MONITORS, APIKEY_MONITORS, SECRET_MONITORS)	
  try:
 	hypervisors = cloudstack.listHosts({
                        'type': 'Routing',
                        'state': 'Up'
                }) 
  except:
     	logger('warn', "status err Unable to connect to CloudStack URL at %s for Hosts" % API_MONITORS)
  for  h in hypervisors:
	metricnameMemUsed = METRIC_DELIM.join([ h['name'].lower(), h['podname'].lower(), re.sub(r"\s+", '-', h['zonename'].lower()), 'memoryused' ])
	metricnameMemTotal = METRIC_DELIM.join([ h['name'].lower(), h['podname'].lower(), re.sub(r"\s+", '-', h['zonename'].lower()), 'memorytotal' ])
	metricnameMemAlloc = METRIC_DELIM.join([ h['name'].lower(), h['podname'].lower(), re.sub(r"\s+", '-', h['zonename'].lower()), 'memoryallocated' ])
	#metricnameDiskAlloc = METRIC_DELIM.join([ h['name'].lower(), h['podname'].lower(), re.sub(r"\s+", '-', h['zonename'].lower()), 'disksizeallocated' ])
	#metricnameDiskTotal = METRIC_DELIM.join([ h['name'].lower(), h['podname'].lower(), re.sub(r"\s+", '-', h['zonename'].lower()), 'disksizetotal' ])
	try:
        	stats[metricnameMemUsed] = h['memoryused'] 
        	stats[metricnameMemTotal] = h['memorytotal'] 
        	stats[metricnameMemAlloc] = h['memoryallocated']
                stats[metricnameCpuAlloc] = h['cpuallocated'] 
  		logger('verb', "readings :  %s memory used %s " % (h['name'], h['memoryused']))
	except (TypeError, ValueError), e:
        	pass

  # collect number of active console sessions
  try:
	systemvms = cloudstack.listSystemVms({
		'systemvmtype': 'consoleproxy'
		})
  except:
     	logger('warn', "status err Unable to connect to CloudStack URL at %s for SystemVms" % API_MONITORS)

  for systemvm in systemvms:
	metricnameSessions = METRIC_DELIM.join([ 'activeviewersessions', systemvm['zonename'].lower(), systemvm['name'].lower(), 'activeviewersessions' ])
	if 'activeviewersessions' in systemvm:
		stats[metricnameSessions] = systemvm['activeviewersessions']

  # collect number of zones, available public ips and VMs
  try:
        zones = cloudstack.listZones({
                'showcapacities': 'true'
                })
  except:
      logger('warn', "status err Unable to connect to CloudStack URL at %s for ListZone" % API_MONITORS)
  for zone in zones:
        metricnameIpAllocated = METRIC_DELIM.join([ 'zonepublicipallocated', zone['name'].lower(),  'zonepublicipallocated' ])
        metricnameIpTotal = METRIC_DELIM.join([ 'zonepubliciptotal', zone['name'].lower(),  'zonepubliciptotal' ])
        metricnameIpAllocatedPercent = METRIC_DELIM.join([ 'zonepublicippercent', zone['name'].lower(),  'zonepublicippercent' ])
        metricnameVmZoneTotalRunning = METRIC_DELIM.join([ 'zonevmtotalrunning', zone['name'].lower(),  'zonevmtotalrunning' ])
        metricnameVmZoneTotalStopped = METRIC_DELIM.join([ 'zonevmtotalstopped', zone['name'].lower(),  'zonevmtotalstopped' ])
        metricnameVmZoneTotalStopping = METRIC_DELIM.join([ 'zonevmtotalstopping', zone['name'].lower(),  'zonevmtotalstopping' ])
        metricnameVmZoneTotalStarting = METRIC_DELIM.join([ 'zonevmtotalstarting', zone['name'].lower(),  'zonevmtotalstarting' ])
        metricnameVmZoneTotal = METRIC_DELIM.join([ 'zonevmtotal', zone['name'].lower(),  'zonevmtotal' ])
        metricnameZonesCount = METRIC_DELIM.join([ 'zonescount',  'zonescount' ])
        metricnameZonesCount = METRIC_DELIM.join([ 'zonescount',  'zonescount' ])


        # collect number of virtual machines 
        try:
            virtualmachines = cloudstack.listVirtualMachines({
                'listall': 'true',
                'details': 'all'
                })
        except:
            logger('warn', "status err Unable to connect to CloudStack URL at %s for ListVms" % API_MONITORS)

        virtualMachineZoneRunningCount = 0
        virtualMachineZoneStoppedCount = 0
        virtualMachineZoneStartingCount = 0
        virtualMachineZoneStoppingCount = 0

        for virtualmachine in virtualmachines:
            if virtualmachine['state'] == 'Running':
                virtualMachineZoneRunningCount = virtualMachineZoneRunningCount + 1
            elif virtualmachine['state'] == 'Stopped':
                virtualMachineZoneStoppedCount = virtualMachineZoneStoppedCount + 1
            elif virtualmachine['state'] == 'Stopping':
                virtualMachineZoneStartingCount = virtualMachineZoneStartingCount + 1
            elif virtualmachine['state'] == 'Starting':
                virtualMachineZoneStoppingCount = virtualMachineZoneStoppingCount + 1

        stats[metricnameVmZoneTotal] = len(virtualmachines)
        stats[metricnameVmZoneTotalRunning] = virtualMachineZoneRunningCount
        stats[metricnameVmZoneTotalStopped] = virtualMachineZoneStoppedCount
        stats[metricnameVmZoneTotalStopping] = virtualMachineZoneStoppingCount
        stats[metricnameVmZoneTotalStarting] = virtualMachineZoneStartingCount


        for capacity in zone['capacity']:
            if capacity['type'] == 8:
                stats[metricnameIpTotal] = capacity['capacitytotal']
                stats[metricnameIpAllocated] = capacity['capacityused']
                stats[metricnameIpAllocatedPercent] = capacity['percentused']

  stats[metricnameZonesCount] = len(zones) 

  # collect accounts
  try:
        accounts = cloudstack.listAccounts({
                'listall': 'true'
                })
  except:
      print("status err Unable to connect to CloudStack URL at %s for ListAccounts")

  metricnameAccountsTotal = METRIC_DELIM.join([ 'accounts',  'accountscount' ])
  metricnameAccountsTotalEnabled = METRIC_DELIM.join([ 'accounts',  'accountenabled' ])
  metricnameAccountsTotalDisabled = METRIC_DELIM.join([ 'accounts',  'accountdisabled' ])
  accountsEnabledCount = 0
  accountsDisabledCount = 0

  for account in accounts:
        if account['state'] == 'enabled':
                accountsEnabledCount = accountsEnabledCount + 1
        elif account['state'] == 'disabled':
                accountsDisabledCount = accountsDisabledCount + 1

  stats[metricnameAccountsTotal] = len(accounts)
  stats[metricnameAccountsTotalEnabled] = accountsEnabledCount
  stats[metricnameAccountsTotalDisabled] = accountsDisabledCount

  
  return stats	

# callback configuration for module
def configure_callback(conf):
  global API_MONITORS, APIKEY_MONITORS, SECRET_MONITORS, AUTH_MONITORS, VERBOSE_LOGGING
  API_MONITORS = '' 
  APIKEY_MONITORS = ''
  SECRET_MONITORS = ''
  AUTH_MONITORS = DEFAULT_AUTH
  VERBOSE_LOGGING = False

  for node in conf.children:
    if node.key == "Api":
      API_MONITORS = node.values[0]
    elif node.key == "ApiKey":
      APIKEY_MONITORS = node.values[0]
    elif node.key == "Secret":
      SECRET_MONITORS = node.values[0]
    elif node.key == "Auth":
      AUTH_MONITORS = node.values[0]
    elif node.key == "Verbose":
      VERBOSE_LOGGING = bool(node.values[0])
    else:
      logger('warn', 'Unknown config key: %s' % node.key)

  if not API_MONITORS:
    API_MONITORS += DEFAULT_API

def read_callback():
  logger('verb', "beginning read_callback")
  info = get_stats()

  if not info:
    logger('warn', "%s: No data received" % NAME)
    return

  for key,value in info.items():
    key_prefix = ''
    key_root = key
    logger('verb', "read_callback key %s" % (key))
    logger('verb', "read_callback value %s" % (value))
    if not value in METRIC_TYPES:
      try:
        key_prefix, key_root = key.rsplit(METRIC_DELIM,1)
      except ValueError, e:
        pass
    if not key_root in METRIC_TYPES:
      continue

    key_root, val_type = METRIC_TYPES[key_root]
    key_name = METRIC_DELIM.join([key_prefix, key_root])
    logger('verb', "key_name %s" % (key_name))
    val = collectd.Values(plugin=NAME, type=val_type)
    val.type_instance = key_name
    val.values = [ value ]
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
# main
collectd.register_config(configure_callback)
collectd.register_read(read_callback)
