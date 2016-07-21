#!/usr/bin/env python3
import wpilib
import math
import shooter


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
        self.drive = wpilib.RobotDrive(self.left_drive, self.right_drive)
        self.driver_stick = wpilib.Joystick(0)
        self.operator_stick = wpilib.Joystick(1)
        self.left_drive.setInverted(True)
        self.right_drive.setInverted(True)

        self.inverting = False
        self.arcade = False

    def autonomousInit(self):
        """This function is run once each time the robot enters autonomous mode."""
        self.auto_loop_counter = 0

    def autonomousPeriodic(self):
        """This function is called periodically during autonomous."""

        # Check if we've completed 100 loops (approximately 2 seconds)
        if self.auto_loop_counter < 100:
            self.drive.drive(-0.5, 0)  # Drive forwards at half speed
            self.auto_loop_counter += 1
        else:
            self.drive.drive(0, 0)  # Stop robot

    def teleopPeriodic(self):
        """This function is called periodically during operator control."""
        self.drive.arcadeDrive(self.driver_stick)
        # if(self.driver_stick.getRawButton(7)):
        #	arcade = True
        # if(self.driver_stick.getRawButton(8)):
        #	arcade = False
        if (self.arcade):
            self.drive.arcadeDrive(self.driver_stick)
        else:
            if (self.driver_stick.getRawButton(THUMB)):
                left = self.driver_stick.getTwist()
                right = -self.driver_stick.getTwist()
                self.drive.tankDrive(left, right)
            else:
                self.updateDrive()
        if (self.driver_stick.getRawButton(TRIGGER)) and (not self.inverting):
            self.left_drive.setInverted(not self.left_drive.getInverted)
            self.right_drive.setInverted(not self.right_drive.getInverted)
            self.inverting = True
        elif not (self.driver_stick.getRawButton(TRIGGER)):
            self.inverting = False

    def testPeriodic(self):
        """This function is called periodically during test mode."""
        wpilib.LiveWindow.run()

    def saneThrottle(self, rawThrottle):
        return ((1.0 - rawThrottle) / 2.0)

    def updateDrive(self):
        x = -self.driver_stick.getX()
        y = -self.driver_stick.getY()
        if (x > 0):
            left = y * self.saneThrottle(self.driver_stick.getThrottle())
            right = (1 - x) * y * self.saneThrottle(self.driver_stick.getThrottle())
            self.drive.tankDrive(left, right)
        else:
            left = y * self.saneThrottle(self.driver_stick.getThrottle())
            right = (1 + x) * y * self.saneThrottle(self.driver_stick.getThrottle())
            self.drive.tankDrive(left, right)


if __name__ == "__main__":
    wpilib.run(MyRobot)
