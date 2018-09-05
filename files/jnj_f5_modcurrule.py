#!/usr/bin/python
# Modify/update iRules on an existing virtual server
# Author: apined12@its.jnj.com
# Name: jnj_f5_modcurrule

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
    with open('./vars/addltmrulevars.yml', 'r') as newrule:
        rule_facts = yaml.load(newrule)

# Walk through variable file 
    for info in rule_facts['vips']:
        vsname = info['vs_name']
        vsirule = '/Common/%s' % info['new_rule']
        vsorule = '/Common/%s' % info['cur_rule']
        lirules = jnjf5tools.show_irule(b, vsname)
        print "Current iRules for %s\n" % vsname
        print "%s" % lirules
# If VS has an http profile applied, replace current iRule (vsorule) with new iRule (vsirule)        
        if jnjf5tools.vs_has_http(b, vsname):
            jnjf5tools.mod_vip_irule(b, vsname, vsorule, vsirule)
            lirules = jnjf5tools.show_irule(b, vsname)
            print "New iRules for %s\n" % vsname
            print "%s" % lirules

# Save configuration
    jnjf5tools.save_config(b, 'locallb.cfg', 'SAVE_HIGH_LEVEL_CONFIG')   
    print "Configuration completed"
