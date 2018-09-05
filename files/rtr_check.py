# Author: A. Pineda
# Test to Cisco IOS
#!/usr/bin/python
import sys
import getpass
from netmiko import ConnectHandler
print "Enter enable password below"
pw = getpass.getpass()
with open("routerip.txt") as rtr:
    for line in rtr:
       m_ip = line.strip()
       device = {
          'device_type':'cisco_ios',
          'ip':m_ip,
          'username':'admin',
          'password':'admin',
          'secret':pw
       }
       try:
          rtr_conn = ConnectHandler(**device)
          rtr_conn.enable()
          out = rtr_conn.send_command("show int fa1")
          out = out.split('\n')
          for line in out:
              if 'FastEthernet1' in line:
                  print "Interface status for FE1 on %s: %s" % (m_ip, line) 
       except Exception as e:
          print "SSH not enabled on this device IP %s" % m_ip
          sys.exit()
