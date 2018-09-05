#!/usr/bin/python
# F5 functions used for JnJ F5 Network Automation
# Author: apined12@its.jnj.com
# Name: jnjf5tools

import sys
import time
import os
from base64 import b64decode

def vs_has_http(obj, vipname):
    '''
This function checks if an HTTP profile is applied to an F5 VIP.
obj = BIGIP connection instance
vipname = virtual server name, e.g. VS-10.0.209.2-80
    '''
    vipname = '/Common/%s' % vipname
    try:
        profs = obj.LocalLB.VirtualServer.get_profile(virtual_servers = [vipname])
    except Exception, e:
        print e
# Check for http profile applied to virtual server    
    ptypes = [z['profile_type'] for x in profs for z in x]
    if 'PROFILE_TYPE_HTTP' in ptypes:
        return True
    else:
        return False

def show_irule(obj, vipname):
    '''
This function displays the iRules associated with a virtual server
    '''
    try:
        rules = obj.LocalLB.VirtualServer.get_rule(virtual_servers = [vipname])
        return rules
    except Exception, e:
        print e

def create_irule(obj, viprule, vrule_content):
    '''
This function create a new iRule.
obj = BIGIP connection instance
viprule = Name of new iRule,e.g. Redirect_VS-10.0.209.6-80_v1.0 
vrule_content = Contents of new iRule stored in an external file; may be created using 
                standard iRule Jinja template 
    '''
    try:
        obj.LocalLB.Rule.create(rules = [{'rule_name': viprule, 'rule_definition': vrule_content}])
        return None
    except Exception, e:
        print e

def mod_vip_irule(obj, vipname, curviprule, viprule):
    '''
This function replaces an existing iRule with a new iRule supplied from
the variable input file.
obj = BIGIP connection instance
vipname = virtual server name, e.g. VS-10.0.209.2-80
curviprule = Name of existing iRule that needs to be replaced
viprule = Name of modified iRule to replace the existing iRule,e.g. Redirect_VS-10.0.209.6-80_v1.0
    ''' 
    lsrules = obj.LocalLB.VirtualServer.get_rule(virtual_servers = [vipname])
    for lrule in lsrules:
        for y in lrule:
            if y['rule_name'] == curviprule:
               try:
                   obj.LocalLB.VirtualServer.remove_rule(virtual_servers = [vipname], \
                       rules = lsrules)
               except Exception, e:
                   print e
               y['rule_name'] = viprule
               try:
                   obj.LocalLB.VirtualServer.add_rule(virtual_servers = [vipname], \
                       rules = lsrules)
               except Exception, e:
                   print e
    return  None   

def add_vip_irule(obj, vipname, viprule):
    '''
This function adds a new iRule to an existing virtual server
obj = BIGIP connection instance
vipname = virtual server name, e.g. VS-10.0.209.2-80
viprule = Name of modified iRule to replace the existing iRule,e.g. Redirect_VS-10.0.209.6-80_v1.0
    '''
    count = 0
    check_priority = []
    rules = obj.LocalLB.VirtualServer.get_rule(virtual_servers = [vipname])
    if rules != [[]]:
        for rule in rules[count]:
            check_priority.append(rule['priority'])
            count += 1
            try:
                obj.LocalLB.VirtualServer.add_rule(virtual_servers = [vipname], \
                    rules = [[{'rule_name': viprule, 'priority': (max(check_priority) + 1)}]])
            except Exception, e:
                print e
    else:
        try:
            obj.LocalLB.VirtualServer.add_rule(virtual_servers = [vipname], \
                rules = [[{'rule_name': viprule, 'priority': 0}]])
        except Exception, e:
            print e
    return None

def modify_pool(obj, plname, plmem, plminmem):
    '''
This function adds/remove pool members fro exisitng pool based on the mode value in the 
variable file.
obj = BIGIP connection instance
plname = pool name
plmem = list of pool members
plminmem = Minimum number of pool members in a priority group before switching to next priority group
    '''
    pool = '/Common/%s' % plname
    pmadd = []
    pmdel = []
    prio = []
# The loop below creates lists of pool members and pool priorities
    for m in plmem:
        pm = {}
        pm['address'] = '/Common/%s' % m['address']
        pm['port'] = m['port']
        if m['mode'] == "add":
            pmadd.append(pm)
        else:
            pmdel.append(pm)
        prio.append(m['priority'])
    try:
        getpools = obj.LocalLB.Pool.get_list()
        if pool in getpools and pmadd != []:
            obj.LocalLB.Pool.add_member_v2(pool_names = [pool], members = [pmadd])
        if pool in getpools and pmdel != []:
            obj.LocalLB.Pool.remove_member_v2(pool_names = [pool], members = [pmdel])
        if plminmem != 0:
            obj.LocalLB.Pool.set_minimum_active_member(pool_names = [pool], values = [plminmem])
            obj.LocalLB.Pool.set_member_priority(pool_names = [pool], members = [pmadd], priorities = [prio])
        return None
    except Exception, e:
        print e

