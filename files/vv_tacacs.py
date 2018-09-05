#!/usr/bin/python
from Exscript.util.interact import read_login
from Exscript.protocols import SSH2
import sys

if len(sys.argv) != 2:
    print "Usage: vv_tacacs.py {tacacs-server-ip}"
    sys.exit(1)
account = read_login()              
conn = SSH2()  
# Read router IPs from a file called routerip.txt
with open("routerip.txt") as rtr:
    for line in rtr:
       m_ip = line.strip()                    
       conn.connect(m_ip) 
       conn.login(account)  
       conn.execute('terminal length 0')           
       conn.execute('config t')
       conn.execute('no tacacs-server host')
       conn.execute('tacacs-server host ' + sys.argv[1])
       print conn.response
conn.send('exit\r')               
conn.close()  

