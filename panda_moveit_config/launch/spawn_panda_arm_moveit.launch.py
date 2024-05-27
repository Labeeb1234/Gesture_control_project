import os
import yaml
import xacro
import launch_ros
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.conditions import IfCondition
from ament_index_python import get_package_share_directory
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import TimerAction

def load_file(file_path):
    """Load the contents of a file into a string"""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
        return None


def load_yaml(file_path):
    """Load a yaml file into a dictionary"""
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except EnvironmentError: # parent of IOError, OSError *and* WindowsError where available
        return None
    
def run_xacro(xacro_file):
    """Run xacro and output a file in the same directory with the same name, w/o a .xacro suffix"""
    urdf_file, ext = os.path.splitext(xacro_file)
    if ext != '.xacro':
        raise RuntimeError(f'Input file to xacro must have a .xacro extension, got {xacro_file}')
    os.system(f'xacro {xacro_file} -o {urdf_file}')
    return urdf_file

def generate_launch_description():


    moveit_config_folder_name = get_package_share_directory('panda_moveit_config')
    
    xacro_file = os.path.join(moveit_config_folder_name, 'config/welder.urdf.xacro')
    urdf_file = run_xacro(xacro_file=xacro_file)
    robot_description_arm = load_file(urdf_file)



    srdf_file = os.path.join(moveit_config_folder_name, 'config/welder.srdf')
    kinematics_file = os.path.join(moveit_config_folder_name, 'config/kinematics.yaml')
    ompl_config_file = os.path.join(moveit_config_folder_name, 'config/ompl_planning.yaml')
    moveit_controllers_file = os.path.join(moveit_config_folder_name, 'config/moveit_controllers.yaml')
    # moveit_servo_file = os.path.join(moveit_config_folder_name, "config/ur_servo.yaml")
    ros_controllers_file = os.path.join(moveit_config_folder_name, 'config/ros2_controllers.yaml')

    robot_description_semantic = load_file(srdf_file)
    kinematics_config = load_yaml(kinematics_file)
    ompl_config = load_yaml(ompl_config_file)


    moveit_controllers = {
        'moveit_simple_controller_manager' : load_yaml(moveit_controllers_file),
        'moveit_controller_manager': 'moveit_simple_controller_manager/MoveItSimpleControllerManager'
    }
    trajectory_execution = {
        'moveit_manage_controllers': True,
        'trajectory_execution.allowed_execution_duration_scaling': 1.2,
        'trajectory_execution.allowed_goal_duration_margin': 0.5,
        'trajectory_execution.allowed_start_tolerance': 0.01
    }
    planning_scene_monitor_config = {
        'publish_planning_scene': True,
        'publish_geometry_updates': True,
        'publish_state_updates': True,
        'publish_transforms_updates': True
    }

    # MoveIt node
    move_group_node = Node(
        package='moveit_ros_move_group',
        executable='move_group',
        output='screen',
        parameters=[
            {
                'robot_description': robot_description_arm,
                'robot_description_semantic': robot_description_semantic,
                'robot_description_kinematics': kinematics_config,
                'ompl': ompl_config,
                'planning_pipelines': ['ompl'],
            },
            moveit_controllers,
            trajectory_execution,
            planning_scene_monitor_config,
            {"use_sim_time": True},
        ],
    )


    robot_state_publisher_arm = Node(
        name='robot_state_publisher',
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description_arm}],
    )

    rviz = Node(
        name='rviz',
        package='rviz2',
        executable='rviz2',
        output='screen',
        parameters=[
            {
                'robot_description': robot_description_arm,
                'robot_description_semantic': robot_description_semantic,
                'robot_description_kinematics': kinematics_config,
            }
        ],
    )


    spawn_controllers_manipulator = Node(
            package="controller_manager", 
            executable="spawner",
            name="spawner_mani",
            arguments=['joint_trajectory_controller', '--controller-manager', '/controller_manager'],
    )
    

    spawn_controllers_state = Node(
            package="controller_manager", 
            executable="spawner",
            arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
    )


    return LaunchDescription([
        robot_state_publisher_arm,
        TimerAction(period=1.0, actions=[rviz]),
        TimerAction(period=1.5, actions=[move_group_node]),
        # TimerAction(period=2.0, actions=[spawn_controllers_manipulator]),
        # TimerAction(period=2.5, actions=[spawn_controllers_state]),
        
        ]
    )