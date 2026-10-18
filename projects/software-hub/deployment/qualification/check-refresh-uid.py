"""Fail before any refresh reservation if the APT sandbox cannot change UID."""
import json
import os

assert os.geteuid()==0, 'The isolated rootfs laboratory requires system root'
os.setegid(65534)
os.seteuid(42)
assert os.geteuid()==42 and os.getegid()==65534
print(json.dumps({'apt_sandbox_uid_probe':'PASS','uid':42,'gid':65534}))
