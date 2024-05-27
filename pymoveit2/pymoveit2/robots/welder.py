from typing import List

MOVE_GROUP_ARM: str = "welder_group"
MOVE_GROUP_GRIPPER: str = ""

def joint_names(prefix: str = "") -> List[str]:

    return ["joint_1",
            "joint_2",
            "joint_3",
            "joint_4",
            "joint_5",
            "joint_6",]

def base_link_name(prefix: str = "") -> str:
    return "base_link"


def end_effector_name(prefix: str = "") -> str:
    return ""