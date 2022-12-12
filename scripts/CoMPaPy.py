#! /usr/bin/env python3
import actionlib
from datetime import datetime
import franka_gripper.msg
import geometry_msgs
from geometry_msgs.msg import Pose
import moveit_msgs.msg
from moveit_msgs.msg import RobotTrajectory
import numpy as np
from pathlib import Path
import random
import rospy
from sensor_msgs.msg import JointState
import time
from typing import Dict, Optional, Tuple

from moveit_tutorials.doc.move_group_python_interface.scripts.move_group_python_interface_tutorial import \
    MoveGroupPythonInterfaceTutorial

from compapy.scripts.utils import setup_logger, read_yaml, json_load, pose_to_list, PlanningRes


class CoMPaPy(MoveGroupPythonInterfaceTutorial):
    def __init__(self, log_file: Optional[Path] = None, save_planning_res: bool = False):
        super(CoMPaPy, self).__init__()

        if log_file is None:
            saving_dir = Path('logs') / str(time.strftime("%Y%m%d_%H%M%S"))
            saving_dir.mkdir(exist_ok=True, parents=True)
            log_file = saving_dir / 'log.log'
        else:
            saving_dir = log_file.parent

        self.planning_res_dir = None
        if save_planning_res:
            self.planning_res_dir = saving_dir / 'planning_res'
            self.planning_res_dir.mkdir(parents=True, exist_ok=True)

        self.logger = setup_logger(self.__class__.__name__, log_file=log_file)

        self.config = read_yaml(Path('config/compapy.yaml'))

        obstacles_file = Path(self.config['obstacles']['config_path'])
        if not obstacles_file.exists():
            raise FileExistsError(f'obstacles_file not found: [{obstacles_file}]\n'
                                  f'did you run from [~/catkin_ws/src/compapy]?')
        obstacles_data = json_load(obstacles_file)
        for obstacle in obstacles_data['obstacles']:
            self._add_scene_element(obstacle)

        self.logger.info('joint bounds:')
        for j_name in self.robot.get_joint_names():
            j = self.robot.get_joint(j_name)
            self.logger.info(f'\t{j_name}: {j.bounds()}')

    def _add_scene_element(self, element: Dict) -> None:
        box_name = element["name"]

        if element["type"] == "static_box":
            box_pose = geometry_msgs.msg.PoseStamped()
            box_pose.pose.position.x = element["x"]
            box_pose.pose.position.y = element["y"]
            box_pose.pose.position.z = element["z"]
            box_pose.header.frame_id = "panda_link0"

            box_size = (
                element["size_x"],
                element["size_y"],
                element["size_z"]
            )
            self.scene.add_box(name=box_name, pose=box_pose, size=box_size)
            # todo: wait_for_state_update

        else:
            raise NotImplementedError(f'cannot deal with element["type"]=[{element["type"]}]')

    def move_j(self, target_pose: geometry_msgs.msg.Pose) -> bool:
        self.move_group.set_pose_target(target_pose)

        # todo: how to set speed?
        #  self.move_group.set_max_velocity_scaling_factor()
        success = self.move_group.go(wait=True)

        self.move_group.stop()  # ensures that there is no residual movement
        self.move_group.clear_pose_targets()

        self._compute_move_error(target_pose=target_pose, move_name='move_j')

        return success

    def plan_move_l(
            self,
            start_pose: geometry_msgs.msg.Pose,
            target_pose: geometry_msgs.msg.Pose,
            resolution_m: Optional[float] = None,
            jump_threshold: Optional[float] = None,
    ) -> Tuple[RobotTrajectory, float]:

        if jump_threshold is None:
            jump_threshold = self.config['move_l']['jump_threshold']

        if resolution_m is None:
            resolution_m = self.config['move_l']['resolution_m']

        distance = np.linalg.norm([
            target_pose.position.x - start_pose.position.x,
            target_pose.position.y - start_pose.position.y,
            target_pose.position.z - start_pose.position.z,
        ])
        self.logger.info(f'want to travel [{distance * 100:.1f} cm]')
        self.logger.info(f'with resolution_m=[{resolution_m:.5f}] and jump_threshold=[{jump_threshold:.3f}]')
        self.logger.info(f'... from start_pose =  {pose_to_list(start_pose)}')
        self.logger.info(f'... to   target_pose = {pose_to_list(target_pose)}')

        # do not add current point to the waypoint list
        #   otherwise: "Trajectory message contains waypoints that are not strictly increasing in time."
        #   `https://answers.ros.org/question/253004/moveit-problem-error-trajectory-message-contains-waypoints-that-are-not-strictly-increasing-in-time/`
        waypoints = [
            target_pose,
        ]

        # todo: add constraints
        #  https://github.com/ros-planning/moveit_tutorials/pull/518/files#diff-77946a0e5e0e873f97288add4d30861477c31fa4528736e414a0903fbaa9c438
        self.move_group.limit_max_cartesian_link_speed(
            speed=self.config['move_l']['speed']
        )

        # takes as input waypoints of end effector poses, and outputs a joint trajectory that visits each pose
        plan, fraction = self.move_group.compute_cartesian_path(
            waypoints=waypoints,

            # configurations are computed for every eef_step meters
            # it should be a step size of at most `eef_step` meters between end effector configurations
            #   of consecutive points in the result trajectory
            # todo: tune it
            #  "The computed trajectory is too short to detect jumps in joint-space Need at least 10 steps,
            #   only got 3. Try a lower max_step."
            eef_step=resolution_m,

            # jump_threshold against joint flips (cannot continue following the waypoints without reorienting the arm)
            # solution: limit the maximum distance ("jump") in joint positions between two consecutive trajectory points
            # todo: see tuning: https://thomasweng.com/moveit_cartesian_jump_threshold/
            # todo: enable jump_threshold (not 0.0), to check for infeasible jumps in joint space
            #  disabling the jump threshold while operating real hardware can cause
            #  large unpredictable motions of redundant joints and could be a safety issue
            jump_threshold=jump_threshold,

            # todo: understand. collision wrt robot or wrt scene-obstacles?
            # avoid_collisions=True

            # todo: add path_constraints?
            # todo: how to check the current joint-bounds written in `joint_limits.yaml`?
        )

        if self.planning_res_dir is not None:
            # save planning results (e.g. to check determinism)
            planning_res = PlanningRes(
                start_pose=start_pose,
                target_pose=target_pose,
                plan=plan,
                fraction=fraction,
            )
            fraction_str = f'{fraction:.0%}'
            curr_time = datetime.now()
            timestamp = curr_time.strftime('%Y%m%d_%H%M%S_%f')
            file_name = f'{timestamp}_cm[{int(distance * 100)}]_f[{fraction_str}].json'
            planning_res.save(saving_path=self.planning_res_dir / file_name)

        return plan, fraction

    def move_l(self, target_pose: geometry_msgs.msg.Pose, n_trials: int = 20) -> bool:
        start_pose = self.move_group.get_current_pose().pose

        resolution_m = self.config['move_l']['resolution_m']
        resolution_m_offset = 0
        jump_threshold = self.config['move_l']['jump_threshold']
        jump_threshold_offset = 0

        plan = None
        for i_trial in range(n_trials):
            if i_trial > 0:
                self.logger.info(f'trial [{i_trial + 1}] / [{n_trials}]')

            # try different values for (resolution_m, jump_threshold) if the first trial failed
            if i_trial > 0:
                resolution_m_offset = random.uniform(-0.002, 0.002)
                jump_threshold_offset = random.uniform(-1.0, 1.0)

            plan, fraction = self.plan_move_l(
                start_pose=start_pose,
                target_pose=target_pose,
                resolution_m=resolution_m + resolution_m_offset,
                jump_threshold=jump_threshold + jump_threshold_offset
            )

            self.logger.info(f'[{fraction:.1%}] = fraction of the path achieved as described by the waypoints')

            if fraction == -1.0:
                self.logger.error('error with compute_cartesian_path')
                # todo: fallback

            else:
                n_points = len(plan.joint_trajectory.points)
                self.logger.info(f'[{n_points}] points (resolution_m = {resolution_m * 100:.1f} cm) -> '
                                 f'path.length at most {n_points * resolution_m * 100:.1f} cm')
                if fraction == 1.0:
                    break
                else:
                    self.logger.error(f'path not complete [{fraction:.1%}]')
                    # todo: fallback

        if plan is None:
            return False

        # we were just planning, not asking move_group to actually move the robot yet

        # display the saved trajectory
        display_trajectory = moveit_msgs.msg.DisplayTrajectory()
        display_trajectory.trajectory_start = self.robot.get_current_state()
        display_trajectory.trajectory.append(plan)
        self.display_trajectory_publisher.publish(display_trajectory)

        success = self.move_group.execute(plan, wait=True)
        # todo: this prints sometimes 'ABORTED: CONTROL_FAILED'

        self._compute_move_error(target_pose=target_pose, move_name='move_l')

        return success

    def _compute_move_error(self, target_pose: geometry_msgs.msg.Pose, move_name: str) -> None:
        current_p = self.get_pose()

        target_pose_position = np.array([target_pose.position.x, target_pose.position.y, target_pose.position.z])
        l8_pose_position = np.array([current_p.position.x, current_p.position.y, current_p.position.z])
        delta_cm = 100 * np.linalg.norm((target_pose_position - l8_pose_position))
        self.logger.info(f'after [{move_name}]: delta = [{delta_cm:0.2f} cm]')

        target_pose_orientation = np.array([
            target_pose.orientation.x,
            target_pose.orientation.y,
            target_pose.orientation.z,
            target_pose.orientation.w,
        ])
        l8_pose_orientation = np.array([
            current_p.orientation.x,
            current_p.orientation.y,
            current_p.orientation.z,
            current_p.orientation.w,
        ])
        delta_q = np.linalg.norm((target_pose_orientation - l8_pose_orientation))
        self.logger.info(f'after [{move_name}]: delta_q = [{delta_q:0.3f}]')

        if delta_cm > 1.0:
            self.logger.error(f'after [{move_name}]: delta_cm = [{delta_cm:.2f} cm] between target and current pose')

        if delta_q > 0.1:
            self.logger.error(f'after [{move_name}]: delta_q = [{delta_q:.3f} cm] between target and current pose')

    def open_gripper(self) -> bool:
        # Initialize actionLib client
        move_client = actionlib.SimpleActionClient('/franka_gripper/move', franka_gripper.msg.MoveAction)
        move_client.wait_for_server()

        # Creates a goal to send to the action server.
        goal = franka_gripper.msg.MoveGoal()
        goal.width = self.config['open_gripper']['width']
        goal.speed = self.config['open_gripper']['speed']

        # Sends the goal to the action server.
        move_client.send_goal(goal)

        # Waits for the server to finish performing the action.
        move_client.wait_for_result()

        # Prints out the result of executing the action
        result = move_client.get_result()
        return result.success

    def close_gripper(self) -> bool:
        # Initialize actionLib client
        grasp_client = actionlib.SimpleActionClient('/franka_gripper/grasp', franka_gripper.msg.GraspAction)
        grasp_client.wait_for_server()

        # Creates a goal to send to the action server.
        goal = franka_gripper.msg.GraspGoal()
        goal.width = self.config['close_gripper']['width']
        goal.epsilon.inner = self.config['close_gripper']['epsilon_inner']
        goal.epsilon.outer = self.config['close_gripper']['epsilon_outer']
        goal.speed = self.config['close_gripper']['speed']
        goal.force = self.config['close_gripper']['force']

        # Sends the goal to the action server.
        grasp_client.send_goal(goal)

        # Waits for the server to finish performing the action.
        grasp_client.wait_for_result()

        # Prints out the result of executing the action
        result = grasp_client.get_result()
        return result.success

    def get_pose(self):
        return self.move_group.get_current_pose().pose

    def get_joints(self):
        return self.move_group.get_current_joint_values()

    def get_gripper_width_mm(self):
        msg = rospy.wait_for_message('/franka_gripper/joint_states', JointState, timeout=5)

        if msg.name != ['panda_finger_joint1', 'panda_finger_joint2']:
            self.logger.error(f'[gripper] msg.name = {msg.name}')

        joint_positions = msg.position
        self.logger.info(f'[gripper] joint_positions = {joint_positions}')

        # as strange as it can be, "width" can be directly derived from the two joint angles
        width_mm = 1000 * sum(joint_positions)

        return width_mm
