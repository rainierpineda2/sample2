#!/usr/bin/python
#Author: That Damn Contractor - apineda
#Description: Script to generate network map text file
import bigsuds
import getpass
import time
import sys
import json
import collections

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
persist_list = v.get_persistence_profile(virtual_servers = vs_list)
#pool_members = p.get_member(pool_names = pool_list)
pool_status = p.get_object_status(pool_names = p_list)
pool_lb = p.get_lb_method(pool_names = p_list)
member_status = b.LocalLB.PoolMember.get_object_status(pool_names = pool_list)
#Write std output to file
combined = zip(vs_list, dst_ip, dst_pt, pool_list, rule_list, member_status, persist_list)
sys.stdout = open(o_file, 'w')
newDict = {}
newList = []
for x in combined:        
#    newDict = collections.OrderedDict() 
#    newDict['VIP_NAME'] = x[0]
#    newDict['VIP_IP'] = x[1]
#    newDict['VIP_PORT'] = x[2]
#    newDict['POOL'] = x[3]
#    for l in pool_lb:
#        if x[3] == '':
#            newDict['LB_METHOD'] = "NONE"
#        else:    
#            newDict['LB_METHOD'] = l
#    newDict['PERSISTENCE'] = x[6]
#    newDict['RULE'] = x[4]
#    newDict['MEMBER'] = x[5]
#    newList.append(newDict)

    print "VServer: %s" % x[0]
    print "VIP: %s:%d" % (x[1], x[2])
    print "\tPool: %s" % x[3]
    for idx3, p in enumerate(x[6]):
        print "\tPersistence: %s" % p['profile_name']
    for idx1, z in enumerate(x[4]):   
        print "\t\tRule",idx1+1,"= %s" %  z['rule_name'] 
    for idx2, y in enumerate(x[5]):
        print "\tMember",idx2+1,"= %s:%d" % (y['member']['address'], y['member']['port']),
        print "Status: %s" % y['object_status']['status_description']   
    print "\n"
#Redirect stdout to normal
#print json.dumps(newList, indent=4)
sys.stdout.close()
sys.stdout = sys.__stdout__
print "Done! Please check output file in your home directory"
