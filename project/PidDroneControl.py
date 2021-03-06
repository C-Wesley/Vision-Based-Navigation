"""
Vision Based Navigation Project
Augusta University
3/11/2022

This file contains the PidDroneControl class.
This class uses two PID controllers to determine a control value 
to send to the drone to help it reach a specific position.
One PID controls the x movement (left/right) of the drone.
The second PID controls the y (forward/back) movement of the drone.

PidDroneControl.py
"""

from ids import ID
from simple_pid import PID
import time
import json
from djitellopy import Tello

from point import Point

class PidDroneControl:
    """
    Class that uses simple_pid to generate control values to send to a Tello 
    drone.
    """

    def __init__(self, drone_object:Tello, point:Point, instance_num, kp, ki, kd):
        """
        Sets everything up. Instance_num is vital to ensure proper control.
        This instance number links the drone object/ip with its proper ID. 
        If the wrong instance number is assigned, the controller will be
        getting the position (measured value) from a different drone 
        than it is controlling. 

        :param drone_object: The drone object that this controller with control
        :type drone_object: Tello
        
        :param point: The setpoint of the controlelr
        :type point: point.Point
        
        :param instance_num: The instance number of the drone object that
                             corresponds to the id in the ID.instances list. 
        :type instance_num: int
        """

        self.drone = drone_object
        self.time_limit = 5
        self.d2d_range = 30
        # Set point is relative to the camera pixel.
        self.range = 30
        x_set = point.x
        y_set = point.y
        self.wait_time = 0
        self.new_point = False
        self.pidx= PID(kp, ki, kd, setpoint=x_set, output_limits=(-self.range,self.range))
        self.pidy = PID(kp, ki, kd, setpoint=y_set, output_limits=(-self.range,self.range))
        #self.pidx= PID(0.20, 0.05, 0.05, setpoint=self.x_set, output_limits=(-self.range,self.range))
        #self.pidy = PID(0.20, 0.05, 0.05, setpoint=self.y_set, output_limits=(-self.range,self.range))
        self.f_b_vel = 0
        self.u_d_vel = 0
        self.yaw_vel = 0
        self.l_r_vel = 0

        self.d2d = 0
        self.destination = point

        self.instance_num = instance_num

    def update_velocity(self):
        """
        Method to get get the position of the drone, use it to compute
        the new control value, and update the velocity of the drone accordingly
        """
    
        # Get new control values
        position = ID.instances[self.instance_num].position
        self.l_r_vel = self.pidx(position.x)
        self.f_b_vel = self.pidy(position.y) * -1 # flip the y because it is not normal coordinates due to image processing
        
        
        self.d2d = position.dist(self.destination)
        
        #If the distance is close enough, and the time is under still, hold the drone still
        if self.d2d < self.d2d_range and self.wait_time < self.time_limit:
            #self.drone.send_rc_control(0, 0, self.u_d_vel, self.yaw_vel)
            self.drone.send_rc_control(int(self.l_r_vel), int(self.f_b_vel), self.u_d_vel, self.yaw_vel)
            self.wait_time += 1
            print(self.d2d)
        elif self.wait_time < self.time_limit:
            self.drone.send_rc_control(int(self.l_r_vel), int(self.f_b_vel), self.u_d_vel, self.yaw_vel)
        else:
            self.new_point = True
            
    def update_setpoints(self,setpoint):
        """
        Method used to change the setpoint of the controller. 

        :param setpoint: The desired position to move the drone to
        :type setpoint: point.Point
        """
        # Update the Setpoint and clear the history of the PID.
        self.pidx.setpoint = setpoint.x
        self.pidy.setpoint = setpoint.y
        self.pidx.reset()
        self.pidy.reset()

        self.new_point = False
        self.wait_time = 0
        self.destination = setpoint
    
    def takeoff(self):
        """
        Method to make the drone fly
        """
        self.drone.takeoff()
    
    def land(self):
        """
        Method to land the drone
        """
        self.drone.land()
