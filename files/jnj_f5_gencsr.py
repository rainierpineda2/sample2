#!/usr/bin/python
# Generate F5 CSR
# Author: apined12@its.jnj.com
# Name: jnj_f5_gencsr

if __name__ == "__main__":
   
    import bigsuds
    import getpass
    import json
    import jnjf5tools

    print "Enter device credentials\n"
    ltmname = raw_input('F5 Mgmt IP: ')
    urname = raw_input('Username: ')
    upass = getpass.getpass()
# Establish connection with device and get software version
    try:
        b = bigsuds.BIGIP(hostname = ltmname, username = urname, password = upass)
        version = b.System.SystemInfo.get_version()
    except Exception, e:   
        print e
        
# Load the variable file
    with open('../vars/newcsrreq.json', 'r') as cr:
        csr_req = json.load(cr)

# Walk through variable file 
    for info in csr_req.values():
        comname = info['common_name']
        email = info['email']
        country = info['country']
        state = info['state']
        city = info['city']
        org = info['org']
        ou = info['org_unit']
        lsan = info['san']
        
# If SAN is needed, an extension string is created below to be used for a separate F5 API call
# to generate the CSR with SAN extensions
        san = []
        if lsan:
            print lsan
            sd = {}
            sd['extension_type'] = 'CERTIFICATE_EXTENSION_SAN'
            sd['value'] = lsan
            san.append(sd)
            print san
        else:
            pass

# Generate the CSR            
        sfile = jnjf5tools.generate_csr(b, email, comname, country, state, city, org, ou, san, version)
# Download CSR file from F5 to provide to requester
        dfile = comname + '.csr'
        jnjf5tools.file_download(b, sfile, dfile, 65535)
# Sync configuration
        jnjf5tools.config_sync(b)
# Save configuration
    jnjf5tools.save_config(b, 'locallb.cfg', 'SAVE_HIGH_LEVEL_CONFIG')   
    print "CSR has been generated"
