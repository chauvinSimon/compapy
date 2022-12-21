"""
a specialization for a particular setting
- orientation of the gripper is of the form [180, 0, rz] (euler.xyz), because:
    - the gripper points downwards, to the floor
    - the gripper only rotates along z

"""
import numpy as np
from pathlib import Path
from scipy.spatial.transform import Rotation
from typing import Optional

import geometry_msgs
from compapy.scripts.utils import wrap_to_pi, wrap_to_pi_over_four
from geometry_msgs.msg import Pose, Quaternion

from compapy.scripts.CoMPaPy import CoMPaPy


class MyCoMPaPy(CoMPaPy):
    def __init__(self, log_file: Optional[Path] = None, save_planning_res: bool = False):
        super(MyCoMPaPy, self).__init__(log_file=log_file, save_planning_res=save_planning_res)

    def set_force_threshold(self):
        # todo
        raise NotImplementedError

    def recover_force_exceeded(self):
        # todo
        raise NotImplementedError

    def process_target(
            self,
            target_pose: geometry_msgs.msg.Pose
    ) -> Optional[geometry_msgs.msg.Pose]:
        target_rz_rad = self.rz_from_q(target_pose.orientation)
        self.logger.info(f'{np.rad2deg(target_rz_rad):.1f} = target_rz')
        if target_rz_rad is None:
            return None

        # conversion between link8 and ee
        target_rz_ee_rad = target_rz_rad + np.deg2rad(45)

        # in my particular setting, plan are successful for rz_ee in [-100°, 100°].
        # also, I can exploit the 90° rotation symmetry of my specific scenario
        # therefore, lets wrap to -45°, 45°
        rz_min_ee_rad = -np.pi / 4
        rz_max_ee_rad = np.pi / 4

        if (target_rz_ee_rad < rz_min_ee_rad) or (target_rz_ee_rad > rz_max_ee_rad):
            self.logger.warning(
                f'target_rz_ee={np.rad2deg(target_rz_ee_rad):.1f} not in '
                f'[{np.rad2deg(rz_min_ee_rad):.0f}, {np.rad2deg(rz_max_ee_rad):.0f}]:')
            rz_ee = wrap_to_pi_over_four(a_rad=target_rz_ee_rad)
            rz_l8 = rz_ee - np.deg2rad(45)
            self.logger.warning(f'setting rz_ee={np.rad2deg(rz_ee):.1f} => rz_l8={np.rad2deg(rz_l8):.1f} deg')
            q = self.q_from_rz(rz_rad=rz_l8)
            target_pose.orientation = q
        return target_pose

    def my_move(
            self,
            target_pose: geometry_msgs.msg.Pose
    ) -> bool:
        target_pose = self.process_target(target_pose=target_pose)
        if target_pose is None:
            return False

        # todo: fallback in case move_l fails
        # todo: recovery from HW error
        success_move = self.move_l(target_pose=target_pose)
        if not success_move:
            self.logger.error(f'move_l failed for processed target = {target_pose}')
        return success_move

    def rz_from_q(self, q: Quaternion) -> Optional[float]:
        """
        expect orientation [180°, 0, rz] (euler) and derive rz
        """
        r = Rotation.from_quat([q.x, q.y, q.z, q.w])
        euler_rad = r.as_euler('xyz')

        euler_ref = [np.pi, 0, 0]
        threshold = np.deg2rad(3)
        if abs(wrap_to_pi(euler_rad[0] - euler_ref[0])) < threshold:
            if abs(wrap_to_pi(euler_rad[1] - euler_ref[1])) < threshold:
                rz = euler_rad[2]
                return rz
        self.logger.error(f"cannot derive rz from [{' '.join([f'{np.rad2deg(e):.1f}' for e in euler_rad])}]")
        return None

    @staticmethod
    def q_from_rz(rz_rad: float) -> Quaternion:
        euler_rad = [np.pi, 0, rz_rad]
        q = Rotation.from_euler(angles=euler_rad, seq='xyz').as_quat()
        return Quaternion(x=q[0], y=q[1], z=q[2], w=q[3])
