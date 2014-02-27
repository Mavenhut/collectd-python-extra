# collectd-cloudstack - cloudstack.py
#
# Author : Loic Lambiel @ exoscale
# Description : This is a collectd python module to gather stats from Vmware vcenters

import collectd
from pysphere import VIServer, VIProperty
        
        
        
NAME = 'Vcenter'


METRIC_TYPES = {
    'globaldatacenterscount': ('datacenters', 'current'),
    'globalclusterscount': ('clusters', 'current'),
    'globalhostscount': ('hosts', 'current'),
    'zonedatacenterscount': ('z_datacenters', 'current'),
    'zoneclusterscount': ('z_clusters', 'current'),
    'zonehostscount': ('z_hosts', 'current'),
    'globalrunningVMS': ('vm_running', 'current'),
    'globalstoppedVMS': ('vm_stopped', 'current'),
    'globaltotalVMS': ('vm_stopped', 'current'),
    'zonerunningVMS': ('z_vm_running', 'current'),
    'zonestoppedVMS': ('z_vm_stopped', 'current'),
    'zonetotalVMS': ('z_vm_stopped', 'current'),
    'datacenterclusterscount': ('d_clusters', 'current'),
    'datacenterhostscount': ('d_hosts', 'current'),
    'clussterhostscount': ('c_hosts', 'current'),
    'datacenterrunningVMS': ('d_vm_running', 'current'),
    'datacenterstoppedVMS': ('d_vm_stopped', 'current'),
    'datacentertotalVMS': ('d_vm_total', 'current'),
    'clusterrunningVMS': ('c_vm_running', 'current'),
    'clusterstoppedVMS': ('c_vm_stopped', 'current'),
    'clustertotalVMS': ('c_vm_total', 'current'),
 
}

METRIC_DELIM = '.'


def get_stats():
    stats = dict()

    logger('verb', "get_stats calls vcenterlist %s user %s" % (VCENTERLIST, USERNAME))
    server = VIServer()

    GlobalDatacentersCount = ''
    GlobalClustersCount = ''
    GlobalHostsCount = ''
    GlobalRunningVMS = ''
    GlobalStoppedVMS = ''
    GlobalTotalVMS = ''

    for vcenter in VCENTERLIST:
        try:
            server.connect(vcenter, USERNAME, PASSWORD)
        except:
            logger('warn', "failed to connect to %s" % (vcenter))
            continue
         
        ZoneDatacentersCount = ''
        ZoneClustersCount = ''
        ZoneHostsCount = ''
        ZoneRunningVMS = ''
        ZoneStoppedVMS = ''
        ZoneTotalVMS = ''


        datacenters = server.get_datacenters()
        ZoneDatacentersCount = len(datacenters)
        GlobalDatacentersCount = GlobalDatacentersCount + ZoneDatacentersCount

        for d in datacenters:

            DatacenterRunningVMS = ''
            DatacenterStoppedVMS = ''
            DatacenterTotalVMS = ''
            DatacenterClustersCount = ''
            DatacenterHostsCount = ''

            clusters = server.get_clusters(datacenter=d)
            DatacenterClustersCount = len(clusters)
            ZoneClustersCount = ZoneClustersCount + DatacenterClustersCount
            GlobalClustersCount = GlobalClustersCount + ZoneClustersCount

            for c in clusters:
                hosts = server.get_hosts()
                ClusterHostsCount = len(hosts)
                DatacenterHostsCount = DatacenterHostsCount + ClusterHostsCount
                ZoneHostsCount = ZoneHostsCount + DatacenterHostsCount
                GlobalHostsCount = GlobalHostsCount + ZoneHostsCount

                for h, name in server.get_hosts().items():
                    props = VIProperty(server, h)
                    HostMemoryUsage = props.summary.quickStats.overallMemoryUsage
                    HostCpuUsage = props.summary.quickStats.overallCpuUsage
                    HostTotalMemory = props.hardware.memorySize


                ClusterRunningVMS = server.get_registered_vms(cluster=c, status='poweredOn')
                ClusterStoppedVMS = server.get_registered_vms(cluster=c, status='poweredOff')
                ClusterTotalVMS = server.get_registered_vms(cluster=c)
                DatacenterRunningVMS = DatacenterRunningVMS + ClusterRunningVMS
                DatacenterStoppedVMS = DatacenterStoppedVMS + ClusterStoppedVMS
                DatacenterTotalVMS = DatacenterTotalVMS + ClusterTotalVMS
            
                metricnameClusterRunningVMS = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), c.lower(), 'clusterrunningvms')
                metricnameClusterStoppedVMS = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), c.lower(), 'clusterstoppedvms')
                metricnameClusterTotalVMS = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), c.lower(), 'clustertotalvms')
            
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

            metricnameDatacenterRunningVMS = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), 'datacenterrunningvms')
            metricnameDatacenterStoppedVMS = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), 'datacenterstoppedvms')
            metricnameDatacenterTotalVMS = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), 'datacentertotalvms')

            try:
                stats[metricnameDatacenterRunningVMS] = DatacenterRunningVMS
                stats[metricnameDatacenterStoppedVMS] = DatacenterStoppedVMS
                stats[metricnameDatacenterTotalVMS] = DatacenterTotalVMS
            except (TypeError, ValueError), e:
                pass

        # post zone metrics count here    
        metricnameZoneRunningVMS = METRIC_DELIM.join(vcenter.lower(), 'zonerunningvms')
        metricnameZoneStoppedVMS = METRIC_DELIM.join(vcenter.lower(), 'zonestoppedvms')
        metricnameZoneTotalVMS = METRIC_DELIM.join(vcenter.lower(), 'zonetotalvms')

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
   
        GlobalRunningVMS = GlobalRunningVMS + ZoneRunningVMS 
        GlobalStoppedVMS = GlobalStoppedVMS + ZoneStoppedVMS
        GlobalTotalVMS = GlobalTotalVMS + ZoneTotalVMS

        server.disconnect()

    #post global metrics here
    metricnameGlobalRunningVMS = METRIC_DELIM.join('globalrunningvms')
    metricnameGlobalStoppedVMS = METRIC_DELIM.join('globalstoppedvms')
    metricnameGlobalTotalVMS = METRIC_DELIM.join('globaltotalvms')

    try:
        stats[metricnameGlobalRunningVMS] = GlobalRunningVMS
        stats[metricnameGlobalStoppedVMS] = GlobalStoppedVMS
        stats[metricnameGlobalTotalVMS] = GlobalTotalVMS
    except (TypeError, ValueError), e:
        pass 





    return stats	

# callback configuration for module
def configure_callback(conf):
  global API_MONITORS, APIKEY_MONITORS, SECRET_MONITORS, AUTH_MONITORS, VERBOSE_LOGGING
  VCENTERLIST = '' 
  USERNAME = ''
  PASSWORD = ''
  VERBOSE_LOGGING = False

  for node in conf.children:
    if node.key == "Vcenterlist":
      VCENTERLIST = node.values[0]
    elif node.key == "Username":
      USERNAME = node.values[0]
    elif node.key == "Password":
      PASSWORD = node.values[0]
    elif node.key == "Verbose":
      VERBOSE_LOGGING = bool(node.values[0])
    else:
      logger('warn', 'Unknown config key: %s' % node.key)


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
