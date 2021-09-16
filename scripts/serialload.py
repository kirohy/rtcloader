#!/usr/bin/env python

import rospy
rospy.init_node("serialload",anonymous=True)

import sys
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("manager", help="ex localhost:2810")
parser.add_argument("-managername", default="", help="ex manager_name")
args = parser.parse_args(rospy.myargv(argv=sys.argv)[1:])

from omniORB import CORBA
import OpenRTM_aist
import RTM
orb = CORBA.ORB_init(sys.argv, CORBA.ORB_ID)
obj = orb.string_to_object("corbaloc:iiop:"+args.manager+"/manager")
mgr = obj._narrow(RTM.Manager)

# load components
import pkgconfig
import os
import rospkg
components = rospy.get_param("~components")
rtcs = []
for component in components:
    modulepkg = component["module"].split("/")[0]
    modulename = component["module"].split("/")[1]
    if "name" in component:
        instance_name = component["name"]
    else:
        instance_name = modulename

    if "config_file" in component:
        #mgr.set_configuration("example."+instance_name+".config_file", component["config_file"])
        mgr.set_configuration("example."+modulename+".config_file", component["config_file"])

    if os.path.exists(str(pkgconfig.variables(modulepkg)["prefix"])+"/lib/"+modulename+".so"):
        modulepath = str(pkgconfig.variables(modulepkg)["prefix"])+"/lib/"+modulename+".so"
    elif os.path.exists(rospkg.RosPack().get_path(modulepkg)+"/lib/"+modulename+".so"):
        modulepath = rospkg.RosPack().get_path(modulepkg)+"/lib/"+modulename+".so"
    else:
        modulepath = modulename+".so"
    mgr.load_module(modulepath,modulename+"Init")

    create_args = modulename+'?instance_name=' + instance_name
    if args.managername:
        create_args+="&manager_name="+args.managername
    rtc = mgr.create_component(create_args)
    if rtc:
        rospy.loginfo(instance_name+" created")
        rtcs.append(rtc)
    else:
        rospy.loginfo(instance_name+" create failed")

# serialize components
ec = rtcs[0].get_owned_contexts()[0]
for rtc in rtcs[1:]:
    if not ec._is_equivalent(rtc.get_owned_contexts()[0]):
        rtc.get_owned_contexts()[0].stop()
        ec.add_component(rtc)
