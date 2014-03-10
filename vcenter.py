# collectd-cloudstack - cloudstack.py
#
# Author : Loic Lambiel @ exoscale
# Description : This is a collectd python module to gather stats from Vmware vcenters

import collectd
from pysphere import VIServer, VIProperty
        
        
        
NAME = 'Vcenter'




METRIC_TYPES = {
    'zonedatacenterscount': ('z_datacenters_count', 'current'),
    'zoneclusterscount': ('z_clusters_count', 'current'),
    'zonehostscount': ('z_hosts_count', 'current'),
    'zonememoryusage': ('z_memory_usage', 'current'),
    'zonecpuusage': ('z_cpu_usage', 'current'),
    'zonetotalmemory': ('z_total_memory', 'current'),
    'zonecputotal': ('z_cpu_total', 'current'),
    'hostmemoryusage': ('h_memory_usage', 'current'),
    'hostcpuusage': ('h_cpu_usage', 'current'),
    'hosttotalmemory': ('h_total_memory', 'current'),
    'hostcputotal': ('h_cpu_total', 'current'),
    'hostrunningvms': ('c_vm_running_count', 'current'),
    'hoststoppedvms': ('c_vm_stopped_count', 'current'),
    'hosttotalvms': ('c_vm_total_count', 'current'),
    'zonerunningvms': ('z_vm_running_count', 'current'),
    'zonestoppedvms': ('z_vm_stopped_count', 'current'),
    'zonetotalvms': ('z_vm_total_count', 'current'),
    'datacenterclusterscount': ('d_clusters_count', 'current'),
    'datacenterhostscount': ('d_hosts_count', 'current'),
    'clussterhostscount': ('c_hosts_count', 'current'),
    'datacenterrunningvms': ('d_vm_running_count', 'current'),
    'datacenterstoppedvms': ('d_vm_stopped_count', 'current'),
    'datacentertotalvms': ('d_vm_total_count', 'current'),
    'datacentermemoryusage': ('d_memory_usage', 'current'),
    'datacentercpuusage': ('d_cpu_usage', 'current'),
    'datacentertotalmemory': ('d_total_memory', 'current'),
    'datacentercputotal': ('d_cpu_total_count', 'current'),
    'clusterrunningvms': ('c_vm_running_count', 'current'),
    'clusterstoppedvms': ('c_vm_stopped_count', 'current'),
    'clustertotalvms': ('c_vm_total_count', 'current'),
    'clustermemoryusage': ('c_memory_usage', 'current'),
    'clustercpuusage': ('c_cpu_usage', 'current'),
    'clustertotalmemory': ('c_total_memory', 'current'),
    'clustercputotal': ('c_cpu_total', 'current'),
 
}

METRIC_DELIM = '.'


