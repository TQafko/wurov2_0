#!/usr/bin/env python3

import rospy
from std_msgs.msg import Float64
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Vector3, Twist
from thrusters import Thrusters
import time
import numpy as np
import math

desired_twist = Twist()

def rotate_2d(x,y, angle_rad):
    x_p = x * np.cos(angle_rad) - y * np.sin(angle_rad)
    y_p = x * np.sin(angle_rad) + y * np.cos(angle_rad)
    return x_p , y_p


def callback_navigation(data):
    # Does this once joystick sends data
    left_trigger = (-data.axes[2] + 1) / 2 
    right_trigger = (-data.axes[5] + 1) / 2 
    left_stick_x = data.axes[0]
    left_stick_y = data.axes[1]

    left_stick_x, left_stick_y = rotate_2d(left_stick_x, left_stick_y, -np.pi/2)

    desired_twist.linear.x = left_stick_x
    desired_twist.linear.y = left_stick_y
    desired_twist.linear.z = right_trigger - left_trigger # no press = 1, full press = -1
    # print(f'right_trigger: {data.axes[5]}')
    
    
def callback_angle(data):
    # Does this once Imu data comes in
    # desired_twist.angular.x = data.x # Roll degress
    # desired_twist.angular.y = data.y # pitch degress
    # desired_twist.angular.z = data.z # yaw degress
    pass

    
def thruster_pub():
    global desired_twist
    thrusters = Thrusters()

    print(f'Thrusters started')

    # Initilizes a default ros node 
    rospy.init_node('thrusters', anonymous=True)
    sub = rospy.Subscriber("joy", Joy, callback_navigation) # Gets data from joy msg in float32 array for axes and int32 array for buttons
    sub2 = rospy.Subscriber("orientation", Vector3, callback_angle) # Has data.x as roll = x, pitch = y, yaw = z in degrees
    rate = rospy.Rate(10) # 10hz

    while not rospy.is_shutdown():
        thruster_output = thrusters.set_thrust(desired_twist.linear.x, desired_twist.linear.y, desired_twist.linear.z, 
                             desired_twist.angular.z, desired_twist.angular.y, desired_twist.angular.x)

        print(f'thruster_output: {thruster_output}\n')
        
        rate.sleep()
    
    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    thruster_pub()