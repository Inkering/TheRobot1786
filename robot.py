#!/usr/bin/env python3
"""
	This is a good foundation to build your robot code on
"""

import wpilib
import math

TRIGGER = 1
THUMB = 2
RAMP_RAISE = 5
RAMP_LOWER = 3
UNJAM = 11
DEADZONE_RADIUS = 0.05
TURN_FACTOR = 1.5

class MyRobot(wpilib.IterativeRobot):

	def robotInit(self):
		"""
		This function is called upon program startup and
		should be used for any initialization code.
		"""
		self.left_drive = wpilib.TalonSRX(0)
		self.right_drive = wpilib.TalonSRX(1)
		self.shooter1 = wpilib.CANTalon(11)
		self.shooter2 = wpilib.CANTalon(10)
		self.ramp = wpilib.CANTalon(12)
		self.arms = wpilib.CANTalon(13)
		self.drive = wpilib.RobotDrive(self.left_drive,self.right_drive)
		#Shooter object
		self.driver_stick = wpilib.Joystick(0)
		self.operator_stick = wpilib.Joystick(1)
		self.left_drive.setInverted(True)
		self.right_drive.setInverted(True)

		global inverting
		inverting = False
		pickupRunning = False
		ramping = False
		shooting = False
		unjamming = False
		arming = False
		shooterPower = 0
		global arcade
		arcade = False
	def autonomousInit(self):
		"""This function is run once each time the robot enters autonomous mode."""
		self.auto_loop_counter = 0

	def autonomousPeriodic(self):
		"""This function is called periodically during autonomous."""

		# Check if we've completed 100 loops (approximately 2 seconds)
		if self.auto_loop_counter < 100:
			self.drive.drive(-0.5, 0) # Drive forwards at half speed
			self.auto_loop_counter += 1
		else:
			self.drive.drive(0, 0)    #Stop robot

	def saneThrottle(rawThrottle):
		return ((1.0 - rawThrottle) / 2.0)

	def updateDrive():
		x = -self.driver_stick.getX()
		y = -self.driver_stick.getY()
		if (x > 0):
			left = y * saneThrottle(driver_stick.getThrottle())
			right = (1 + x) * y * saneThrottle(driver_stick.getThrottle())
			drive.tankDrive(left, right)

	def teleopPeriodic(self):
		"""This function is called periodically during operator control."""
		self.drive.arcadeDrive(self.driver_stick)
		if(self.driver_stick.getRawButton(7)):
			global arcade
			arcade = True
		if(self.driver_stick.getRawButton(8)):
			global arcade
			arcade = False
		if(arcade):
			self.drive.arcadeDrive(self.driver_stick)
		else:
			if(self.driver_stick.getRawButton(THUMB)):
				left = self.driver_stick.getTwist()
				right = -self.driver_stick.getTwist()
				self.drive.tankDrive(left, right)
			else:
				self.updateDrive
		if(self.driver_stick.getRawButton(TRIGGER)) and not inverting:
			self.left_drive.setInverted(not self.left_drive.getInverted)
			self.right_drive.setInverted(not self.right_drive.getInverted)
			global inverting
			inverting = True
		elif not self.driver_stick.getRawButton(TRIGGER):
			global inverting
			inverting = False

	def testPeriodic(self):
		"""This function is called periodically during test mode."""
		wpilib.LiveWindow.run()



if __name__ == "__main__":
	wpilib.run(MyRobot)