#!/usr/bin/python
# Modify pool members (add/delete)
# Author: apined12@its.jnj.com
# Name: jnj_f5_chgpool

if __name__ == "__main__":
   
    import bigsuds
    import getpass
    import yaml
    import sys
    import jnjf5tools

    print "Enter device credentials\n"
    ltmname = raw_input('F5 Mgmt IP: ')
    urname = raw_input('Username: ')
    upass = getpass.getpass()
# Establish connection with device
    try:
        b = bigsuds.BIGIP(hostname = ltmname, username = urname, password = upass)
    except Exception, e:   
        print e
# Load the variable file
    with open('vars/poolchg.yml', 'r') as newvip:
        vip_facts = yaml.load(newvip)
# Walk through variable file to configure the VIPs and pools
    for info in vip_facts['vips']:
        vsname = info['vs_name']

        if info['pool_name'].lower() != "none":
            pname = info['pool_name']
            pmembers = info['members']
            pminmem = info['min_act_mem']
            jnjf5tools.modify_pool(b, pname, pmembers, pminmem)

        print "Pool %s has been modified" % pname 
# Save configuration; filename supplied will be ignored due to save_flag of SAVE_HIGH_LEVEL_CONFIG
# See F5 API Reference for details

    jnjf5tools.save_config(b, 'locallb.cfg', 'SAVE_HIGH_LEVEL_CONFIG')   
    print "Configuration completed"
