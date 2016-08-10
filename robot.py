#!/usr/bin/env python3
import wpilib
from networktables import NetworkTable
import math
import shooter
import time
from enum import Enum
from robotpy_ext.common_drivers.navx import AHRS

#Button bindings
TRIGGER = 1
THUMB = 2
RAMP_RAISE = 4
RAMP_LOWER = 3
UNJAM = 11
ROTATE_RESET = 10
ROTATE_0 = 5
ROTATE_90 = 6
ROTATE_180 = 7
ROTATE_NEG90 = 8
STOPPID = 9


class MyRobot(wpilib.IterativeRobot):
    #Tune your PID here! These variables control how "jerky" the rotation buttons are
    kP = 0.03
    kI = 0.00
    kD = 0.00
    kF = 0.00
    kToleranceDegrees = 2.0
    def robotInit(self):
        """
		This function is called upon program startup and
		should be used for any initialization code.
		"""
        #network tables
        self.table = NetworkTable.getTable("SmartDashboard")

        #Define Drivetrain and drive talons
        self.left_drive = wpilib.TalonSRX(0)
        self.right_drive = wpilib.TalonSRX(1)
        self.drive = wpilib.RobotDrive(self.left_drive, self.right_drive)
        self.drive.setExpiration(0.1)

        #Define Shooter talons
        self.shooter1 = wpilib.CANTalon(11)
        self.shooter2 = wpilib.CANTalon(10)
        self.ramp = wpilib.CANTalon(12)
        self.shooter = shooter.shooter(self.shooter1, self.shooter2, self.ramp)

        #Define Joysticks and GamePads
        self.driver_stick = wpilib.Joystick(0)
        self.operator_stick = wpilib.Joystick(1)
        self.game_pad = wpilib.Joystick(2)

        #Initialize Shooter instances
        self.shooter1.enable()
        self.shooter2.enable()

        #inverse the drive train
        self.left_drive.setInverted(True)
        self.right_drive.setInverted(True)

        #Hey look some fun booleans!
        self.inverting = False
        self.pickupRunning = False
        self.ramping = False
        self.shooting = False
        self.unjamming = False
        self.arming = False
        self.shooterPower = 0
        self.arcade = False

        #navx init/PID init
        self.ahrs = AHRS.create_spi()
        self.turnController = wpilib.PIDController(self.kP, self.kI, self.kD, self.kF, self.ahrs, output = self)
        self.turnController.setInputRange(-180.0, 180.0)
        self.turnController.setOutputRange(-1.0, 1.0)
        self.turnController.setAbsoluteTolerance(self.kToleranceDegrees)
        self.turnController.setContinuous(True)


    def autonomousInit(self):
        """This function is run once each time the robot enters autonomous mode."""
        self.auto_loop_counter = 0

    def autonomousPeriodic(self):
        """This function is called periodically during autonomous."""

        # Check if we've completed 100 loops (approximately 2 seconds)
        if self.auto_loop_counter < 100:
            self.drive.drive(-0.01, 0)  # Drive forwards at one hundreth speed
            self.auto_loop_counter += 1
        else:
            self.drive.drive(0, 0)  # Stop robot

    def teleopPeriodic(self):
        #Put data from NAVX on SmartDashboard
        self.table.putBoolean("IMUConnected", self.ahrs.isConnected())
        self.table.putNumber("IMUTotalYaw", self.ahrs.getAngle())
        self.table.putNumber("IMUAccelY", self.ahrs.getWorldLinearAccelY())
        #Put limit switch state on SmartDashboard
        self.table.putBoolean("RampLimitF", not self.ramp.isFwdLimitSwitchClosed())
        self.table.putBoolean("RampLimitR", not self.ramp.isRevLimitSwitchClosed())

        """This function is called periodically during operator control."""
        #Switch between arcade and sorta tank drive
        if(self.driver_stick.getRawButton(7)):
            self.arcade = True
        if(self.driver_stick.getRawButton(8)):
            self.arcade = False
        if (self.arcade):
            self.drive.arcadeDrive(self.driver_stick)
        else:
            #Hold Button for twist
            if (self.driver_stick.getRawButton(THUMB)):
                left = self.driver_stick.getTwist()
                right = -self.driver_stick.getTwist()
                self.drive.tankDrive(left, right)
            else:
                self.updateDrive()
        #Create the dog
        tm = wpilib.Timer()
        tm.start()
        #Make sure that it desires food
        self.drive.setSafetyEnabled(True)
        #NAVX rotation functionality
        if self.driver_stick.getRawButton(STOPPID):
            self.turnController.disable()
        if self.driver_stick.getRawButton(ROTATE_RESET):
           self.ahrs.zeroYaw()
        self.rotateToAngle = False
        if self.driver_stick.getRawButton(ROTATE_0):
            self.turnController.setSetpoint(0.0)
            self.rotateToAngle = True
        elif self.driver_stick.getRawButton(ROTATE_90):
            self.turnController.setSetpoint(90.0)
            self.rotateToAngle = True
        elif self.driver_stick.getRawButton(ROTATE_180):
            self.turnController.setSetpoint(179.9)
            self.rotateToAngle = True
        elif self.driver_stick.getRawButton(ROTATE_NEG90):
            self.turnController.setSetpoint(-90.0)
            self.rotateToAngle = True
        if self.rotateToAngle:
            self.turnController.enable()
            self.currentRotationRate = self.rotateToAngleRate
        else:
            self.turnController.disable()
            self.currentRotationRate = self.driver_stick.getTwist()
        self.drive.arcadeDrive(self.driver_stick.getY(), self.currentRotationRate)

        #Control the ramp
        if (not self.ramping and self.operator_stick.getRawButton(RAMP_RAISE)):
            self.shooter.raiseRamp()
            self.ramping = True
        elif (not self.ramping and self.operator_stick.getRawButton(RAMP_LOWER)):
            self.shooter.lowerRamp()
            self.rampign = True
        elif (self.ramping and not self.operator_stick.getRawButton(RAMP_LOWER) and not self.operator_stick.getRawButton(RAMP_RAISE)):
            self.shooter.stopRamp()
            self.ramping = False
        #Run all the rollers to eject the ball
        if (not self.unjamming and self.operator_stick.getRawButton(UNJAM)):
            self.unjamming = True
            self.shooter.unJam()
        elif (not self.unjamming and self.operator_stick.getRawButton(TRIGGER)):
            self.shooter.shootLow()
            self.unjamming = True
        elif (self.unjamming and not self.operator_stick.getRawButton(UNJAM) and not self.operator_stick.getRawButton(TRIGGER)):
            self.shooter.pickUp(False)
            self.unjamming = False
        #comment here
        if(self.operator_stick.getRawButton(THUMB) and not self.pickupRunning):
            self.shooter.pickUp(True)
            self.pickupRunning = True
        elif (not self.operator_stick.getRawButton(THUMB) and self.pickupRunning):
            self.shooter.pickUp(False)
            self.pickupRunning = False
        if (self.driver_stick.getRawButton(TRIGGER) and not self.inverting):
            print("re-re-inverting")
            self.left_drive.setInverted(not self.left_drive.getInverted())
            self.right_drive.setInverted(not self.right_drive.getInverted())
            self.inverting = True
        elif not (self.driver_stick.getRawButton(TRIGGER)):
            self.inverting = False

        self.opThrottle = self.saneThrottle(self.operator_stick.getThrottle())

        if (not self.pickupRunning and not self.unjamming):
            self.shooter.setPower(self.opThrottle)
    def testPeriodic(self):
        """This function is called periodically during test mode."""
        wpilib.LiveWindow.run()
    def saneThrottle(self, rawThrottle):
        #smooth throttle data
        return ((1.0 - rawThrottle) / 2.0)
    def updateDrive(self):
        x = -self.game_pad.getX()
        y = -self.game_pad.getY()
        if (x > 0):
            left = y * self.saneThrottle(self.driver_stick.getThrottle())
            right = (1 - x) * y * self.saneThrottle(self.driver_stick.getThrottle())
            self.drive.tankDrive(left, right)
        else:
            left = y * self.saneThrottle(self.driver_stick.getThrottle())
            right = (1 + x) * y * self.saneThrottle(self.driver_stick.getThrottle())
            self.drive.tankDrive(left, right)
    def pidWrite(self, output):
        self.rotateToAngleRate = output
if __name__ == "__main__":
    wpilib.run(MyRobot)