def get_stats():
    stats = dict()

    logger('verb', "get_stats calls vcenterlist %s user %s" % (VCENTER, USERNAME))
    server = VIServer()

    try:
        server.connect(VCENTER, USERNAME, PASSWORD)
    except:
        logger('warn', "failed to connect to %s" % (VCENTER))
        quit()
         
    ZoneDatacentersCount = 0
    ZoneClustersCount = 0
    ZoneHostsCount = 0
    ZoneRunningVMS = 0
    ZoneStoppedVMS = 0
    ZoneTotalVMS = 0
    ZoneMemoryUsage = 0
    ZoneCpuUsage = 0
    ZoneTotalMemory = 0
    ZoneCpuTotal = 0


    datacenters = server.get_datacenters()
    ZoneDatacentersCount = len(datacenters)

    for d,dname in server.get_datacenters().items():

        if "." in dname:
            dname = dname.split(".")[0]

        DatacenterRunningVMS = 0
        DatacenterStoppedVMS = 0
        DatacenterTotalVMS = 0
        DatacenterClustersCount = 0
        DatacenterHostsCount = 0
        DatacenterMemoryUsage = 0
        DatacenterCpuUsage = 0
        DatacenterTotalMemory = 0
        DatacenterCpuTotal = 0

        clusters = server.get_clusters(d)
        DatacenterClustersCount = len(clusters)
        ZoneClustersCount = ZoneClustersCount + DatacenterClustersCount

        for c,cname in server.get_clusters().items():

            if "." in cname:
                cname = cname.split(".")[0]

            ClusterMemoryUsage = 0
            ClusterCpuUsage = 0
            ClusterTotalMemory = 0
            ClusterCpuTotal = 0
            ClusterRunningVMS = 0
            ClusterStoppedVMS = 0
            ClusterTotalVMS = 0

            hosts = server.get_hosts(c)
            ClusterHostsCount = len(hosts)
            DatacenterHostsCount = DatacenterHostsCount + ClusterHostsCount
            ZoneHostsCount = ZoneHostsCount + DatacenterHostsCount

            for h, hname in server.get_hosts().items():
                    
                if "." in hname:
                    hname = hname.split(".")[0]

                props = VIProperty(server, h)
                HostMemoryUsage = props.summary.quickStats.overallMemoryUsage
                HostCpuUsage = props.summary.quickStats.overallCpuUsage
                HostTotalMemory = props.summary.hardware.memorySize
                HostNumCpuCores = props.summary.hardware.numCpuCores
                HostMhzPerCore = props.summary.hardware.cpuMhz
                HostCpuTotal = (HostNumCpuCores * HostMhzPerCore)
                HostRunningVMS = len(server.get_registered_vms(h, status='poweredOn'))
                HostStoppedVMS = len(server.get_registered_vms(h, status='poweredOff'))
                HostTotalVMS = len(server.get_registered_vms(h))
                               
                metricnameHostMemoryUsage = METRIC_DELIM.join([VCENTER.lower(), dname.lower(), cname.lower(), hname.lower(), 'hostmemoryusage'])
                metricnameHostCpuUsage = METRIC_DELIM.join([VCENTER.lower(), dname.lower(), cname.lower(), hname.lower(), 'hostcpuusage'])
                metricnameHostTotalMemory = METRIC_DELIM.join([VCENTER.lower(), dname.lower(), cname.lower(), hname.lower(), 'hosttotalmemory'])
                metricnameHostCpuTotal = METRIC_DELIM.join([VCENTER.lower(), dname.lower(), cname.lower(), hname.lower(), 'hostcputotal'])
                metricnameHostRunningVMS = METRIC_DELIM.join([VCENTER.lower(), dname.lower(), cname.lower(), hname.lower(), 'hostrunningVMS'])
                metricnameHostStoppedVMS = METRIC_DELIM.join([VCENTER.lower(), dname.lower(), cname.lower(), hname.lower(), 'hoststoppedVMS'])
                metricnameHostTotalVMS = METRIC_DELIM.join([VCENTER.lower(), dname.lower(), cname.lower(), hname.lower(), 'hosttotalVMS'])

                ClusterMemoryUsage = ClusterMemoryUsage + HostMemoryUsage
                ClusterCpuUsage = ClusterCpuUsage + HostCpuUsage
                ClusterTotalMemory = ClusterTotalMemory + HostTotalMemory
                ClusterCpuTotal = ClusterCpuTotal + HostCpuTotal
                ClusterRunningVMS = ClusterRunningVMS + HostRunningVMS
                ClusterStoppedVMS = ClusterStoppedVMS + HostStoppedVMS
                ClusterTotalVMS = ClusterTotalVMS + HostTotalVMS

                try:
                    stats[metricnameHostMemoryUsage] = HostMemoryUsage
                    stats[metricnameHostCpuUsage] = HostCpuUsage
                    stats[metricnameHostTotalMemory] = HostTotalMemory
                    stats[metricnameHostCpuTotal] = HostCpuTotal
                    stats[metricnameHostRunningVMS] = HostRunningVMS
                    stats[metricnameHostStoppedVMS] = HostStoppedVMS
                    stats[metricnameHostTotalVMS] = HostTotalVMS
                except (TypeError, ValueError), e:
                    pass


            DatacenterRunningVMS = DatacenterRunningVMS + ClusterRunningVMS
            DatacenterStoppedVMS = DatacenterStoppedVMS + ClusterStoppedVMS
            DatacenterTotalVMS = DatacenterTotalVMS + ClusterTotalVMS
            DatacenterMemoryUsage = DatacenterMemoryUsage + ClusterMemoryUsage
            DatacenterCpuUsage = DatacenterCpuUsage + ClusterCpuUsage
            DatacenterTotalMemory = DatacenterTotalMemory + ClusterTotalMemory
            DatacenterCpuTotal = DatacenterCpuTotal + ClusterCpuTotal
            
            metricnameClusterRunningVMS = METRIC_DELIM.join([VCENTER.lower(), dname.lower(), cname.lower(), 'clusterrunningvms'])
            metricnameClusterStoppedVMS = METRIC_DELIM.join([VCENTER.lower(), dname.lower(), cname.lower(), 'clusterstoppedvms'])
            metricnameClusterTotalVMS = METRIC_DELIM.join([VCENTER.lower(), dname.lower(), cname.lower(), 'clustertotalvms'])
            metricnameClusterMemoryUsage = METRIC_DELIM.join([VCENTER.lower(), dname.lower(), cname.lower(), 'clustermemoryusage'])
            metricnameClusterCpuUsage = METRIC_DELIM.join([VCENTER.lower(), dname.lower(), cname.lower(), 'clustercpuusage'])
            metricnameClusterTotalMemory = METRIC_DELIM.join([VCENTER.lower(), dname.lower(), cname.lower(), 'clustertotalmemory'])
            metricnameClusterCpuTotal = METRIC_DELIM.join([VCENTER.lower(), dname.lower(), cname.lower(), 'clustercputotal'])
            
            try:
                stats[metricnameClusterRunningVMS] = ClusterRunningVMS
                stats[metricnameClusterStoppedVMS] = ClusterStoppedVMS
                stats[metricnameClusterTotalVMS] = ClusterTotalVMS
                stats[metricnameClusterMemoryUsage] = ClusterMemoryUsage 
                stats[metricnameClusterCpuUsage] = ClusterCpuUsage
                stats[metricnameClusterTotalMemory] = ClusterTotalMemory
                stats[metricnameClusterCpuTotal] = ClusterCpuTotal
            except (TypeError, ValueError), e:
                pass
       
        #post datacenter metrics count here

        ZoneRunningVMS = ZoneRunningVMS + DatacenterRunningVMS
        ZoneStoppedVMS = ZoneStoppedVMS + DatacenterStoppedVMS
        ZoneTotalVMS = ZoneTotalVMS + DatacenterTotalVMS
        ZoneMemoryUsage = ZoneMemoryUsage + DatacenterMemoryUsage
        ZoneCpuUsage = ZoneCpuUsage + DatacenterCpuUsage
        ZoneTotalMemory = ZoneTotalMemory + DatacenterTotalMemory
        ZoneCpuTotal = ZoneCpuTotal + DatacenterCpuTotal

        metricnameDatacenterRunningVMS = METRIC_DELIM.join([VCENTER.lower(), dname.lower(), 'datacenterrunningvms'])
        metricnameDatacenterStoppedVMS = METRIC_DELIM.join([VCENTER.lower(), dname.lower(), 'datacenterstoppedvms'])
        metricnameDatacenterTotalVMS = METRIC_DELIM.join([VCENTER.lower(), dname.lower(), 'datacentertotalvms'])
        metricnameDatacenterMemoryUsage = METRIC_DELIM.join([VCENTER.lower(), dname.lower(), 'datacentermemoryusage'])
        metricnameDatacenterCpuUsage = METRIC_DELIM.join([VCENTER.lower(), dname.lower(), 'datacentercpuusage'])
        metricnameDatacenterTotalMemory = METRIC_DELIM.join([VCENTER.lower(), dname.lower(), 'datacentertotalmemory'])
        metricnameDatacenterCpuTotal = METRIC_DELIM.join([VCENTER.lower(), dname.lower(), 'datacentercputotal'])

        try:
            stats[metricnameDatacenterRunningVMS] = DatacenterRunningVMS
            stats[metricnameDatacenterStoppedVMS] = DatacenterStoppedVMS
            stats[metricnameDatacenterTotalVMS] = DatacenterTotalVMS
            stats[metricnameDatacenterMemoryUsage] = DatacenterMemoryUsage
            stats[metricnameDatacenterCpuUsage] = DatacenterCpuUsage
            stats[metricnameDatacenterTotalMemory] = DatacenterTotalMemory
            stats[metricnameDatacenterCpuTotal] = DatacenterCpuTotal
        except (TypeError, ValueError), e:
            pass

    # post zone metrics count here    
    metricnameZoneRunningVMS = METRIC_DELIM.join([VCENTER.lower(), 'zonerunningvms'])
    metricnameZoneStoppedVMS = METRIC_DELIM.join([VCENTER.lower(), 'zonestoppedvms'])
    metricnameZoneTotalVMS = METRIC_DELIM.join([VCENTER.lower(), 'zonetotalvms'])
    metricnameZoneMemoryUsage = METRIC_DELIM.join([VCENTER.lower(), 'zonememoryusage'])
    metricnameZoneCpuUsage = METRIC_DELIM.join([VCENTER.lower(), 'zonecpuusage'])
    metricnameZoneTotalMemory = METRIC_DELIM.join([VCENTER.lower(), 'zonetotalmemory'])
    metricnameZoneCpuTotal = METRIC_DELIM.join([VCENTER.lower(), 'zonecputotal'])

    try:
        stats[metricnameZoneRunningVMS] = ZoneRunningVMS
        stats[metricnameZoneStoppedVMS] = ZoneStoppedVMS
        stats[metricnameZoneTotalVMS] = ZoneTotalVMS
        stats[metricnameZoneMemoryUsage] = ZoneMemoryUsage
        stats[metricnameZoneCpuUsage] = ZoneCpuUsage
        stats[metricnameZoneTotalMemory] = ZoneTotalMemory
        stats[metricnameZoneCpuTotal] = ZoneCpuTotal
    except (TypeError, ValueError), e:
        pass



    metricnameZoneDatacentersCount = METRIC_DELIM.join([VCENTER.lower(), 'zonedatacenterscount'])
    metricnameZoneClustersCount = METRIC_DELIM.join([VCENTER.lower(),'zoneclusterscount'])
    metricnameZoneHostsCount = METRIC_DELIM.join([VCENTER.lower(),'zonehostscount'])
    
    try:
        stats[metricnameZoneDatacentersCount] = ZoneDatacentersCount
        stats[metricnameZoneClustersCount] = ZoneClustersCount
        stats[metricnameZoneHostsCount] = ZoneHostsCount
    except (TypeError, ValueError), e:
        pass
   

    server.disconnect()

    return stats	

# callback configuration for module
def configure_callback(conf):
  global VCENTER, USERNAME, PASSWORD, VERBOSE_LOGGING
  VCENTER = ''
  USERNAME = ''
  PASSWORD = ''
  VERBOSE_LOGGING = False

  for node in conf.children:
    if node.key == "Vcenter":
      VCENTER = node.values[0]
    if node.key == "Username":
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
