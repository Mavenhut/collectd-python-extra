# collectd-cloudstack - cloudstack.py
#
# Author : Loic Lambiel @ exoscale
# Description : This is a collectd python module to gather stats from Vmware vcenters

import collectd
from pysphere import VIServer
        
        
        
NAME = 'Vcenter'

DEFAULT_VCENTERLIST = ''
DEFAULT_USERNAME = ''
DEFAULT_PASSWORD = ''
VERBOSE_LOGGING = False

METRIC_TYPES = {
    'datacenters': ('datacenters', 'current'),
    'clusters': ('clusters', 'current'),
    'hosts': ('hosts', 'current'),
    'runningVMS': ('vm_running', 'current'),
    'stoppedVMS': ('vm_stopped', 'current'),
    'totalVM': ('vm_stopped', 'current'),
    'zonerunningVMS': ('vm_running', 'current'),
    'zonestoppedVMS': ('vm_stopped', 'current'),
    'zonetotalVM': ('vm_stopped', 'current'),
    'datacenterClusters': ('d_clusters', 'current'),
    'datacenterHosts': ('d_hosts', 'current'),
    'clussterHosts': ('c_hosts', 'current'),
    'datacenterRunningVMS': ('d_vm_running', 'current'),
    'datacenterStoppedVMS': ('d_vm_stopped', 'current'),
    'datacenterTotalVMS': ('d_vm_total', 'current'),
    'clusterRunningVMS': ('c_vm_running', 'current'),
    'clusterStoppedVMS': ('c_vm_stopped', 'current'),
    'clusterTotalVMS': ('c_vm_total', 'current'),
 
}

METRIC_DELIM = '.'


def get_stats():
    stats = dict()

    logger('verb', "get_stats calls vcenterlist %s user %s" % (VCENTERLIST, USERNAME))
    server = VIServer()

    GlobalRunningVMS = ''
    GlobalStoppedVMS = ''
    GlobalTotalVMS = ''

    for vcenter in VCENTERLIST:
        try:
            server.connect(vcenter, USERNAME, PASSWORD)
        except:
            logger('warn', "failed to connect to %s" % (vcenter))
            continue

        datacenters = server.get_datacenters()
        DatacentersCount = len(datacenters)

        ZoneRunningVMS = ''
        ZoneStoppedVMS = ''
        ZoneTotalVMS = ''
        DatacenterRunningVMS = ''
        DatacenterStoppedVMS = ''
        DatacenterTotalVMS = ''

        for datacenter in datacenters:
            clusters = server.get_clusters()
            ClustersCount = len(clusters)

            for c in clusters:
                hosts = server.get_hosts()
                HostsCount = len(hosts)

                for host in hosts:
                    #get host metrics here

                ClusterRunningVMS = server.get_registered_vms(cluster=c, status='poweredOn')
                ClusterStoppedVMS = server.get_registered_vms(cluster=c, status='poweredOff')
                ClusterTotalVMS = server.get_registered_vms(cluster=c)
                DatacenterRunningVMS = DatacenterRunningVMS + ClusterRunningVMS
                DatacenterStoppedVMS = DatacenterStoppedVMS + ClusterStoppedVMS
                DatacenterTotalVMS = DatacenterTotalVMS + ClusterTotalVMS
            
                metricnameClusterRunningVMS = METRIC_DELIM.join(datacenter.lower(), c.lower(), 'clusterrunningvms')
                metricnameClusterStoppedVMS = METRIC_DELIM.join(datacenter.lower(), c.lower(), 'clusterstoppedvms')
                metricnameClusterTotalVMS = METRIC_DELIM.join(datacenter.lower(), c.lower(), 'clustertotalvms')
            
                try:
                    stats[metricnameClusterRunningVMS] = ClusterRunningVMS
                    stats[metricnameClusterStoppedVMS] = ClusterStoppedVMS
                    stats[metricnameClusterTotalVMS] = ClusterTotalVMS
                except (TypeError, ValueError), e:
                    pass
       
            #post datacenter metrics count here

            ZoneRunningVMS = ZoneRunningVMS + DatacenterRunningVMS
            ZoneStoppedVMS = ZoneStoppedVMS + DatacenterStoppedVMS
            ZoneTotalVMS = ZoneTotalVMS + DatacenterTotalVMS

            metricnameDatacenterRunningVMS = METRIC_DELIM.join(datacenter.lower(), 'datacenterrunningvms')
            metricnameDatacenterStoppedVMS = METRIC_DELIM.join(datacenter.lower(), 'datacenterstoppedvms')
            metricnameDatacenterTotalVMS = METRIC_DELIM.join(datacenter.lower(), 'datacentertotalvms')

            try:
                stats[metricnameDatacenterRunningVMS] = DatacenterRunningVMS
                stats[metricnameDatacenterStoppedVMS] = DatacenterStoppedVMS
                stats[metricnameDatacenterTotalVMS] = DatacenterTotalVMS
            except (TypeError, ValueError), e:
                pass

        # post zone metrics count here    
        metricnameZoneRunningVMS = METRIC_DELIM.join('zonerunningvms')
        metricnameZoneStoppedVMS = METRIC_DELIM.join('zonestoppedvms')
        metricnameZoneTotalVMS = METRIC_DELIM.join('zonetotalvms')

        try:
            stats[metricnameZoneRunningVMS] = ZoneRunningVMS
            stats[metricnameZoneStoppedVMS] = ZoneStoppedVMS
            stats[metricnameZoneTotalVMS] = ZoneTotalVMS
        except (TypeError, ValueError), e:
             pass



        metricnameDatacentersCount = METRIC_DELIM.join('datacenters')
        metricnameClustersCount = METRIC_DELIM.join('clusters')
        metricnameHostsCount = METRIC_DELIM.join('hosts')
    
        try:
            stats[metricnameDatacentersCount] = DatacentersCount
            stats[metricnameClustersCount] = ClustersCount
            stats[metricnameHostsCount] = HostsCount
            except (TypeError, ValueError), e:
                pass
    
    #post global metrics here
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
