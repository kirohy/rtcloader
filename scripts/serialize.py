#!/usr/bin/env python

# args:
#   serialize.py localhost:2810

# rosparams
#   instance_names: ["rh","seq","sh"]

import rospy
rospy.init_node("load",anonymous=True)

import argparse
import sys
parser = argparse.ArgumentParser()
parser.add_argument("manager", help="ex localhost:2810")
args = parser.parse_args(rospy.myargv(argv=sys.argv)[1:])

import sys
from omniORB import CORBA
import OpenRTM_aist
import RTM
orb = CORBA.ORB_init(sys.argv, CORBA.ORB_ID)
obj = orb.string_to_object("corbaloc:iiop:"+args.manager+"/manager")
mgr = obj._narrow(RTM.Manager)

rtcs = []

# find components
import time
instance_names = rospy.get_param("~instance_names")
for instance_name in instance_names:
    rtc = None
    while not rtc:
        for component in mgr.get_components():
            if component.get_component_profile().instance_name == instance_name:
                rtc = component
        if rtc != None:
            break
        else:
            rospy.logwarn("waiting for "+instance_name)
            time.sleep(1)
    rtcs.append(rtc)

# serialize components
rospy.loginfo("serialize: "+",".join(instance_names))
ec = rtcs[0].get_owned_contexts()[0]
for rtc in rtcs[1:]:
    if not ec._is_equivalent(rtc.get_owned_contexts()[0]):
        rtc.get_owned_contexts()[0].stop()
        rtc.get_owned_contexts()[0].remove_component(rtc)
        ec.add_component(rtc)

for rtc in rtcs:
    ec.activate_component(rtc) # <rtactivate> tag cannot activate because it uses get_owned_context() (not get_participating_context) and ec_id=0 (not 1)
