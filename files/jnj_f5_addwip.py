#!/usr/bin/python
# Create GTM wideIP using iControl SOAP API
# This code has been tested on v11.x
# Author: apined12@its.jnj.com
# Name: jnj_f5_addwip
def check_vs_exist(obj, vs_ltm):
    try:
        vslist = obj.GlobalLB.VirtualServerV2.get_list()
    except Exception, e:
        print e
    for vs in vslist:
        if vs['name'] == vs_ltm:
            return vs['name']

def check_vs_discovery(obj, vs_srv):
    try:
        vsd = obj.GlobalLB.Server.get_auto_configuration_state(servers = [vs_srv])
        return vsd
    except Exception, e:
        print e

def create_gtm_vs(obj, vs_srv, vs_ltm, vs_addr, vs_port):
    try:
        obj.GlobalLB.VirtualServerV2.create(virtual_servers = [{'name': vs_ltm, 'server': vs_srv}], \
            addresses = [{'address': vs_addr, 'port': vs_port}])    
        return None
    except Exception, e:
        z = ''.join(e)
        print 'Message:%s' % z.rsplit(':',1)[1]

def create_gtm_pool(obj, wip_pool, pref_lb, pm_list, vs_order):
    try:
        obj.GlobalLB.Pool.create_v2(pool_names = [wip_pool], lb_methods = [pref_lb], \
            members = [pm_list], orders = [vs_order]) 
        return None
    except Exception, e:
        print e

def create_gtm_wideip(obj, wide_ip, wip_lb, wip_pool):
    try:
        obj.GlobalLB.WideIP.create(wide_ips = [wide_ip], lb_methods = [wip_lb], \
            wideip_pools = [[{'pool_name': wip_pool, 'order': 0, 'ratio': 0}]], \
            wideip_rules = [[]]) 
        return None
    except Exception, e:
        print e

def check_wip(obj, wide_ip):
    wip = '/Common/%s' % wide_ip
    try:
        wiplist = obj.GlobalLB.WideIP.get_list()
    except Exception, e:
        print e
    if wip in wiplist:
        print "WideIP %s has been configured" % wide_ip
    return None

def save_config(obj, savefile, saveflag):
    try:
        obj.System.ConfigSync.save_configuration(filename = savefile, save_flag = saveflag)
        return None
    except Exception, e:
        print e

if __name__ == "__main__":
   
    import bigsuds
    import getpass
    import yaml

    print "Enter device credentials\n"
    gtmname = raw_input('F5 Mgmt IP: ')
    urname = raw_input('Username: ')
    upass = getpass.getpass()
# Establish connection with device
    try:
        b = bigsuds.BIGIP(hostname = gtmname, username = urname, password = upass)
    except Exception, e:   
        print e
# Load the variable file
    with open('vars/newwippy.yml', 'r') as newwip:
        wip_facts = yaml.load(newwip)
# Walk through variable file to configure WIP
    for info in wip_facts['wip']:
        wideip = info['wideip']
        wiplb = info['wip_lb']
        wippool = info['wip_pool']
        preflb = info['pref_lb']
        server = info['v_server']
# Create a list of virtual server order; check if virtual server discovery is disabled on server
        vsorder = []
        pmlist = []
        for m in server:
            pm = {}
            vsltm = '/Common/%s' % m['vs_ltm']
            pm['name'] = vsltm
            vssrv = '/Common/%s' % m['name']
            pm['server'] = vssrv
            pmlist.append(pm)
            vsaddr = m['address']
            vsport = m['port']
            vsorder.append(m['order'])
            vsdiscovery = check_vs_discovery(b, vssrv)
            if 'AUTOCONFIG_DISABLED' in vsdiscovery:
                create_gtm_vs(b, vssrv, vsltm, vsaddr, vsport)
                
        create_gtm_pool(b, wippool, preflb, pmlist, vsorder)       
        create_gtm_wideip(b, wideip, wiplb, wippool)
        check_wip(b, wideip)

# Save configuration; filename supplied will be ignored due to save_flag of SAVE_HIGH_LEVEL_CONFIG
# See F5 API Reference for details
        save_config(b, 'locallb.cfg', 'SAVE_HIGH_LEVEL_CONFIG')   
