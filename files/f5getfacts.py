#!/usr/bin/python
# Gather F5 system information using F5 SOAP API
# Author: apined12@its.jnj.com
from timeout import timeout
@timeout(15)
def get_f5_facts(mgmtip, mpass):
    obj = bigsuds.BIGIP(hostname=mgmtip,username='SA-ITS-Networkinfo',password=mpass)
    m = obj.System.SystemInfo.get_version()
    f5ver = re.search(r'\d.+', m).group()
    f5model = obj.System.SystemInfo.get_marketing_name()
    f5sysinfo = obj.System.SystemInfo.get_system_information()
    f5serial = f5sysinfo['chassis_serial']
    f5hostname = f5sysinfo['host_name']
    print "{0} has a serial number of {1}".format(f5hostname, f5serial)
    return [f5hostname, mgmtip, f5serial, f5ver]

if __name__ == "__main__":
    import bigsuds
    import json
    import getpass
    import csv
    import re

    print "Enter F5 password\n"
    upass = getpass.getpass()
    success = 0
    failure = 0
    F5data = [['Hostname','Management IP','Serial No','SW Version']]
    F5dev = open('./files/F5Device-Upgrade-List.csv', 'wb')

    with open('vars/f5List.json') as json_data:
        f5_fact = json.load(json_data)
    for k,v in f5_fact['_meta']['hostvars'].items():
        devicename = k
        mgmt_ip = v['ansible_host']
        try:
            print "Connecting to {}...".format(devicename)
            m = get_f5_facts(mgmt_ip, upass)
            F5data.append(m)
            success += 1
        except Exception,e:
            print e
            failure += 1
    with F5dev:
        writer = csv.writer(F5dev)
        writer.writerows(F5data)
    print "Successful access: {}".format(success)  
    print "Failed access: {}".format(failure)
    total = success + failure
    print "Device count: {}".format(total)