def generate_csr(obj, c_email, c_cn, c_ctry, c_st, c_loc, c_org, c_ou, c_san, ver):
    '''
This function generates a 2048-bit public key and a CSR that can be used for certificate signing
request generation from a CA. This function does not include SAN which uses a different set of 
API and can only work for v12 F5 devices.
    '''
    subject = {}
    subject['common_name'] = c_cn
    subject['country_name'] = c_ctry
    subject['state_name'] = c_st
    subject['locality_name'] = c_loc
    subject['organization_name'] = c_org
    subject['division_name'] = c_ou

# Generate key below; do not create CSR here so we can add email address in the API call below
    try:
        obj.Management.KeyCertificate.key_generate_v2(mode = 'MANAGEMENT_MODE_DEFAULT', \
            keys = [{'id': c_cn,'key_type': 'KTYPE_RSA_PUBLIC', 'bit_length': 2048, \
            'security': 'STYPE_NORMAL','curve_name': 'ELLIPTIC_CURVE_NONE'}], \
            x509_data = [subject], create_optional_cert_csr = False, overwrite = False) 
    except Exception, e:
        print e

# Generate CSR below
    try:
        if 'v12' in ver and c_san != []:
            obj.Management.KeyCertificate.certificate_request_generate_with_extensions( \
                mode = 'MANAGEMENT_MODE_DEFAULT', \
                csrs = [{'id': c_cn, 'email': c_email, 'challenge_password': None}], \
                x509_data = [subject], \
                extensions = [c_san], overwrite = False)
        elif 'v10' in ver or 'v11' in ver or ('v12' in ver and c_san == []):
            obj.Management.KeyCertificate.certificate_request_generate(mode = 'MANAGEMENT_MODE_DEFAULT', \
                csrs = [{'id': c_cn, 'email': c_email, 'challenge_password': None}], \
                x509_data = [subject], overwrite = False)
    except Exception, e:
        print e
# Export CSR file to /shared/tmp directory on device        
    try:
        obj.Management.KeyCertificate.certificate_request_export_to_file(mode = 'MANAGEMENT_MODE_DEFAULT', \
            csr_ids = [c_cn], file_names = ['/shared/tmp/' + c_cn + '.csr'], overwrite = False)
    except Exception, e:
        print e
    csr_location = '/shared/tmp/' + c_cn + '.csr'    
    return csr_location

def config_sync(obj):
    '''
This function will synchronize device ocnfiguration between redundant pair of F5 devices.
    '''
    rd = obj.System.Failover.is_redundant()
    if rd:
        fs = obj.System.Failover.get_failover_state()
    else:
        return None
    if fs == "FAILOVER_STATE_ACTIVE":
        dl = obj.Management.DeviceGroup.get_list()
        dt = obj.Management.DeviceGroup.get_type(device_groups = dl)
# Determine local device name and sync device group        
        for x in zip(dl, dt):
            if x[1] == "DGT_FAILOVER":
                device_grp = x[0]
                local_dev = obj.Management.Device.get_local_device()
                try:
                    obj.System.ConfigSync.synchronize_to_group_v2(group = device_grp, \
                        device = local_dev, force = True)
                except Exception, e:
                    return None

def save_config(obj, savefile, saveflag):
    '''    
This function saves the current configuration changes on the F5. Save configuration filename 
supplied will be ignored due to save_flag of SAVE_HIGH_LEVEL_CONFIG
See F5 API Reference for detail
    '''
    try:
        obj.System.ConfigSync.save_configuration(filename = savefile, save_flag = saveflag)
        return None
    except Exception, e:
        print e

def file_download(obj,src_file,dst_file,chunk_size,buff = 1048576):
    '''
This function will download a file from the F5 to the Ansible host that made the request.
This function is courtesy of Eric Flores from F5.
obj = BIGIP connection instance
src_file = location of file to be downloaded from F5
dst_file = location of file on local server
chunk_size = download size for each chunk
buff(optional) = sieze of file write buffer; default sieze is 1MB
    '''
# Set begining vars
    foffset = 0
    timeout_error = 0
    fbytes = 0
                  
# Open temp file for writing, default buffer size is 1MB
    f_dst = open(dst_file + '.tmp','w',buff)
                          
    while True:
        try:
            chunk = obj.System.ConfigSync.download_file(file_name = src_file, \
                        chunk_size = chunk_size, \
                        file_offset = foffset)
        except:
            timeout_error += 1
            # Is this the 3rd connection attempt?
            if (timeout_error >= 3):
                # Close tmp file & delete, raise error
                f_dst.close()
                os.remove(dst_file + '.tmp')
                raise
            else:
                # Otherwise wait 2 seconds before retry
                time.sleep(2)
                continue
        # Reset error counter after a good connect
        timeout_error = 0
        # Write contents to file
        fchunk = b64decode(chunk['return']['file_data'])
        f_dst.write(fchunk)
        fbytes += sys.getsizeof(fchunk) - 40
                                   
        # Check to see if chunk is end of file
        fprogress = chunk['return']['chain_type']
        if (fprogress == 'FILE_FIRST_AND_LAST')  or (fprogress == 'FILE_LAST' ):
        # Close file, rename from name.tmp to name
            f_dst.close()
            os.rename(dst_file + '.tmp' , dst_file)
            return fbytes
        # set new file offset
        foffset = chunk['file_offset']
