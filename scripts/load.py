#!/usr/bin/env python

# args:
#   load.py hrpsys-base/RobotHardware localhost:2810

# rosparams
#   execution_context:
#     type: "PeriodicExecutionContext"
#     rate: 500
#   instance_name: rh
#   config_file: $(find hrpsys_ros_bridge)/models/SampleRobot.conf
#   profiles:
#     <name>: <value>

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
            if len(execution_context["type"].split("/")) > 2:
                ecfile = execution_context["type"].split("/")[1]
                ecname = execution_context["type"].split("/")[2]
            else:
                ecfile = execution_context["type"].split("/")[1]
                ecname = execution_context["type"].split("/")[1]
            ecpath = ""
            for directory, i in zip(pkgconfig.parse(ecpkg)["library_dirs"], list(range(1))): # search only top dir
                if os.path.exists(str(directory)+"/"+ecfile+".so"):
                    ecpath = str(directory)+"/"+ecfile+".so"
            if ecpath == "":
                if os.path.exists(rospkg.RosPack().get_path(ecpkg)+"/lib/"+ecfile+".so"):
                    ecpath = rospkg.RosPack().get_path(ecpkg)+"/lib/"+ecfile+".so"
            if ecpath == "":
                ecpath = ecfile+".so"
            mgr.load_module(ecpath,ecfile+"Init")
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

# profiles
if rospy.has_param("~config_file"):
    #mgr.set_configuration("example."+instance_name+".config_file", args.configfile)
    mgr.set_configuration("example."+modulename+".config_file", rospy.get_param("~config_file"))
if rospy.has_param("~profiles"):
    profiles = rospy.get_param("~profiles")
    for key, value in list(profiles.items()):
        create_args += "&" + key + "=" + str(value)

modulepath = ""
for directory, i in zip(pkgconfig.parse(modulepkg)["library_dirs"], list(range(1))): # search only top dir
    if os.path.exists(str(directory)+"/"+modulename+".so"):
        modulepath = str(directory)+"/"+modulename+".so"
if modulepath == "":
    if os.path.exists(rospkg.RosPack().get_path(modulepkg)+"/lib/"+modulename+".so"):
        modulepath = rospkg.RosPack().get_path(modulepkg)+"/lib/"+modulename+".so"
if modulepath == "":
    modulepath = modulename+".so"
mgr.load_module(modulepath,modulename+"Init")

create_args = modulename+'?instance_name=' + instance_name + create_args

rtc = mgr.create_component(create_args)
if rtc:
    rospy.loginfo(instance_name+" created")
else:
    rospy.logerr(instance_name+" create failed")
