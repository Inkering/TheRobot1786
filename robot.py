#!/usr/bin/env python3
import wpilib
import math
import shooter


TRIGGER = 1
THUMB = 2
RAMP_RAISE = 5
RAMP_LOWER = 3
UNJAM = 11

class MyRobot(wpilib.IterativeRobot):
    def robotInit(self):
        """
		This function is called upon program startup and
		should be used for any initialization code.
		"""
        self.left_drive = wpilib.TalonSRX(0)
        self.right_drive = wpilib.TalonSRX(1)
        self.drive = wpilib.RobotDrive(self.left_drive, self.right_drive)

        self.shooter1 = wpilib.CANTalon(11)
        self.shooter2 = wpilib.CANTalon(10)
        self.ramp = wpilib.CANTalon(12)
        self.shooter = shooter.shooter(self.shooter1, self.shooter2, self.ramp)

        self.driver_stick = wpilib.Joystick(0)
        self.operator_stick = wpilib.Joystick(1)

        self.shooter1.enable()
        self.shooter2.enable()

        self.left_drive.setInverted(True)
        self.right_drive.setInverted(True)

        self.inverting = False
        self.pickupRunning = False
        self.ramping = False
        self.shooting = False
        self.unjamming = False
        self.arming = False
        self.shooterPower = 0
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
        #self.drive.arcadeDrive(self.driver_stick)
        self.drive.arcadeDrive(-self.driver_stick.getY(), -self.driver_stick.getX() * 0.75)
        if(self.driver_stick.getRawButton(7)):
            self.arcade = True
        if(self.driver_stick.getRawButton(8)):
            self.arcade = False
        if (self.arcade):
            self.drive.arcadeDrive(self.driver_stick)
        else:
            if (self.driver_stick.getRawButton(THUMB)):
                left = self.driver_stick.getTwist()
                right = -self.driver_stick.getTwist()
                self.drive.tankDrive(left, right)
            else:
                self.updateDrive()
        if (not self.ramping and self.operator_stick.getRawButton(RAMP_RAISE)):
            self.shooter.raiseRamp()
            self.ramping = True
        elif (not self.ramping and self.operator_stick.getRawButton(RAMP_LOWER)):
            self.shooter.lowerRamp()
            self.rampign = True
        elif (self.ramping and not self.operator_stick.getRawButton(RAMP_LOWER) and not self.operator_stick.getRawButton(RAMP_RAISE)):
            self.shooter.stopRamp()
            self.ramping = False
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
            #added True Bool to self.shooter.pickUp(True)
            self.shooter.pickUp(True)
            self.pickupRunning = True
        elif (not self.operator_stick.getRawButton(THUMB) and self.pickupRunning):
            self.shooter.pickUp(False)
            self.pickupRunning = False

        if (self.driver_stick.getRawButton(TRIGGER) and not self.inverting):
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
