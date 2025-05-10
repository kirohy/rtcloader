cmake_minimum_required(VERSION 3.0.2)
project(rtcloader)

find_package(catkin REQUIRED catkin_virtualenv)

catkin_package()

if("$ENV{ROS_DISTRO}" STRLESS "noetic")
  catkin_generate_virtualenv(
    PYTHON_INTERPRETER python2
    )

  catkin_install_python(
    PROGRAMS scripts/load.py scripts/serialize.py
    DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION})

  install(FILES requirements.txt
    DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION})
endif()
