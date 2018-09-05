#!/usr/bin/python
#Author: That Damn Contractor - apineda
#Description: Script to generate network map text file
import bigsuds
import getpass
import time
import sys

print "Enter device credentials\n"
gtmname = raw_input('GTM Mgmt IP: ')
urname = raw_input('Username: ')
upass = getpass.getpass()

print "Generating network map file..."
b = bigsuds.BIGIP(hostname=gtmname, username=urname, password=upass)
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
o_file = hostname + '-' + timestr + '.txt'

w = b.GlobalLB.WideIP
wip_list = w.get_list()
if wip_list == []:
    print "%s is not being used as an F5 GTM/DNS" % hostname
    sys.exit()
p_list = w.get_wideip_pool(wide_ips = wip_list)
alyas = w.get_alias(wide_ips = wip_list)
p = b.GlobalLB.Pool.get_list()
p_member = b.GlobalLB.Pool.get_member(pool_names = p)
p_stat = b.GlobalLB.Pool.get_object_status(pool_names = p) 

#Write std output to file
combined = zip(wip_list, p_list, p_stat, alyas)
sys.stdout = open(o_file, 'w')
for x in combined:
    print "WideIP: %s" % x[0]
    for y in x[1]:
        print "\tPool: %s" % y['pool_name']
        if y['pool_name'] in p: 
           print "\tStatus: %s" % p_stat[p.index(y['pool_name'])]['status_description']
           mquery = p_member[p.index(y['pool_name'])]
           for mquery in mquery: 
               print "\t\tMember: %s:%d" % (mquery['member']['address'], mquery['member']['port'])          
    for t in x[3]: 
        print "\tAlias: %s" % t 
    print "\n"
#Redirect stdout to normal
sys.stdout.close()
sys.stdout = sys.__stdout__
print "Done! Please check output file in your home directory"
