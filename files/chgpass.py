#!/usr/bin/python
import pexpect
import time
def ChangePassword(user, newpass):
    passwd = pexpect.spawn("/usr/bin/passwd %s" % user)

    for x in xrange(2):
    # wait for password: to come out of passwd's stdout
        passwd.expect("Password: ")
        # send pass to passwd's stdin
        passwd.sendline(newpass)
        time.sleep(0.1)
ChangePassword('root', 'password123')
