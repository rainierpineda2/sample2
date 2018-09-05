#!/usr/bin/python
# Delete VS, pool and pool members using iControl SOAP API
# Author: apined12@its.jnj.com
# Name: jnj_f5_delvip
def delete_pool(obj, plname):
    pool = '/Common/%s' % plname
    try:
        vs_updated = obj.LocalLB.VirtualServer.get_list()
        pool_list = obj.LocalLB.VirtualServer.get_default_pool_name(virtual_servers = [vs_updated])
        combined = zip(vs_updated, pool_list)
        for x in combined:
            if pool == x[1]:
                print "Unable to delete pool %s used by %s" % (x[1], x[0])
        if pool not in pool_list:    
            obj.LocalLB.Pool.delete_pool(pool_names = [pool])
    except Exception, e:
        print e
    return None

def delete_vip(obj, vipname, vs_list):
    try:
        vs = '/Common/%s' % vipname
        if vs in vs_list:
            obj.LocalLB.VirtualServer.delete_virtual_server(virtual_servers = [vs])
    except Exception, e:
        print e
    return None

def save_config(obj, savefile, saveflag):
    try:
        obj.System.ConfigSync.save_configuration(filename = savefile, save_flag = saveflag)
    except Exception, e:
        print e
    return None    

if __name__ == "__main__":
   
    import bigsuds
    import getpass
    import yaml
    import sys

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
    with open('vars/newltmvippy.yml', 'r') as newvip:
        vip_facts = yaml.load(newvip)
# Gather virtual server list
    vs_list = b.LocalLB.VirtualServer.get_list()
# Walk through variable file to configure the VIPs and pools
    for info in vip_facts['vips']:
        vsname = info['vs_name']
        delete_vip(b, vsname, vs_list)
        if info['pool_name'].lower() != "none":
            pname = info['pool_name']
            delete_pool(b, pname)

# Save configuration; filename supplied will be ignored due to save_flag of SAVE_HIGH_LEVEL_CONFIG
# See F5 API Reference for details

    save_config(b, 'locallb.cfg', 'SAVE_HIGH_LEVEL_CONFIG')        
    print "VIP cleanup complete. Please log in to %s via browser to check" % ltmname
