#!/usr/bin/python
# Create VS, pool and pool members using iControl SOAP API
# Author: apined12@its.jnj.com
# Name: jnj_f5_newvip
def create_pool(obj, plname, plmethod, plmem, plmonitor, plminmem):
    pool = '/Common/%s' % plname
    pmlist = []
    prio = []
    # The loop below creates lists of pool members and pool priorities
    for m in plmem:
        pm = {}
        pm['address'] = '/Common/%s' % m['address']
        pm['port'] = m['port']
        pmlist.append(pm)
        prio.append(m['priority'])
    for i, hm in enumerate(plmonitor):
        plmonitor[i] = '/Common/%s' % hm
    try:
        getpools = obj.LocalLB.Pool.get_list()
        getmembers = obj.LocalLB.Pool.get_member_v2(pool_names = getpools)
        if pool in getpools and pmlist not in getmembers:
            obj.LocalLB.Pool.add_member_v2(pool_names = [pool], members = [pmlist])
        if pool not in getpools:
            obj.LocalLB.Pool.create_v2(pool_names = [pool], lb_methods = [plmethod], members = [pmlist])
            obj.LocalLB.Pool.set_monitor_association(\
                monitor_associations = [{'monitor_rule': {'monitor_templates': [plmonitor], \
                                         'quorum': 0, 'type': 'MONITOR_RULE_TYPE_AND_LIST'}, \
                                         'pool_name': pool}])
        # Condition below for configuring pool priority groups        
        if plminmem != 0:
            obj.LocalLB.Pool.set_minimum_active_member(pool_names = [pool], values = [plminmem])
            obj.LocalLB.Pool.set_member_priority(pool_names = [pool], members = [pmlist], priorities = [prio])
        return None
    except Exception, e:
        print e

def create_vip(obj, vipname, vipaddr, vipport, vipproto, plname, vipprof, httpprof):
    try:
        client_prot = '/Common/%s' % vipprof
        # Condition below creates VIP with provided pool name otherwise creates it without associated pool
        if plname.lower() != "none":
            pool = '/Common/%s' % plname
            obj.LocalLB.VirtualServer.create(\
                definitions = [{'name': vipname, 'address': vipaddr, 'port': vipport, 'protocol': vipproto}], \
                wildmasks = ['255.255.255.255'], \
                resources = [{'type': 'RESOURCE_TYPE_POOL', 'default_pool_name': pool}], \
                profiles = [[{'profile_context': 'PROFILE_CONTEXT_TYPE_ALL', 'profile_name': client_prot}]])
        else:
            obj.LocalLB.VirtualServer.create(\
                definitions = [{'name': vipname, 'address': vipaddr, 'port': vipport, 'protocol': vipproto}], \
                wildmasks = ['255.255.255.255'], \
                resources = [{'type': 'RESOURCE_TYPE_POOL'}], \
                profiles = [[{'profile_context': 'PROFILE_CONTEXT_TYPE_ALL', 'profile_name': client_prot}]])
        # If HTTP profile is provided, add to virtual server    
        if httpprof.lower() != "none":
            http_prof = '/Common/%s' % httpprof
            obj.LocalLB.VirtualServer.add_profile(virtual_servers = [vipname], \
                profiles = [[{'profile_context': 'PROFILE_CONTEXT_TYPE_ALL', 'profile_name': http_prof}]])
        return None
    except Exception, e:
        print e
           
def set_vip_description(obj, vipname, vipdesc):
    try:
        obj.LocalLB.VirtualServer.set_description(virtual_servers = [vipname], descriptions = [vipdesc])
        return None
    except Exception, e:
        print e
 
def set_vip_def_persist(obj, vipname, vippersist):
    persist = '/Common/%s' % vippersist
    try:
        obj.LocalLB.VirtualServer.add_persistence_profile(virtual_servers = [vipname], \
            profiles = [[{'profile_name': persist, 'default_profile': 'true'}]])
        return None
    except Exception, e:
        print e

