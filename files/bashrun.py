#!/usr/bin/env python
## Run F5 bash command remotely
## Author: A. Pineda
def runBash(hostname,username,password,shellcmd):
   import requests, urllib3 
   from f5.bigip import ManagementRoot
   # Suppresses HTTPS warnings
   requests.packages.urllib3.disable_warnings()
   urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

   b = ManagementRoot(hostname, username, password)
   rtstat = b.tm.util.bash.exec_cmd('run', utilCmdArgs='-c "'+shellcmd+'"')
   print rtstat.commandResult

def main():
   import argparse, getpass

   parser = argparse.ArgumentParser(description='Run bash command on BIGIP')

   parser.add_argument("host", help='BIG-IP  Management IP', )
   parser.add_argument("username", help='BIG-IP Username', )
   parser.add_argument("shellcmd", help='Command to Run')
   args = vars(parser.parse_args())

   hostname = args['host']
   username = args['username']
   shellcmd = args['shellcmd']
   
   password = getpass.getpass()

   runBash(hostname,username,password,shellcmd)
   
if __name__ == "__main__":
   main()
