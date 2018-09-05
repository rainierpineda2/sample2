#!/usr/bin/python
#-*- coding: utf-8 -*-
ANSIBLE_METADATA = {
  'metadata_version': '1.1',
  'status': ['preview'],
  'supported_by': 'community'
}
DOCUMENTATION = '''
---
module: bashrunv2
short_description: Run F5 bash command remotely
version: 1.1
options:
    server:
    description:
      - Management IP or FQDN of remote F5 device
    required: True
	username:
    description:
      - Administrative username on remote F5 device
    required: True
    password:
    description:
      - Administrative password on remote F5 device
	shellcmd:
    description:
      - Bash command to run on remote F5 device
    required: True
notes:
  - Requires the f5-sdk Python package on the host This is as easy as pip
    install f5-sdk
requirements:
  - f5-sdk
author:
  - A. Pineda(apined12@its.jnj.com)
'''

EXAMPLES = '''
- name: Run F5 bash command
  bashrunv2:
    server: "lb.mydomain.com"
    username: "admin" 
    password: "secret"
	shellcmd: "netstat -rn" 
  register: result
- debug: var=result  
'''
import requests, urllib3
from f5.bigip import ManagementRoot

def runBash(server,username,password,shellcmd):
   # Suppresses HTTPS warnings
   requests.packages.urllib3.disable_warnings()
   urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

   b = ManagementRoot(server, username, password)
   rtstat = b.tm.util.bash.exec_cmd('run', utilCmdArgs='-c "'+shellcmd+'"')
   result = rtstat.commandResult
   return result

def main():
   fields = dict(
      server=dict(type='str', required=True),
      username=dict(type='str', required=True),
      password=dict(type='str', required=True, no_log=True),
      shellcmd=dict(type='str', required=True),
   ) 
   module = AnsibleModule(argument_spec=fields)
	
   server = module.params['server']
   username = module.params['username']
   password = module.params['password']
   shellcmd = module.params['shellcmd']
	
   result = runBash(server,username,password,shellcmd)

   module.exit_json(changed=False,output=result)
 
   return

try:
   from ansible.module_utils.basic import *
except ImportError:
   pass       

if __name__ == "__main__":
   main()