def irule_exist(viprule, rulelist):
    if viprule not in rulelist: 
        print "iRule %s not found...please check name or make sure it is loaded on the LB" % viprule
        return False
    else:
        return True

def add_vip_irule(obj, vipname, viprule):
    count = 0
    check_priority = []
    rules = obj.LocalLB.VirtualServer.get_rule(virtual_servers = [vipname])
    if rules != [[]]:
        for rule in rules[count]:
            check_priority.append(rule['priority'])
        count += 1
        try:
            obj.LocalLB.VirtualServer.add_rule(virtual_servers = [vipname], \
                rules = [[{'rule_name': viprule, 'priority': (max(check_priority) + (i+1))}]])
        except Exception, e:
            print e
    else:
        try:
           obj.LocalLB.VirtualServer.add_rule(virtual_servers = [vipname], \
               rules = [[{'rule_name': viprule, 'priority': 0}]])
        except Exception, e:
           print e
    return None            

def set_vip_clientssl(obj, vipname, vipclientssl):
    sslclient = '/Common/%s' % vipclientssl
    try:
        obj.LocalLB.VirtualServer.add_profile(virtual_servers = [vipname], \
            profiles = [[{'profile_context': 'PROFILE_CONTEXT_TYPE_CLIENT', 'profile_name': sslclient}]])    
        return None
    except Exception, e:
        print e

def set_vip_serverssl(obj, vipname, vipserverssl):
    sslserver = '/Common/%s' % vipserverssl
    try:
        obj.LocalLB.VirtualServer.add_profile(virtual_servers = [vipname], \
            profiles = [[{'profile_context': 'PROFILE_CONTEXT_TYPE_SERVER', 'profile_name': sslserver}]])
        return None
    except Exception, e:
        print e

def set_vip_automap(obj, vipname):
    try:
        obj.LocalLB.VirtualServer.set_source_address_translation_automap(virtual_servers = [vipname])
        return None   
    except Exception, e:
        print e

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
# Walk through variable file to configure the VIPs and pools
    for info in vip_facts['vips']:
        vsname = info['vs_name']
        vsaddr = info['vs_address']
        vsport = info['vs_port']
        vsproto = info['vs_protocol']
        vsprof = info['vs_profile']
        vshttp = info['http_profile']

        if info['pool_name'].lower() != "none":
            pname = info['pool_name']
            lbmethod = info['lb_method']
            pmembers = info['members']
            phealth = info['monitors']
            pminmem = info['min_act_mem']
            create_pool(b, pname, lbmethod, pmembers, phealth, pminmem)
        else:
            pname = info['pool_name']

        create_vip(b, vsname, vsaddr, vsport, vsproto, pname, vsprof, vshttp)

        if info['vs_desc'].lower() != "none":
            vsdesc = info['vs_desc']
            set_vip_description(b, vsname, vsdesc)

        if info['clientssl_profile'].lower() != "none" and vshttp == "http" and vsport == 443: 
            vsclientssl = info['clientssl_profile']
            set_vip_clientssl(b, vsname, vsclientssl)
            if info['serverssl_profile'].lower() != "none": 
                vsserverssl = info['serverssl_profile']
                set_vip_serverssl(b, vsname, vsserverssl)

        if info['snat'].lower() == "automap":
            set_vip_automap(b, vsname)

        if info['def_persist'].lower() != "none":
            vspersist = info['def_persist']
            set_vip_def_persist(b, vsname, vspersist)

        if info.has_key('irules') and vshttp == "http":
            vsirules = info['irules']
            listorules = b.LocalLB.Rule.get_list()
            for i, rulecheck in enumerate(vsirules):
                vsirules[i] = '/Common/%s' % rulecheck
                if irule_exist(vsirules[i], listorules):
                    add_vip_irule(b, vsname, vsirules[i])

        print "VIP %s has been configured" % vsname 
# Save configuration; filename supplied will be ignored due to save_flag of SAVE_HIGH_LEVEL_CONFIG
# See F5 API Reference for details

    save_config(b, 'locallb.cfg', 'SAVE_HIGH_LEVEL_CONFIG')   
    print "Configuration completed"
