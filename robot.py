#!/usr/bin/env python3

import wpilib
import math

TRIGGER =    1  #Trigger button number
THUMB =      2  #Thumb button number
RAMP_RAISE = 5  #Button for raising ramp
RAMP_LOWER = 3  #Buttom to lower ramp
UNJAM =      11 #Button to run unjam command

DEADZONE_RADIUS = 0.05 # Deadzone Radius prevents tiny twitches in the joystick's value from
					   # affecting the robot.  Use this for cleaning up drive train and shooter.
					   # Also used for detecting changes in an axis' value.

TURN_FACTOR = 1.5      # Left(x,y)  = y*(1 + TF*x)  :  x < 0
					   #	= y 			  :  x >= 0
					   # Right(x,y) = y			  :  x < 0
					   #    = y*(1 - TF*x)  :  x >= 0

class Robot(wpilib.IterativeRobot):
	def robotInit(self):
		"""
        This function is called upon program startup and
        should be used for any initialization code.
        """
        #shooter1.Enable()
        #shooter2.Enable()
        left_drive.SetInverted(true)
        right_drive.SetInverted(true)

        inverting = false
        pickupRunning = false
        ramping = false
        shooting = false
        unjamming = false
        arming = false
        shooter_power = 0
        arcade = false

    #Robotpy docs said these instances need to be after robotInit()
    left_drive = wpilib.TalonSRX(0)
	right_drive = wpilib.TalonSRX(1)
	shooter1 = wpilib.CANTalon(11)
	shooter2 = wpilib.CANTalon(10)
	ramp = wpilib.CANTalon(12)
	arms = wpilib.CANTalon(13)
	drive = wpilib.RobotDrive(left_drive, right_drive)
	# shooter = Shooter(shooter1, shooter2, ramp) #Must add shooter class
	driver_stick = wpilib.Joystick(0)
	operator_stick = wpilib.Joystick(1)
    def autonomousInit(self):
    	"""This function is run once each time the robot enters autonomous mode."""
    def autonomousPeriodic(self):
    	"""This function is called periodically during autonomous."""
    def teleopPeriodic(self):
    	"""This function is called periodically during operator control."""
    	drive.ArcadeDrive(-driver_stick.GetY(), -driver_stick.GetX()*0.75)
    	if(driver_stick.GetRawButton(7))
    		arcade = true
    	if(driver_stick.GetRawButton(8))
    		arcade = false
    	if (arcade)
    		drive.ArcadeDrive(driver_stick)
    	else
    		if(driver_stick.GetRawButton(THUMB))
    			left = driver_stick.GetTwist()
    			right = -driver_stick.GetTwist()
    			drive.TankDrive(left, right)
    		else
    			wpilib.UpdateDrive()
    	#ARMS & Shooter I ignored for now
	def SaneThrottle(rawThrottle):
		return ((1.0 - rawThrottle) / 2.0)
    def testPeriodic(self):
    	"""This function is called periodically during test mode."""
    	#live window
    def SimpleDrive()
    	x = -driver_stick.getX()
    	y = -driver_stick.getY()
    	left = 0
    	right = 0

    	if (x > 0)
    		right = y
    		left = (1 - x * TURN_FACTOR) * y
    	else
    		left = y
    		right = (1 + x * TURN_FACTOR) * y

    	drive.TankDrive(left, right)
    def UpdateDrive
    	x = -driver_stick.GetX()
    	y = -driver_stick.GetY()
    	if (x > 0)
    		right = y * SaneThrottle(driver_stick.GetThrottle())
    		left = (1 - x) * y * SaneThrottle(driver_stick.GetThrottle())
    		drive.TankDrive(left, right)
    	else
    		left = y * SaneThrottle(driver_stick.GetThrottle())
    		right = (1 + x) * y * SaneThrottle(driver_stick.GetThrottle())
    		drive.TankDrive(left, right)
if __name__ == "__main__":
    wpilib.run(Robot)