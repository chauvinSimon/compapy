- `Co`ntrol with `M`oveIt of `Pa`nda robot in `Py`thon

- :speaking_head: `CoMPaPy` = `[kɔm papi]` :older_man: (:fr:)

- :construction: _work in progress_ :construction_worker:

# `CoMPaPy`

## :eyeglasses: description

**"a simple python interface for basic control of a real [panda robot](https://www.franka.de/)
with [moveit](https://ros-planning.github.io/moveit_tutorials/doc/getting_started/getting_started.html)"**

- using only **official** and **maintained** repos: [`franka_ros`](https://frankaemika.github.io/docs/franka_ros.html)
  and [`MoveIt`](https://ros-planning.github.io/moveit_tutorials/doc/getting_started/getting_started.html)
- two modes: `simulated` and `real` panda
- no `cpp`, just `python`

## :warning: limitations

- rely on `ROS` :confused:
- only tested on the following combination
    - (`ubuntu 20`, `noetic`, `libfranka 0.10.0`, `franka_ros 0.10.1`)
    - _todo: docker_
- require switching to a real-time kernel to control the `real` panda
- require lots of installations
    - _todo: docker_
- only basic actions
    - `move_j`
    - `move_l`
    - `open_gripper`
    - `close_gripper`
    - `rotate_joint`
- may require some parameter tuning
    - e.g. `compute_cartesian_path()` params in `move_l`
- control `panda_link8` instead of the gripper :weary:
    - c.f. [known issues](#thinking-known-issues)
    - _todo: [ros.org/question/334902](https://answers.ros.org/question/334902/moveit-control-gripper-instead-of-panda_link8-eff/)_

## :wrench: installation

note: installing `libfranka` and `franka_ros` with `sudo apt install ros-noetic- ...` is not an option at the time of
  writing: it gives incompatible versions

create a directory for all packages

```
mkdir -p ~/catkin_ws/src
cd ~/catkin_ws/src
```

### :dart: final structure

<details>
  <summary>click to expand</summary>

```
tree ~/catkin_ws/src -d -L 2

.
├── compapy
│     ├── config
│     ├── launch
│     ├── media
│     ├── logs
│     └── scripts
├── franka_ros
│     ├── cmake
│     ├── franka_control
│     ├── franka_description
│     ├── franka_example_controllers
│     ├── franka_gazebo
│     ├── franka_gripper
│     ├── franka_hw
│     ├── franka_msgs
│     ├── franka_ros
│     └── franka_visualization
├── geometric_shapes
│     ├── cmake
│     ├── include
│     ├── src
│     └── test
├── moveit
│     ├── moveit
│     ├── moveit_commander
│     ├── moveit_core
│     ├── moveit_experimental
│     ├── moveit_kinematics
│     ├── moveit_planners
│     ├── moveit_plugins
│     ├── moveit_ros
│     ├── moveit_runtime
│     └── moveit_setup_assistant
├── moveit_msgs
│     ├── action
│     ├── dox
│     ├── msg
│     └── srv
├── moveit_resources
│     ├── dual_panda_moveit_config
│     ├── fanuc_description
│     ├── fanuc_moveit_config
│     ├── moveit_resources
│     ├── panda_description
│     ├── panda_moveit_config
│     ├── pr2_description
│     ├── prbt_ikfast_manipulator_plugin
│     ├── prbt_moveit_config
│     ├── prbt_pg70_support
│     └── prbt_support
├── moveit_tutorials
│     ├── doc
│     ├── _scripts
│     ├── _static
│     └── _themes
├── moveit_visual_tools
│     ├── include
│     ├── launch
│     ├── resources
│     └── src
├── panda_moveit_config
│     ├── config
│     └── launch
├── rviz_visual_tools
│     ├── icons
│     ├── include
│     ├── launch
│     ├── resources
│     ├── src
│     └── tests
├── srdfdom
│     ├── include
│     ├── scripts
│     ├── src
│     └── test
└── ven
    ├── bin
    ├── include
    ├── lib
    ├── lib64 -> lib
    └── share
```

</details>

### :pick: building from source

only tested with these versions ([source](https://frankaemika.github.io/docs/compatibility.html)):

| Robot system version | libfranka version | franka_ros version | Ubuntu / ROS    |
| -------------------- | ----------------- | ------------------ | ----------------|
| > = 5.2.0 (FR3)       | > = 0.10.0         | > = 0.10.0          | 20.04 / noetic  |

#### :mag: `libfranka`

follow [these instructions](https://frankaemika.github.io/docs/installation_linux.html#building-from-source)

#### :package: ROS meta-packages

##### :panda_face: `franka_ros`

follow [these instructions](https://frankaemika.github.io/docs/installation_linux.html#building-the-ros-packages)

- prefer `catkin build` to `catkin_make`

##### :hourglass_flowing_sand: real-time kernel

follow [these instructions](https://frankaemika.github.io/docs/installation_linux.html#setting-up-the-real-time-kernel)

- check with `uname -r`
- note: the real-time kernel seems to be required to use the real robot, but not for `gazebo` / `rviz` simulations

##### :cartwheeling: `moveit_panda_config`

follow [these instructions](https://ros-planning.github.io/moveit_tutorials/doc/getting_started/getting_started.html)

- prefer `~/catkin_ws/src` to `~/ws_moveit/src`

##### :cartwheeling: `compapy`

```
cd ~/catkin_ws/src
git clone https://github.com/chauvinSimon/compapy.git
cd ~/catkin_ws/
catkin build
```

#### :performing_arts: `venv`

```
cd ~/catkin_ws/src
python3 -m venv ven --system-site-packages
source ven/bin/activate
pip install -r requirements.txt
```

#### :pencil2: `source_catkin` alias in `~/.bashrc`

this may be useful

```
alias source_catkin="source ~/catkin_ws/devel/setup.bash; source ~/catkin_ws/src/ven/bin/activate; cd ~/catkin_ws/src"
```

#### :bug: troubleshooting

> "Unable to find either executable 'empy' or Python module 'em'... try installing the package 'python-empy'"

- `(ven) ~/catkin_ws$ catkin build -DPYTHON_EXECUTABLE=/usr/bin/python3 -DPYTHON_INCLUDE_DIR=/usr/include/python3.8`

### :writing_hand: pycharm

follow [this great video](https://www.youtube.com/watch?v=lTew9mbXrAs) (Peter Mitrano)

```
source ~/catkin_ws/src/ven/bin/activate
python -c "import ros; print(ros.__file__)"

# if not using the alias
source ~/catkin_ws/devel/setup.sh
```

find the path to `pycharm.sh` either with `JetBrains ToolBox` or with

```
sudo apt install locate
sudo updatedb
locate pycharm.sh
```

I prefer to run python scripts from `pycharm` :blush:

- `Working directory` is configured to be `~/catkin_ws/src/compapy`
- if you prefer using the terminal, you may need to `export PYTHONPATH=${PYTHONPATH}:${PWD}`
  against `ModuleNotFoundError` and `ModuleNotFoundError`

## :arrow_forward: starting real robot

:warning: keep the emergency button close to you :rescue_worker_helmet:

the first time: follow the [fci](https://frankaemika.github.io/docs/getting_started.html) instructions to configure `fci`

switch on the robot

in [`http://172.16.0.2/desk/`](http://172.16.0.2/desk/)

- release joints
- activate `fci`
- Re-initialize Hand

in a terminal

- `source_catkin` (the alias defined in a previous section)

## :stethoscope: verifications

### :wave: manual control

- move the arm
  - in `programming` mode
  - see [this 30-sec demo](https://youtu.be/hCfn0mzHLyM?t=59)

- open/close the gripper
  - in `programming` mode or `execution` mode
  - see [this 15-sec demo](https://youtu.be/hCfn0mzHLyM?t=220)
  - `FCI` can stay activated but make sure to close `RViz` and stop all `ROS` nodes (otherwise `End Effector: Not Connected`)

<details>
  <summary>:heavy_check_mark: expected result</summary>

![source: Franka Emika](media/manual_move.gif)

![source: Franka Emika](media/manual_gripper.gif)

</details>


### :phone: robot connection

```
ping 172.16.0.2
```

### :video_game: `move group` python Interface

no real robot needed: follow
this [tutorial](https://ros-planning.github.io/moveit_tutorials/doc/move_group_python_interface/move_group_python_interface_tutorial.html#move-group-python-interface)

```
roslaunch panda_moveit_config demo.launch rviz_tutorial:=true
rosrun moveit_tutorials move_group_python_interface_tutorial.py
```

<details>
  <summary>:heavy_check_mark: expected result</summary>

![py_tuto_rviz](media/py_tuto_rviz.gif)

</details>

### :book: `libfranka`

in `execution` mode

```
~/libfranka/build/examples/communication_test 172.16.0.2
```

<details>
  <summary>:heavy_check_mark: expected result</summary>

![libfranka.gif](media/libfranka.gif)

</details>

### :popcorn: `franka_example_controllers`

in `execution` mode

```
roslaunch franka_visualization franka_visualization.launch robot_ip:=172.16.0.2 load_gripper:=true

# move a bit the gripper from its start pose before running this
roslaunch franka_example_controllers move_to_start.launch robot_ip:=172.16.0.2
```

<details>
  <summary>notes</summary>

- the pose defined in [`start_pose.yaml`](https://github.com/frankaemika/franka_ros/blob/develop/franka_control/config/start_pose.yaml) is reached
  - the `max_dq` parameter, in `rad/s`, is [used to control the duration of the move](https://github.com/frankaemika/franka_ros/blob/develop/franka_example_controllers/scripts/move_to_start.py#L33), hence the speed

- `franka_visualization.launch` raises the following, but the command can still be executed
  - > `Robot semantic description not found. Did you forget to define or remap '/robot_description_semantic'?`

</details>

### :tv: `rviz` visualization

in `programming` mode

```
roslaunch franka_visualization franka_visualization.launch robot_ip:=172.16.0.2 load_gripper:=true
```

- move the arm manually (gently press the two buttons on the gripper)
- see the corresponding motion in `rviz`

<details>
  <summary>note</summary>

`franka_visualization.launch` raises the following, but motion in `rviz` can still be seen

> `Robot semantic description not found. Did you forget to define or remap '/robot_description_semantic'?`

</details>

### :computer_mouse: `rviz` control

in `execution` mode

```
roslaunch panda_moveit_config franka_control.launch robot_ip:=172.16.0.2 load_gripper:=true
```

in `rviz`:

- add the `MotionPlanning` plugin
- in `Planning Request`, enable `Query Goal State`
- drag the interactive marker to some the goal state
- click `Plan` and the `Execute`
- try different planning settings (cartesian path, speed, planning pipeline ...)
- try to display and hide the different visualisation tools
- I personally like the `Joints` tab in `MotionPlanning` plugin

### :clamp: gripper

in `execution` mode

run one of

```
roslaunch franka_gripper franka_gripper.launch robot_ip:=172.16.0.2
roslaunch franka_control franka_control.launch robot_ip:=172.16.0.2
roslaunch panda_moveit_config franka_control.launch robot_ip:=172.16.0.2 load_gripper:=true
roslaunch compapy real.launch robot_ip:=172.16.0.2
```

alternatively to the real robot, `gazebo` can be used

```
roslaunch panda_moveit_config demo_gazebo.launch
```



```
# close the gripper
rostopic pub --once /franka_gripper/grasp/goal franka_gripper/GraspActionGoal "goal: { width: 0.022, epsilon:{ inner: 0.005, outer: 0.005 }, speed: 0.1, force: 5.0}"

# open the gripper
rostopic pub --once /franka_gripper/move/goal franka_gripper/MoveActionGoal "goal: { width: 0.08, speed: 0.1 }"
```

<details>
  <summary>:heavy_check_mark: expected result</summary>

![gripper.gif](media/gripper.gif)

</details>

### :mechanical_leg: joints

in `execution` mode

```
roslaunch compapy real.launch robot_ip:=172.16.0.2
```

install and run [`rqt_joint_trajectory_controller`](http://wiki.ros.org/rqt_joint_trajectory_controller)

```
sudo apt install ros-noetic-rqt-joint-trajectory-controller
rosrun rqt_joint_trajectory_controller rqt_joint_trajectory_controller
```

in the two drop down options select `/controller_manager` and `effort_joint_trajectory_contoller` and then press the red button to "enable sending commands to the controller"

use this `rqt` tool:

- in `execution` mode to move each joint individually _(done with gazebo in the next section)_

- in `programming` mode or in a simulation to monitor the value of each joint and the distance to joint limits

<details>
  <summary>:heavy_check_mark: expected result</summary>

![rqt.gif](media/rqt.gif)

</details>

### :performing_arts: gazebo

<details>
  <summary>:plate_with_cutlery: ground_plane</summary>

about `ground_plane`

- the default `world` contains a `ground_plane`
- it acts as an obstacle and prevents the robot from reaching negative `z`
- it is located in `/usr/share/gazebo-11/worlds/empty.world`

![gazebo_ground_plane.gif](media/gazebo_ground_plane.gif)

two solutions
- either ... delete the `ground_plane` in `Models`
- or ... create a `my_empty.world` with just a `sun`, and add the args `world:=[ABSOLUTE_PATH_TO_my_empty.world]` to the `demo_gazebo.launch`

```xml
<?xml version="1.0" ?>
<sdf version="1.5">
    <world name="default">
        <!-- A global light source -->
        <include>
            <uri>model://sun</uri>
        </include>
    </world>
</sdf>
```

</details>

```
roslaunch panda_moveit_config demo_gazebo.launch [world:=/home/simonchauvin/catkin_ws/src/compapy/config/my_empty.world]
```

```
rosrun rqt_joint_trajectory_controller rqt_joint_trajectory_controller
```

<details>
  <summary>:heavy_check_mark: expected result</summary>

![gazebo_rqt.gif](media/gazebo_rqt.gif)

</details>

### :straight_ruler: read cartesian coordinates

run one of

```
roslaunch panda_moveit_config franka_control.launch robot_ip:=172.16.0.2 load_gripper:=true
roslaunch compapy real.launch robot_ip:=172.16.0.2
```

alternatively to the real robot, `gazebo` can be used

```
roslaunch panda_moveit_config demo_gazebo.launch
```

then

- in `rviz` add [`tf`](http://wiki.ros.org/tf) under `Panels`
- under `Frames`, `panda_EE` gives the current transform from the base (`world`) to the end effector
- move the robot
    - either manually in `programming` mode
    - or by commands in `execution` mode
- read the updated transform

alternatively, without `rviz`:

```
rosrun tf tf_echo /panda_link0 /panda_EE
```

<details>
  <summary>:heavy_check_mark: expected result</summary>

![tf.gif](media/tf.gif)

</details>

### :suspension_railway: `CoMPaPy` control

in `execution` mode

```
roslaunch compapy real.launch robot_ip:=172.16.0.2
```

alternatively to the real robot, `gazebo` can be used

```
roslaunch panda_moveit_config demo_gazebo.launch
```

in `pycharm`, with `Working directory` set to `~/catkin_ws/src/compapy`

```
python scripts/tests/test_ref_actions.py
```

<details>
  <summary>:heavy_check_mark: expected result</summary>

| ![unittest_5dof.gif](media/unittests_5dof.gif) | 
|:--:| 
| *unit-test with `5`-dof* |

| ![unittest_7dof.gif](media/unittests_7dof.gif) | 
|:--:| 
| *unit-test with `7`-dof* |

</details>

## :checkered_flag: usage

### :chopsticks: gripper

adjust the parameters for `close_gripper()`, depending on the width of the object to grasp, in [`compapy.yaml`](config/compapy.yaml#L22)

### :evergreen_tree: scene

define obstacles in [`obstacles.json`](config/obstacles.json)

then visualize them with

```
roslaunch compapy sim.launch
```

in `pycharm`, with `Working directory` set to `~/catkin_ws/src/compapy`

```
python scripts/main_load_obstacles.py
```

<details>
  <summary>:heavy_check_mark: expected result</summary>

![obstacles.gif](media/obstacles.gif)

</details>

### :joystick: example

in `execution` mode

```
roslaunch compapy real.launch robot_ip:=172.16.0.2
```

adapt and run [`main_example.py`](scripts/main_example.py)

in `pycharm`, with `Working directory` set to `~/catkin_ws/src/compapy`

```
python scripts/main_example.py
```

#### :bug: troubleshooting

calling a `compapy` function that moves the arm, while in `programming` mode
```
[ INFO] [1674462487.629393072]: ABORTED: CONTROL_FAILED
[ WARN] [1674462487.628997406]: Controller 'position_joint_trajectory_controller' failed with error GOAL_TOLERANCE_VIOLATED: panda_joint1 goal error -0.560709
[ WARN] [1674462487.629082297]: Controller handle position_joint_trajectory_controller reports status ABORTED
ERROR - 2023-01-23 09:28:07,629 - CoMPaPy: failed to execute plan
ERROR - 2023-01-23 09:28:07,629 - CoMPaPy: execution of plan failed
ERROR - 2023-01-23 09:28:08,654 - move_to_start_and_set_limits: move failed: execution of plan failed
```

starting a script to control the amr (e.g. `main_example.py`), while no ROS is running
```
[ERROR] [1673445824.345144228]: [registerPublisher] Failed to contact master at [localhost:11311]. Retrying...
# note: `roslaunch` starts `roscore` (and therefore the term "`ROS` master")
```

running a `.launch` file, while ROS is already running
```
[ WARN] [1674459968.109411334]: Shutdown request received.
[ WARN] [1674459968.110716175]: Reason given for shutdown: [[/robot_state_publisher] Reason: new node registered with same name]
```


### :thinking: known issues

<details>
  <summary>:100: [move_l] cannot compute an entire [plan]</summary>

what can help:

- check this [answer](https://github.com/ros-planning/moveit/issues/3183#issuecomment-1202145379)
    - > "A Cartesian path fraction less than 100% usually means either a **collision** was detected (which seems not to be the case here) or **IK failed**."
- change the `eef_step` and `jump_threshold` params of `compute_cartesian_path()`, e.g. several trials with random
  offsets
    - I observe `fraction` improvements of max. `1%`, i.e. so not very helpful
- add intermediate waypoints to `waypoints` to make sub-paths easier
- change the `orientation` of the `target_pose`
    - I noticed that simple combinations of [straight lines] and [rotation around `z` of the gripper of `rz` deg] fail
      for certain `rz` values
- try `move_j` if this is an option :man_shrugging:

</details>

<details>
  <summary>:woozy_face: the computed [plan] includes strange joint moves</summary>

| ![joints.gif](media/joints.gif) | 
|:--:| 
| *__left__: `joint_1` rotates first `cw` and then `ccw`, causing warnings or errors during the execution of the trajectory. **right**: `joint_1` keeps rotating in only one direction* |

what can help:

- check this [answer](https://www.franka-community.de/t/paths-planned-using-moveit-are-very-strange/2550/2)
- use a different planner in `MoveIt` (usually done with the `pipeline` argument)
- play with the [`jump_threshold`](https://github.com/ros-planning/moveit/issues/773) param
  of `compute_cartesian_path()`
- **reduce the degrees of freedom** (dof) of the panda arm
    - ideally, create a new `move_group` using
      the [`MoveIt setup assistant`](https://ros-planning.github.io/moveit_tutorials/doc/setup_assistant/setup_assistant_tutorial.html)
      where not all joints are used
        - e.g. freeze `joint_3` and `joint_5`
        - _todo: I could not find how to do it_
    - alternatively, but not optimal, drastically reduce the bounds of `joint_3` and `joint_5` in `joint_limits.yaml` (note that [`fr3`](https://github.com/frankaemika/franka_ros/blob/develop/franka_description/robots/fr3/joint_limits.yaml) is more constrained than [`panda`](https://github.com/frankaemika/franka_ros/blob/develop/franka_description/robots/panda/joint_limits.yaml))
        - `moveit` uses the limits defined in [`~/catkin_ws/src/franka_ros/franka_description/robots/panda/joint_limits.yaml`](https://github.com/frankaemika/franka_ros/blob/noetic-devel/franka_description/robots/panda/joint_limits.yaml)
        - :warning: **after adjusting `joint_limits.yaml`, make sure all joints are in their intervals before starting `moveit` in the `execution` mode! Otherwise, the arm can strongly vibrate**
        - in `execution` mode, run `python scripts/move_to_start_and_set_limits.py --dof=5`, which does the following:
          - clear changes in `joint_limits.yaml`, i.e. reset to `7`-dof
          - move the amr to a pose suitable for `5`-dof: `joint_5` = `joint_3` = `0.0`
            - _note: this can also be achieved using [`move_to_start.launch`](https://github.com/chauvinSimon/compapy#popcorn-franka_example_controllers), or even manually:_
              - _in `programming` mode, with `roslaunch compapy real.launch robot_ip:=172.16.0.2`, manually move the amr so that `joint_3` and `joint_5` are at `0` (align the arrows printed on the joints)_
              - _make sure these two joints are at `0` with `rosrun rqt_joint_trajectory_controller rqt_joint_trajectory_controller`_
              - _manually move the other joints roughly to the middle of their ranges_
              - _quit `rviz` and kill `real.launch`_
          - overwrite `joint_limits.yaml` for `5`-dof: reduce the bounds of `joint_3` and `joint_5` to ~`0`

</details>

<details>
  <summary>:game_die:	[compute_cartesian_path] is not deterministic</summary>

using the same configurations and parameters, `compute_cartesian_path()` can return `plan` that differ in size

- despite setting `python` and `numpy` `random.seed()`
- probably a `cpp` seed setting is required instead

</details>

<details>
  <summary>:mechanical_arm: the [compapy.move] functions move the [panda_link8] frame to the passed [target_pose], not [panda_EE] </summary>

| ![panda_axes.png](media/panda_axes.png) | 
|:--:| 
| *`compapy.move` functions move the __`panda_link8` frame__ to the passed `target_pose`, __not `panda_EE`__* |

- an example of frame conversion can be found in [`frame_conversion.py`](scripts/socket_interface/frame_conversion.py)
- I could not find how to directly control `panda_EE` instead

here the measurements used to derive some of the parameters for the conversion:

| ![panda_origins_of_coordinates_systems.png](media/panda_origins_of_coordinates_systems.png) | 
|:--:| 
| *measurements when the fingers are in contact with the ground plane: `panda_EE.z = 8.5mm` and `panda_link8.z = 111.6mm`* |

conclusions from the above measurements:
- the `z` offset between `panda_EE` and `panda_link8` is `~103`mm
- the origin of the `panda_EE` frame is located between the finger pads, at `~8`mm from the tip

| ![panda_origins_ee_on_finger.png](media/panda_origins_ee_on_finger.png) | 
|:--:| 
| *origin of `panda_EE`, at `~8.5`mm from the tip* |

</details>

## :+1: acknowledgements

the following resources helped me understand how to control the robot

- [Panda Programming Guide](https://usermanual.wiki/Document/PandaProgrammingGuide.1809781175/help) (Ahmad Al Attar)
- [`franka_ros_interface`](https://github.com/justagist/franka_ros_interface) (Saif Sidhik)
- [`DE3-Panda-Wall`](https://de3-panda-wall.readthedocs.io/en/latest/index.html) (Keith Li, Daniel Yin, Zachary Yamaoka)
- [`panda-gazebo`](https://rickstaa.dev/panda-gazebo) (Rick Staa)
- [`frankx`](https://github.com/pantor/frankx) (Berscheid)
- [`moveit_python`](https://github.com/mikeferguson/moveit_python) (Michael Ferguson)