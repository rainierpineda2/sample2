#!/usr/bin/python
#Author: That Damn Contractor - apineda
#Description: Script to generate network map text file
import bigsuds
import getpass
import time
import sys
import csv

print "Enter device credentials\n"
ltmname = raw_input('LTM Mgmt IP: ')
urname = raw_input('Username: ')
upass = getpass.getpass()

print "Generating network map file..."
b = bigsuds.BIGIP(hostname=ltmname, username=urname, password=upass)
version = b.System.SystemInfo.get_version()
if 'v11' in version or 'v12' in version:
    b = b.with_session_id()
    #Search the / folder for all VIPs for v11
    b.System.Session.set_recursive_query_state(state='STATE_ENABLED')
    b.System.Session.set_active_folder(folder="/")
if 'v10' in version:
    #Search the Common partition for v10; comment out for v9
    b.Management.Partition.set_active_partition("Common")

info = b.System.SystemInfo.get_system_information()
timestr = time.strftime("%Y%m%d")
hostname = info['host_name']
o_file = hostname + '-' + timestr + '.csv'

v = b.LocalLB.VirtualServer
vs_list = v.get_list()
if vs_list == []:
    print "%s is not being used as an F5 LTM" % hostname
    sys.exit()
p = b.LocalLB.Pool
p_list = p.get_list()

if 'v11' in version or 'v12' in version:
    dst = v.get_destination_v2(virtual_servers = vs_list)
else:
    dst = v.get_destination(virtual_servers = vs_list)
dst_ip = [t['address'] for t in dst]
dst_pt = [t['port'] for t in dst]
pool_list = v.get_default_pool_name(virtual_servers = vs_list)
rule_list = v.get_rule(virtual_servers = vs_list)
#Grab only rule name from rule list
rule_name = [[r['rule_name'] for r in group] for group in rule_list]
persist_list = v.get_persistence_profile(virtual_servers = vs_list)
pool_status = p.get_object_status(pool_names = p_list)
pool_lb = p.get_lb_method(pool_names = p_list)
member_status = b.LocalLB.PoolMember.get_object_status(pool_names = pool_list)
# Grab member address and port
mem_addr = [[m['member']['address'] for m in group] for group in member_status]
mem_port = [[m['member']['port'] for m in group] for group in member_status]
combined = zip(vs_list, dst_ip, dst_pt, pool_list, mem_addr, mem_port, rule_name)
wline = 0
with open(o_file, 'w') as myMap:
    writer = csv.writer(myMap)
    writer.writerow(["VIP Names","VIP","VIP Port","Pool Name", \
                     "Pool Member IP","Pool Member Port","iRules"])
    for x in combined:
        writer.writerow(x)
        wline += 1
print "Wrote %s to %s" % (wline, o_file)        
print "Done! Please check output file in your home directory"
