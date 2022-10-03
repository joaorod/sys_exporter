# Importing the library
import time
import psutil

from prometheus_client.core import GaugeMetricFamily, REGISTRY, CounterMetricFamily
from prometheus_client import start_http_server


class SysExporter(object):
    callsCount=0
    failsCount=0
    startTime = 0
    def __init__(self):
        self.startTime = time.time()
        pass

    def collect(self):
        try:

            self.callsCount+=1
            
            ccalls = CounterMetricFamily("Calls", 'Call count to exporter', labels=['status'])
            ccalls.add_metric(['success'],self.callsCount)
            ccalls.add_metric(['fail'],self.failsCount)

            yield ccalls
                        
            gcpu = GaugeMetricFamily("CPU", 'CPU Usage', labels=['counter'])
            # load1, load5, load15 = psutil.getloadavg()
            loadperc=psutil.cpu_percent(3)
            gcpu.add_metric(['usage'],loadperc)
            # gcpu.add_metric(['load1'],load1)
            # gcpu.add_metric(['load5'],load5)
            # gcpu.add_metric(['load15'],load15)
            print('CPU Usage %:',loadperc)
            yield gcpu

            gmem = GaugeMetricFamily("RAM", 'RAM Usage', labels=['counter'])
            mem = psutil.virtual_memory()
            gmem.add_metric(['total'],mem[0])
            gmem.add_metric(['available'],mem[1])
            gmem.add_metric(['used %'],mem[2])
            gmem.add_metric(['used'],mem[3])
            gmem.add_metric(['free'],mem[4])
            print(mem)

            yield gmem

            gdisk_size = GaugeMetricFamily("HDD_Size", 'Disk Size', labels=['Mountpoint'])
            gdisk_used = GaugeMetricFamily("HDD_Used", 'Disk Used', labels=['Mountpoint'])
            gdisk_free = GaugeMetricFamily("HDD_Free", 'Disk Free', labels=['Mountpoint'])
            gdisk_usage_percent = GaugeMetricFamily("HDD_UsedPerc", 'Disk Usage %', labels=['Mountpoint'])
            
            partitions = psutil.disk_partitions()

            for p in partitions:
                gdisk_size.add_metric([p.mountpoint],psutil.disk_usage(p.mountpoint).total)
                gdisk_used.add_metric([p.mountpoint],psutil.disk_usage(p.mountpoint).used)
                gdisk_free.add_metric([p.mountpoint],psutil.disk_usage(p.mountpoint).free)
                gdisk_usage_percent.add_metric([p.mountpoint],psutil.disk_usage(p.mountpoint).percent)
                print (p.mountpoint, psutil.disk_usage(p.mountpoint))
                
            yield gdisk_size
            yield gdisk_used
            yield gdisk_free
            yield gdisk_usage_percent

        except Exception as e:
            print("Something went wrong:", e)
            self.failsCount+=1
        
if __name__ == '__main__':
    start_http_server(9515)
    REGISTRY.register(SysExporter())
    
    while True:
        time.sleep(1)
