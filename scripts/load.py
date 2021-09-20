#!/usr/bin/env python

# args:
#   load.py hrpsys-base/RobotHardware localhost:2810

# rosparams
#   execution_context:
#     type: "PeriodicExecutionContext"
#     rate: 500
#   instance_name: rh
#   config_file: $(find hrpsys_ros_bridge)/models/SampleRobot.conf


import rospy
rospy.init_node("load",anonymous=True)

import sys
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("module", help="ex <packagename>/<modulename>")
parser.add_argument("manager", help="ex localhost:2810")
args = parser.parse_args(rospy.myargv(argv=sys.argv)[1:])

from omniORB import CORBA
import OpenRTM_aist
import RTM
orb = CORBA.ORB_init(sys.argv, CORBA.ORB_ID)
obj = orb.string_to_object("corbaloc:iiop:"+args.manager+"/manager")
mgr = obj._narrow(RTM.Manager)

create_args = ""

import pkgconfig
import os
import rospkg

# load execution context
if rospy.has_param("~execution_context"):
    execution_context = rospy.get_param("~execution_context")
    if "type" in execution_context:
        if "/" in execution_context["type"]:
            ecpkg = execution_context["type"].split("/")[0]
            ecname = execution_context["type"].split("/")[1]
            if os.path.exists(str(pkgconfig.variables(ecpkg)["prefix"])+"/lib/"+ecname+".so"):
                ecpath = str(pkgconfig.variables(ecpkg)["prefix"])+"/lib/"+ecname+".so"
            elif os.path.exists(rospkg.RosPack().get_path(ecpkg)+"/lib/"+ecname+".so"):
                ecpath = rospkg.RosPack().get_path(ecpkg)+"/lib/"+ecname+".so"
            else:
                ecpath = modulename+".so"
            mgr.load_module(ecpath,ecname+"Init")
        else:
            ecname = execution_context["type"]
        create_args += "&exec_cxt.periodic.type="+ecname
    if "rate" in execution_context:
        create_args += "&exec_cxt.periodic.rate="+str(execution_context["rate"])

# load component
modulepkg = args.module.split("/")[0]
modulename = args.module.split("/")[1]
if rospy.has_param("~instance_name"):
    instance_name = rospy.get_param("~instance_name")
else:
    instance_name = modulename

if rospy.has_param("~config_file"):
    #mgr.set_configuration("example."+instance_name+".config_file", args.configfile)
    mgr.set_configuration("example."+modulename+".config_file", rospy.get_param("~config_file"))

if os.path.exists(str(pkgconfig.variables(modulepkg)["prefix"])+"/lib/"+modulename+".so"):
    modulepath = str(pkgconfig.variables(modulepkg)["prefix"])+"/lib/"+modulename+".so"
elif os.path.exists(rospkg.RosPack().get_path(modulepkg)+"/lib/"+modulename+".so"):
    modulepath = rospkg.RosPack().get_path(modulepkg)+"/lib/"+modulename+".so"
else:
    modulepath = modulename+".so"
mgr.load_module(modulepath,modulename+"Init")

create_args = modulename+'?instance_name=' + instance_name + create_args

rtc = mgr.create_component(create_args)
if rtc:
    rospy.loginfo(instance_name+" created")
else:
    rospy.logerror(instance_name+" create failed")
