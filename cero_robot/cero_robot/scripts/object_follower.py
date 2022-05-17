#!/usr/bin/env python 
import rospy 
import numpy as np
import time

from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class ClosestDetectorClass(): 
    def __init__(self): 
        rospy.on_shutdown(self.cleanup) 
	    ############################### PUBLISHERS #####################################
        self.pub_cmdvel = rospy.Publisher("/cmd_vel_auto", Twist, queue_size=1)
        ############################### SUBSCRIBERS ##################################### 
        rospy.Subscriber("base_scan",LaserScan, self.laser_cb) 
        ############ CONSTANTS ################ 
        self.my_twist = Twist()
        self.kp_lin = 0.075
        self.ki_lin = 0.0
        self.kd_lin = 0.05
        self.kp_ang = 1.5
        self.ki_ang = 0.0
        self.kd_ang = 0.2

        self.curr_time = 0	
        self.prev_time = 0

        self.prev_error_lin = 0
        self.error_lin = 0	
        self.cumul_error_lin = 0
        self.rate_error_lin = 0
        self.prev_error_ang = 0
        self.error_ang = 0
        self.cumul_error_ang = 0
        self.rate_error_ang = 0
            #********** INIT NODE **********### 
        r = rospy.Rate(1) #1Hz 
        print("Node initialized 1hz")
        while not rospy.is_shutdown(): 
            print("I am working :)")
            r.sleep() 

    def laser_cb(self, laser_msg): 
    ## THIS FUNCTION RECEIVED A LASER SCAN AND COMPUTES THE ANGLE TO THE CLOSES OBJECT FOUND WITHIN THE LIDAR'S OPERATING RANGE
        self.prev_time = self.curr_time
        self.curr_time = time.time()
        ranges = laser_msg.ranges
        smallest_range = min(ranges)
        if(np.isfinite(smallest_range)):
            smallest_index = ranges.index(smallest_range)
            smallest_angle = laser_msg.angle_min + (laser_msg.angle_increment*smallest_index)
            #print("Smallest Distance [m]: ", smallest_range)
            #print("Smallest Angle [rad]: ", smallest_angle)
            #print("Smallest Angle [deg]: ", smallest_angle*180/3.14159265359)

            self.prev_error_lin = self.error_lin
            self.error_lin = smallest_range
            self.cumul_error_lin += smallest_range*(self.curr_time - self.prev_time)
            self.rate_error_lin = (self.error_lin - self.prev_error_lin) / (self.curr_time - self.prev_time)

            if(smallest_range > 1):
                print("kp lin comp", self.kp_lin*self.error_lin)
                print("ki lin comp", self.ki_lin*self.cumul_error_lin)
                print("kd lin comp", self.kd_lin*self.rate_error_lin)
                self.my_twist.linear.x = self.kp_lin*self.error_lin + self.ki_lin*self.cumul_error_lin + self.kd_lin*self.rate_error_lin
            else:
                self.my_twist.linear.x = 0

            self.prev_error_ang = self.error_ang
            self.error_ang = smallest_angle
            self.cumul_error_ang += smallest_angle*(self.curr_time - self.prev_time)
            self.rate_error_ang = (self.error_ang - self.prev_error_ang) / (self.curr_time - self.prev_time)
      
      
            if(smallest_angle > 0.087 or smallest_angle < -0.087):
                print("kp ang comp", self.kp_ang*self.error_ang)
                print("ki ang comp", self.ki_ang*self.cumul_error_ang)
                print("kd ang comp", self.kd_ang*self.rate_error_ang)
                self.my_twist.angular.z = self.kp_ang*self.error_ang + self.ki_ang*self.cumul_error_ang + self.kd_ang*self.rate_error_ang
            else:
                self.my_twist.angular.z = 0
                
                
            self.myPublish( )
            #self.pub_cmdvel.publish(self.my_twist)
        else:
            self.my_twist.linear.x = 0
            self.my_twist.angular.z = 0
            
            self.myPublish()
            #self.pub_cmdvel.publish(self.my_twist)
            
            
            
            
    def myPublish(self):
        max_linear = 0.7
        max_angular = 1.4
        
        mult_linear  = 1.0
        mult_angular = 1.0
    
        if(self.my_twist.linear.x > max_linear):
            self.my_twist.linear.x = max_linear
            
        if(self.my_twist.angular.z > max_angular):
            self.my_twist.angular.z = max_angular
            
        if(self.my_twist.angular.z < -1*max_angular):
            self.my_twist.angular.z = -1*max_angular
            
        self.pub_cmdvel.publish(self.my_twist)
        
        

    def cleanup(self): 
        #This function is called just before finishing the node 
        # You can use it to clean things up before leaving 
        # Example: stop the robot before finishing a node.   
        self.my_twist = Twist()
        self.pub_cmdvel.publish(self.my_twist)

############################### MAIN PROGRAM #################################### 
if __name__ == "__main__": 
    rospy.init_node("closest_object_detector", anonymous=True) 
    ClosestDetectorClass() 
