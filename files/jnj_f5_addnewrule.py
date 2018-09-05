#!/usr/bin/python
# Add iRules to virtual server
# Author: apined12@its.jnj.com
# Name: jnj_f5_addnewrule

if __name__ == "__main__":
   
    import bigsuds
    import getpass
    from jinja2 import Environment, FileSystemLoader
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
        
# Load the variable file and Jinja2 template
    with open('./vars/addltmrulevars.yml', 'r') as newrule:
        rule_facts = yaml.load(newrule)
    env = Environment(loader = FileSystemLoader('./templates'), trim_blocks=True, lstrip_blocks=True)
    template = env.get_template('irule-redirect.j2')

# Walk through variable file 
    for info in rule_facts['vips']:
        vsname = info['vs_name']
        rule_f = './files/Redirect_%s_v1.0.1.tcl' % vsname
        vsirule = '/Common/Redirect_%s_v1.0.1' % vsname
# Generate iRule from template        
        with open(rule_f, 'wb') as f:
            rule_content = template.render(rule_facts)
            f.write(rule_content)
# Create iRule            
        jnjf5tools.create_irule(b, vsirule, rule_content)
# Check if an http profile is applied and add new iRule if that check passes        
        if ijnjf5tools.vs_has_http(b, vsname):
            jnjf5tools.add_vip_irule(b, vsname, vsirule)
# Save configuration
    jnjf5tools.save_config(b, 'locallb.cfg', 'SAVE_HIGH_LEVEL_CONFIG')   
    print "Configuration completed"
