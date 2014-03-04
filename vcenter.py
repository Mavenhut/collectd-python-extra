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
    'zonememoryusage': ('z_memory_usage', 'current'),
    'zonecpuusage': ('z_cpu_usage', 'current'),
    'zonetotalmemory': ('z_total_memory', 'current'),
    'zonecputotal': ('z_cpu_total', 'current'),
    'globalrunningVMS': ('vm_running', 'current'),
    'globalstoppedVMS': ('vm_stopped', 'current'),
    'globaltotalVMS': ('vm_stopped', 'current'),
    'globalmemoryusage': ('memory_usage', 'current'),
    'globalcpuusage': ('cpu_usage', 'current'),
    'globaltotalmemory': ('total_memory', 'current'),
    'globalcputotal': ('cpu_total', 'current'),
    'hostmemoryusage': ('h_memory_usage', 'current'),
    'hostcpuusage': ('h_cpu_usage', 'current'),
    'hosttotalmemory': ('h_total_memory', 'current'),
    'hostcputotal': ('h_cpu_total', 'current'),
    'hostrunningVMS': ('c_vm_running', 'current'),
    'hoststoppedVMS': ('c_vm_stopped', 'current'),
    'hosttotalVMS': ('c_vm_total', 'current'),
    'zonerunningVMS': ('z_vm_running', 'current'),
    'zonestoppedVMS': ('z_vm_stopped', 'current'),
    'zonetotalVMS': ('z_vm_stopped', 'current'),
    'datacenterclusterscount': ('d_clusters', 'current'),
    'datacenterhostscount': ('d_hosts', 'current'),
    'clussterhostscount': ('c_hosts', 'current'),
    'datacenterrunningVMS': ('d_vm_running', 'current'),
    'datacenterstoppedVMS': ('d_vm_stopped', 'current'),
    'datacentertotalVMS': ('d_vm_total', 'current'),
    'datacentermemoryusage': ('d_memory_usage', 'current'),
    'datacentercpuusage': ('d_cpu_usage', 'current'),
    'datacentertotalmemory': ('d_total_memory', 'current'),
    'datacentercputotal': ('d_cpu_total', 'current'),
    'clusterrunningVMS': ('c_vm_running', 'current'),
    'clusterstoppedVMS': ('c_vm_stopped', 'current'),
    'clustertotalVMS': ('c_vm_total', 'current'),
    'clustermemoryusage': ('c_memory_usage', 'current'),
    'clustercpuusage': ('c_cpu_usage', 'current'),
    'clustertotalmemory': ('c_total_memory', 'current'),
    'clustercputotal': ('c_cpu_total', 'current'),
 
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
    GlobalMemoryUsage = ''
    GlobalCpuUsage = ''
    GlobalTotalMemory = ''
    GlobalCpuTotal = ''

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
        ZoneMemoryUsage = ''
        ZoneCpuUsage = ''
        ZoneTotalMemory = ''
        ZoneCpuTotal = ''


        datacenters = server.get_datacenters()
        ZoneDatacentersCount = len(datacenters)
        GlobalDatacentersCount = GlobalDatacentersCount + ZoneDatacentersCount

        for d in datacenters:

            DatacenterRunningVMS = ''
            DatacenterStoppedVMS = ''
            DatacenterTotalVMS = ''
            DatacenterClustersCount = ''
            DatacenterHostsCount = ''
            DatacenterMemoryUsage = ''
            DatacenterCpuUsage = ''
            DatacenterTotalMemory = ''
            DatacenterCpuTotal = ''

            clusters = server.get_clusters(datacenter=d)
            DatacenterClustersCount = len(clusters)
            ZoneClustersCount = ZoneClustersCount + DatacenterClustersCount
            GlobalClustersCount = GlobalClustersCount + ZoneClustersCount

            for c in clusters:
                ClusterMemoryUsage = ''
                ClusterCpuUsage = ''
                ClusterTotalMemory = ''
                ClusterCpuTotal = ''
                ClusterRunningVMS = ''
                ClusterStoppedVMS = ''
                ClusterTotalVMS = ''

                hosts = server.get_hosts()
                ClusterHostsCount = len(hosts)
                DatacenterHostsCount = DatacenterHostsCount + ClusterHostsCount
                ZoneHostsCount = ZoneHostsCount + DatacenterHostsCount
                GlobalHostsCount = GlobalHostsCount + ZoneHostsCount

                for h, name in server.get_hosts().items():
                    props = VIProperty(server, h)
                    HostMemoryUsage = props.summary.quickStats.overallMemoryUsage
                    HostCpuUsage = props.summary.quickStats.overallCpuUsage
                    HostTotalMemory = props.summary.hardware.memorySize
                    HostNumCpuCores = props.summary.hardware.numCpuCores
                    HostMhzPerCore = props.summary.hardware.cpuMhz
                    HostCpuTotal = (HostNumCpuCores * HostMhzPerCore)
                    HostRunningVMS = server.get_registered_vms(host=h, status='poweredOn')
                    HostStoppedVMS = server.get_registered_vms(host=h, status='poweredOff')
                    HostTotalVMS = server.get_registered_vms(host=h)
                               
                    metricnameHostMemoryUsage = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), c.lower(), h.lower(), 'hostmemoryusage')
                    metricnameHostCpuUsage = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), c.lower(), h.lower(), 'hostcpuusage')
                    metricnameHostTotalMemory = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), c.lower(), h.lower(), 'hosttotalmemory')
                    metricnameHostCpuTotal = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), c.lower(), h.lower(), 'hostcputotal')
                    metricnameHostRunningVMS = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), c.lower(), h.lower(), 'hostrunningVMS')
                    metricnameHostStoppedVMS = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), c.lower(), h.lower(), 'hoststoppedVMS')
                    metricnameHostTotalVMS = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), c.lower(), h.lower(), 'hosttotalVMS')

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
            
                metricnameClusterRunningVMS = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), c.lower(), 'clusterrunningvms')
                metricnameClusterStoppedVMS = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), c.lower(), 'clusterstoppedvms')
                metricnameClusterTotalVMS = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), c.lower(), 'clustertotalvms')
                metricnameClusterMemoryUsage = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), c.lower(), h.lower(), 'clustermemoryusage')
                metricnameClusterCpuUsage = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), c.lower(), h.lower(), 'clustercpuusage')
                metricnameClusterTotalMemory = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), c.lower(), h.lower(), 'clustertotalmemory')
                metricnameClusterCpuTotal = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), c.lower(), h.lower(), 'clustercputotal')
            
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

            metricnameDatacenterRunningVMS = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), 'datacenterrunningvms')
            metricnameDatacenterStoppedVMS = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), 'datacenterstoppedvms')
            metricnameDatacenterTotalVMS = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), 'datacentertotalvms')
            metricnameDatacenterMemoryUsage = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), c.lower(), 'datacentermemoryusage')
            metricnameDatacenterCpuUsage = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), c.lower(), 'datacentercpuusage')
            metricnameDatacenterTotalMemory = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), c.lower(), 'datacentertotalmemory')
            metricnameDatacenterCpuTotal = METRIC_DELIM.join(vcenter.lower(), datacenter.lower(), c.lower(), 'datacentercputotal')

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
        metricnameZoneRunningVMS = METRIC_DELIM.join(vcenter.lower(), 'zonerunningvms')
        metricnameZoneStoppedVMS = METRIC_DELIM.join(vcenter.lower(), 'zonestoppedvms')
        metricnameZoneTotalVMS = METRIC_DELIM.join(vcenter.lower(), 'zonetotalvms')
        metricnameZoneMemoryUsage = METRIC_DELIM.join(vcenter.lower(), 'zonememoryusage')
        metricnameZoneCpuUsage = METRIC_DELIM.join(vcenter.lower(), 'zonecpuusage')
        metricnameZoneTotalMemory = METRIC_DELIM.join(vcenter.lower(), 'zonetotalmemory')
        metricnameZoneCpuTotal = METRIC_DELIM.join(vcenter.lower(), 'zonecputotal')

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
        GlobalMemoryUsage = GlobalMemoryUsage + ZoneMemoryUsage
        GlobalCpuUsage = GlobalCpuUsage + ZoneCpuUsage
        GlobalTotalMemory = GlobalTotalMemory + ZoneTotalMemory
        GlobalCpuTotal = GlobalCpuTotal + ZoneCpuTotal
        

        server.disconnect()

    #post global metrics here
    metricnameGlobalRunningVMS = METRIC_DELIM.join('globalrunningvms')
    metricnameGlobalStoppedVMS = METRIC_DELIM.join('globalstoppedvms')
    metricnameGlobalTotalVMS = METRIC_DELIM.join('globaltotalvms')
    metricnameGlobalMemoryUsage = METRIC_DELIM.join('globalmemoryusage')
    metricnameGlobalCpuUsage = METRIC_DELIM.join('globalcpuusage')
    metricnameGlobalTotalMemory = METRIC_DELIM.join('globaltotalmemory')
    metricnameGlobalCpuTotal = METRIC_DELIM.join('globalcputotal')

    try:
        stats[metricnameGlobalRunningVMS] = GlobalRunningVMS
        stats[metricnameGlobalStoppedVMS] = GlobalStoppedVMS
        stats[metricnameGlobalTotalVMS] = GlobalTotalVMS
        stats[metricnameGlobalMemoryUsage] = GlobalMemoryUsage
        stats[metricnameGlobalCpuUsage] = GlobalCpuUsage
        stats[metricnameGlobalTotalMemory] = GlobalTotalMemory
        stats[metricnameGlobalCpuTotal] = GlobalCpuTotal
    except (TypeError, ValueError), e:
        pass 





    return stats	

# callback configuration for module
def configure_callback(conf):
  global VCENTERLIST, USERNAME, PASSWORD, VERBOSE_LOGGING
  VCENTERLIST = [gv1m-vw-vc01] 
  USERNAME = ''
  PASSWORD = ''
  VERBOSE_LOGGING = False

  for node in conf.children:
    #if node.key == "Vcenterlist":
    #  VCENTERLIST = node.values[0]
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
