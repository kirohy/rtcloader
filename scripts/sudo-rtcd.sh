#!/bin/bash
# -*- coding: utf-8 -*-

# roslaunchのlaunch-prefixでsudoを使うと、そのノードはctrl-C時に終了しなくなる. これを、ctrl-C時にちゃんと終了するようにする. sudoのパスワードは不要になっている前提
# ./sudo-rtcd.sh rtcd rtmlaunch hrpsys_tools hrpsys.launch RTCD_LAUNCH_PREFIX:="sudo env -i LANG=C ORBgiopMaxMsgSize=2147483648 PATH=$(env PATH) LD_LIBRARY_PATH=$(env LD_LIBRARY_PATH)
# rtcd is ROS nodename

# sudoのパスワードを不要にする方法
# sudo visudo
# で
# <username> ALL=NOPASSWD: ALL
# を末尾に書く

RTCDNAME=$1
ARGS=${@:2}

function kill_rtcd() {
    echo sending SIGKILL to rtcd...
    ps aux | grep "__name:=$RTCDNAME " | grep -v grep | awk '{ print "kill -9", $2 }' | sudo sh

    #sudo killall rtmlaunch
    return 0
}

trap "echo signal trapped.;kill_rtcd; exit" 1 2 3 15

$ARGS

kill_rtcd
