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

import pkgconfig
components = rospy.get_param("~components")
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

    mgr.load_module(str(pkgconfig.variables(modulepkg)["prefix"])+"/lib/"+modulename+".so",modulename+"Init")

    create_args = modulename+'?instance_name=' + instance_name
    if args.managername:
        create_args+="&manager_name="+args.managername
    rtc = mgr.create_component(create_args)
    if rtc:
        rospy.loginfo(instance_name+" created")
    else:
        rospy.loginfo(instance_name+" create failed")
