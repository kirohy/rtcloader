# rtcloader

## load.py
manager(rtcd)に対し、rtcをロードする.

```xml
<node pkg="rtcloader" type="load.py" name="load" args="hrpsys-base/RobotHardware localhost:2810">
  <rosparam>
    execution_context:
      type: "PeriodicExecutionContext"
      rate: 500
    instance_name: RobotHardware0
    config_file: $(find hrpsys_ros_bridge)/models/SampleRobot.conf
    profiles:
      name1: value1
      name2: value2
  </rosparam>
</node>
```

### 引数
* 第1引数: ロードするモジュール (`パッケージ名/モジュール名`)
* 第2引数: ロードする先のmanagerのポート (`ホスト名:ポート名`)

### parameters
* `execution_context/type`: rtcと一緒にロードするexecution_contextの型()

## serialize.py
rtcのserial executionを可能にする. instance_namesに与えられたrtcを順番に、instance_names[0]のRTCのExecutionContextにattachし、その後activateする. https://github.com/start-jsk/rtmros_common/pull/1112 の問題によってrtmlaunch.pyの`<rtactivate>` tagではrtcをactivateできないので、ここでactivateしている.

```xml
<node name="serialize" pkg="rtcloader" type="serialize.py" output="screen" args="localhost:2810">
  <rosparam>
    instance_names: ["RobotHardware0","seq","sh","kf","rmfo","ast","co","el","log"]
  </rosparam>
</node>
```

### 引数
* 第1引数: master managerのポート (`ホスト名:ポート名`). (この引数、なくてもいいように作り直せる気がする)

### parameters
* `instance_names`: rtcの名前のリスト.
