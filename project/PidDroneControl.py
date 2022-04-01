from ids import ID
from simple_pid import PID
import time
import json

from point import Point

class PidDroneControl:

    def __init__(self, drone_object, point:Point, instance_num):
        self.drone = drone_object
        # Set point is relative to the camera pixel.
        self.range = 20
        self.x_set = point.x
        self.y_set = point.y
        self.wait_time = 0
        self.new_point = False
        self.pidx= PID(0.20, 0.05, 0.05, setpoint=self.x_set, output_limits=(-self.range,self.range))
        self.pidy = PID(0.20, 0.05, 0.05, setpoint=self.y_set, output_limits=(-self.range,self.range))
        self.f_b_vel = 0
        self.u_d_vel = 0
        self.yaw_vel = 0
        self.l_r_vel = 0

        self.d2d = 0
        self.destination = Point(self.x_set, self.y_set)

        self.instance_num = instance_num

        # self.start_time = time.perf_counter()
        # self.new_time = time.perf_counter()
        # self.time_list = []
        # self.pv_x = []
        # self.pv_y = []

    def update_velocity(self):
        
        # self.time_list.append(self.new_time - self.start_time)
        # self.new_time = time.perf_counter()
        # self.pv_x.append(position.x)
        # self.pv_y.append(position.y)
        
        # Get new control values
        position = ID.instances[self.instance_num].position
        self.l_r_vel = self.pidx(position.x)
        self.f_b_vel = self.pidy(position.y) * -1 # flip the y because it is not normal coordinates due to image processing
        
        
        self.d2d = position.dist(self.destination)
        
        #If the distance is close enough, and the time is under still, hold the drone still
        if self.d2d < 16 and self.wait_time < 500:
            self.drone.send_rc_control(0, 0, self.u_d_vel, self.yaw_vel)
            self.wait_time += 1
        elif self.wait_time < 500:
            self.drone.send_rc_control(int(self.l_r_vel), int(self.f_b_vel), self.u_d_vel, self.yaw_vel)
        else:
            self.new_point = True
            

    def update_setpoints(self,setpoint):

        # Update the Setpoint and clear the history of the PID.
        self.pidx.setpoint = setpoint.x
        self.pidy.setpoint = setpoint.y
        self.pidx.reset()
        self.pidy.reset()

        self.new_point = False
        self.wait_time = 0
        self.destination = setpoint

    # def export_to_json(self):
    #     with open("data_file.json", "w") as write_file:
    #         json.dump(self.time_list,write_file)
    #         json.dump(self.pv_x,write_file)
    #         json.dump(self.pv_y,write_file)
    
