#!/usr/bin/env python

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("module", help="ex <packagename>/<modulename>")
parser.add_argument("manager", help="ex localhost:2810")
parser.add_argument("-managername", default="", help="ex manager_name")
parser.add_argument("-configfile", default="", help="ex config_file")
parser.add_argument("-name", default="", help="instance_name")

args = parser.parse_args()

modulepkg = args.module.split("/")[0]
modulename = args.module.split("/")[1]
if args.name:
    instance_name = args.name
else:
    instance_name = modulename

import sys
from omniORB import CORBA
import OpenRTM_aist
import RTM

orb = CORBA.ORB_init(sys.argv, CORBA.ORB_ID)
obj = orb.string_to_object("corbaloc:iiop:"+args.manager+"/manager")
mgr = obj._narrow(RTM.Manager)

if args.configfile:
    mgr.set_configuration("example."+instance_name+".config_file", args.configfile)

import pkgconfig
mgr.load_module(str(pkgconfig.variables(modulepkg)["prefix"])+"/lib/lib"+modulename+".so",modulename+"Init")

create_args = modulename+'?instance_name=' + instance_name
if args.managername:
    create_args+="&manager_name="+args.managername
rtc = mgr.create_component(create_args)
