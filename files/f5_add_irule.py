#!/usr/bin/python
# Add iRule to Virtual Server

import bigsuds
import sys
import getpass
import time
 
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
 
# Retrieve list of VS, of rules and of profiles
virtualservers = b.LocalLB.VirtualServer.get_list()
rules = b.LocalLB.VirtualServer.get_rule(virtualservers)
profiles = b.LocalLB.VirtualServer.get_profile(virtualservers)
irules_list = b.LocalLB.Rule.get_list()
 
#set your iRule name already created in your BigIp
new_rule = '/Common/country_block_v2'
 
vs_to_update = []
rule_to_add = []
found_rule = False
 
# check if iRule is present
for irule in irules_list:
	if irule == new_rule:
		found_rule = True
		break
               
if found_rule:
	print "Found iRule with name: %s" % new_rule
else:
	print "iRule not Found"
	sys.exit()
               
 
#Print virtual Server and rule assigned
count = 0
for vs in virtualservers:
	print "\n\nVS: %s" % vs
	for rule in rules[count]:
		print "\tRules %i: %s" % (count, rule)
	count += 1
 
# Create a list of VS (vs_to_update) for vs which have an HTTP profile and where the irule is not yet present.
count = 0
for vs in virtualservers:
	asHttp_Profile = False
	as_already_rule = False
	check_priority = []
	for profile in profiles[count]:
		if profile["profile_type"] == "PROFILE_TYPE_HTTP":
			asHttp_Profile = True
			break
	for rule in rules[count]:
		check_priority.append(rule["priority"])
		if rule["rule_name"] == new_rule:
			as_already_rule = True
	if asHttp_Profile and not as_already_rule:
		vs_to_update.append(vs)
		if check_priority:
			rule_to_add.append({'rule_name': new_rule, 'priority': (max(check_priority) + 1)})
		else:
			rule_to_add.append({'rule_name': new_rule, 'priority': 0})
	count += 1
               
# Add iRule to elected VS (vs_to_update)
count = 0
for vs in vs_to_update:
	print "\n\nVS to change: %s" % vs
	print "\tRule to add: %s" % rule_to_add[count]
	try:
		b.LocalLB.VirtualServer.add_rule([vs], [[rule_to_add[count]]])
	except Exception, e:
		print e
	count +=1
